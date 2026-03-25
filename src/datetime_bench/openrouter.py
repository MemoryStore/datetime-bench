# AI-ANCHOR: datetime-bench: OpenRouter catalog and client
"""OpenRouter catalog lookup, model selection, and completion calls."""

from __future__ import annotations

import asyncio
import os
from dataclasses import asdict
from typing import Any

import httpx

from .config import (
    API_TIMEOUT_SECONDS,
    MAX_COMPLETION_TOKENS,
    MODEL_CELLS,
    NON_REASONING_TEMPERATURE,
    REASONING_TEMPERATURE,
    REQUEST_RETRIES,
    SYSTEM_PROMPT,
)
from .types import PromptCase, SelectedModel

OPENROUTER_MODELS_URL = "https://openrouter.ai/api/v1/models"
OPENROUTER_CHAT_URL = "https://openrouter.ai/api/v1/chat/completions"


class OpenRouterError(RuntimeError):
    """Raised when OpenRouter returns a permanent error."""


class RateLimiter:
    """Simple launch-rate limiter shared by concurrent workers."""

    def __init__(self, min_interval_seconds: float):
        self._min_interval_seconds = min_interval_seconds
        self._next_available = 0.0
        self._lock = asyncio.Lock()

    async def wait(self) -> None:
        loop = asyncio.get_running_loop()
        async with self._lock:
            now = loop.time()
            if now < self._next_available:
                await asyncio.sleep(self._next_available - now)
                now = loop.time()
            self._next_available = now + self._min_interval_seconds


class OpenRouterClient:
    """Thin async wrapper around the OpenRouter chat completions API."""

    def __init__(self, api_key: str | None = None, *, max_tokens: int = MAX_COMPLETION_TOKENS):
        self.api_key = api_key or os.getenv("OPENROUTER_API_KEY")
        if not self.api_key:
            raise RuntimeError("OPENROUTER_API_KEY is required")
        self.max_tokens = max_tokens
        self.catalog: dict[str, dict[str, Any]] = {}
        self._client = httpx.AsyncClient(
            timeout=API_TIMEOUT_SECONDS,
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
                "HTTP-Referer": "https://github.com/julep-ai/mem-mcp-c",
                "X-Title": "datetime-bench",
            },
        )

    async def close(self) -> None:
        await self._client.aclose()

    async def fetch_catalog(self) -> dict[str, dict[str, Any]]:
        response = await self._client.get(OPENROUTER_MODELS_URL, params={"limit": 2000})
        response.raise_for_status()
        payload = response.json()
        self.catalog = {entry["id"]: entry for entry in payload.get("data", [])}
        return self.catalog

    async def select_models(self) -> list[SelectedModel]:
        catalog = await self.fetch_catalog()
        selections: list[SelectedModel] = []
        for cell in MODEL_CELLS:
            selected: SelectedModel | None = None
            notes: list[str] = []
            for candidate in cell.candidates:
                entry = catalog.get(candidate)
                if entry is None:
                    notes.append(f"missing:{candidate}")
                    continue
                pricing = {
                    key: float(value)
                    for key, value in (entry.get("pricing") or {}).items()
                    if value not in (None, "")
                }
                if "prompt" not in pricing or "completion" not in pricing:
                    notes.append(f"missing_pricing:{candidate}")
                    continue
                selected = SelectedModel(
                    cell=cell.cell,
                    label=cell.label,
                    requested_candidates=list(cell.candidates),
                    selected_model=candidate,
                    reasoning_mode=cell.reasoning_mode,
                    size=cell.size,
                    reasoning_config=normalize_reasoning_config(candidate, cell.reasoning_mode, cell.reasoning_config),
                    pricing=pricing,
                    notes=[
                        f"supported_parameters={','.join(entry.get('supported_parameters') or [])}",
                    ],
                )
                if candidate != cell.candidates[0]:
                    selected.notes.append(f"selected_fallback:{candidate}")
                break
            if selected is None:
                selections.append(
                    SelectedModel(
                        cell=cell.cell,
                        label=cell.label,
                        requested_candidates=list(cell.candidates),
                        selected_model=None,
                        reasoning_mode=cell.reasoning_mode,
                        size=cell.size,
                        reasoning_config=cell.reasoning_config,
                        pricing={},
                        notes=notes or ["no_available_model"],
                    )
                )
            else:
                selections.append(selected)
        return selections

    async def complete_case(self, model: SelectedModel, case: PromptCase) -> dict[str, Any]:
        if not model.selected_model:
            raise OpenRouterError(f"No selected model for {model.cell}")
        body = {
            "model": model.selected_model,
            "messages": [
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": case.prompt},
            ],
            "temperature": request_temperature_for_model(model),
            "max_tokens": self.max_tokens,
        }
        if model.reasoning_config is not None:
            body["reasoning"] = model.reasoning_config

        last_error: str | None = None
        for attempt in range(1, REQUEST_RETRIES + 1):
            try:
                response = await self._client.post(OPENROUTER_CHAT_URL, json=body)
            except httpx.TimeoutException as exc:
                last_error = f"timeout:{exc}"
                if attempt == REQUEST_RETRIES:
                    raise
                await asyncio.sleep(2 ** attempt)
                continue
            if response.status_code in {429, 500, 502, 503}:
                retry_after = response.headers.get("Retry-After")
                delay = float(retry_after) if retry_after else float(2**attempt)
                last_error = f"transient_http_{response.status_code}"
                if attempt == REQUEST_RETRIES:
                    response.raise_for_status()
                await asyncio.sleep(delay)
                continue
            if response.status_code in {400, 401, 404}:
                raise OpenRouterError(response.text)
            response.raise_for_status()
            payload = response.json()
            payload["_request_body"] = body
            return payload
        raise OpenRouterError(last_error or "unknown_openrouter_error")

    def build_candidate_selection(
        self,
        base: SelectedModel,
        candidate: str,
    ) -> SelectedModel | None:
        entry = self.catalog.get(candidate)
        if entry is None:
            return None
        pricing = {
            key: float(value)
            for key, value in (entry.get("pricing") or {}).items()
            if value not in (None, "")
        }
        if "prompt" not in pricing or "completion" not in pricing:
            return None
        return SelectedModel(
            cell=base.cell,
            label=base.label,
            requested_candidates=list(base.requested_candidates),
            selected_model=candidate,
            reasoning_mode=base.reasoning_mode,
            size=base.size,
            reasoning_config=normalize_reasoning_config(
                candidate,
                base.reasoning_mode,
                base.reasoning_config,
            ),
            pricing=pricing,
            notes=list(base.notes),
        )


def request_temperature_for_model(model: SelectedModel) -> float:
    return REASONING_TEMPERATURE if model.reasoning_mode == "reasoning" else NON_REASONING_TEMPERATURE


def reasoning_control_mode(model: SelectedModel) -> str:
    if model.reasoning_mode == "reasoning":
        return "explicit_reasoning"
    if model.reasoning_config is None:
        return "omitted_provider_default"
    return "explicit_disabled"


def normalize_reasoning_config(
    model_slug: str,
    reasoning_mode: str,
    requested: dict[str, Any] | None,
) -> dict[str, Any] | None:
    """Build the ``reasoning`` payload for OpenRouter.

    For non-reasoning cells we try ``{"enabled": false}`` first.  The
    probe will catch models that mandate reasoning (400 error) and the
    fallback mechanism will skip them.

    For reasoning cells the visible-token budget must be large enough
    that hidden reasoning doesn't consume the entire ``max_tokens``.
    We don't control ``max_tokens`` here (that's on the client), but
    we ensure the reasoning envelope is correctly shaped per provider.
    """
    if requested is None:
        return None
    if reasoning_mode == "non_reasoning":
        # Some models (gpt-5-mini, gemini-3.1-pro) mandate reasoning
        # and reject {"enabled": false}.  Return None so no reasoning
        # key is sent at all — the model just runs without explicit
        # reasoning control.  If the model forces reasoning anyway, the
        # probe will catch the quality impact.
        return None
    provider = model_slug.split("/", 1)[0]
    if provider == "anthropic":
        budget = int(requested.get("max_tokens", 2048))
        return {"max_tokens": budget, "exclude": True}
    return dict(requested)


def extract_message_content(payload: dict[str, Any]) -> str:
    choices = payload.get("choices") or []
    if not choices:
        return ""
    message = (choices[0] or {}).get("message") or {}
    content = message.get("content")
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        parts: list[str] = []
        for item in content:
            if isinstance(item, dict):
                text = item.get("text") or item.get("content") or ""
                if text:
                    parts.append(str(text))
            elif isinstance(item, str):
                parts.append(item)
        return "\n".join(parts)
    return str(content or "")


def usage_from_payload(payload: dict[str, Any]) -> dict[str, Any]:
    usage = payload.get("usage") or {}
    prompt_details = usage.get("prompt_tokens_details") or {}
    completion_details = usage.get("completion_tokens_details") or {}
    return {
        "prompt_tokens": int(usage.get("prompt_tokens") or 0),
        "completion_tokens": int(usage.get("completion_tokens") or 0),
        "reasoning_tokens": int(completion_details.get("reasoning_tokens") or 0),
        "cached_tokens": int(prompt_details.get("cached_tokens") or 0),
        "cost": float(usage.get("cost") or 0.0),
        "cost_details": usage.get("cost_details") or {},
    }


def estimate_cost(usage: dict[str, Any], pricing: dict[str, float]) -> float:
    if usage.get("cost"):
        return float(usage["cost"])
    cost_details = usage.get("cost_details") or {}
    upstream = float(cost_details.get("upstream_inference_cost") or 0.0)
    if upstream:
        return upstream
    prompt_tokens = int(usage.get("prompt_tokens") or 0)
    completion_tokens = int(usage.get("completion_tokens") or 0)
    reasoning_tokens = int(usage.get("reasoning_tokens") or 0)
    prompt_cost = prompt_tokens * float(pricing.get("prompt", 0.0))
    reasoning_unit = float(pricing.get("internal_reasoning", pricing.get("completion", 0.0)))
    visible_completion = max(0, completion_tokens - reasoning_tokens)
    completion_cost = visible_completion * float(pricing.get("completion", 0.0))
    reasoning_cost = reasoning_tokens * reasoning_unit
    return prompt_cost + completion_cost + reasoning_cost


def serialize_selections(selections: list[SelectedModel]) -> list[dict[str, Any]]:
    return [asdict(selection) for selection in selections]


def deserialize_selections(rows: list[dict[str, Any]]) -> list[SelectedModel]:
    return [SelectedModel(**row) for row in rows]
