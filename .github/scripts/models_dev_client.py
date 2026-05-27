import json
import time
import httpx
from typing import Any, Dict, Optional, Tuple

from constants import (
    CACHE_TTL_SECONDS,
    MODELS_DEV_CACHE_PATH,
    MODELS_DEV_API_URL,
)
from provider_meta import get_display_name
from rich.console import Console

console = Console()

MODELS_DEV_HEADERS = {
    "Accept": "application/json",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
}

METADATA_FIELDS = (
    "family",
    "cost",
    "limit",
    "modalities",
    "release_date",
    "reasoning",
    "tool_call",
    "attachment",
    "temperature",
    "open_weights",
)


async def fetch_models_dev_data(
    client: Optional[httpx.AsyncClient] = None,
) -> Optional[Dict[str, Any]]:
    """Fetch https://models.dev/api.json, return parsed dict or None."""
    close_client = client is None
    if client is None:
        client = httpx.AsyncClient(timeout=30)

    try:
        resp = await client.get(MODELS_DEV_API_URL, headers=MODELS_DEV_HEADERS, timeout=30)
        resp.raise_for_status()
        data = resp.json()
        if isinstance(data, dict):
            return data
        return None
    except (httpx.RequestError, httpx.HTTPStatusError, json.JSONDecodeError, ValueError) as e:
        console.print(f"  [bold yellow]WARN[/] Failed to fetch models.dev API: {e}")
        return None
    finally:
        if close_client:
            await client.aclose()


def _read_cache_entry() -> Optional[Tuple[Dict[str, Any], bool]]:
    """Read cache and return (data, is_expired) when the cache is usable."""
    if not MODELS_DEV_CACHE_PATH.exists():
        return None
    try:
        with open(MODELS_DEV_CACHE_PATH, encoding="utf-8") as f:
            cached = json.load(f)
        if not isinstance(cached, dict):
            return None
        timestamp = cached.get("_cached_at", 0)
        data = cached.get("data")
        if not isinstance(timestamp, (int, float)) or not isinstance(data, dict):
            return None
        return data, time.time() - timestamp > CACHE_TTL_SECONDS
    except (json.JSONDecodeError, OSError):
        return None


def _load_cache(*, allow_expired: bool = False) -> Optional[Dict[str, Any]]:
    """Load cached models.dev data if it exists and passes the TTL check."""
    entry = _read_cache_entry()
    if entry is None:
        return None

    data, is_expired = entry
    if is_expired and not allow_expired:
        return None
    return data


def _save_cache(data: Dict[str, Any]) -> None:
    """Save models.dev data to cache with timestamp."""
    MODELS_DEV_CACHE_PATH.parent.mkdir(parents=True, exist_ok=True)
    cached = {"_cached_at": time.time(), "data": data}
    with open(MODELS_DEV_CACHE_PATH, "w", encoding="utf-8") as f:
        json.dump(cached, f, indent=2, ensure_ascii=False)
    console.print(f"  [bold green]OK[/] models.dev cache saved to {MODELS_DEV_CACHE_PATH}")


async def get_models_dev_data(
    client: Optional[httpx.AsyncClient] = None,
) -> Optional[Dict[str, Any]]:
    """Get models.dev data with caching (TTL 24h)."""
    cached = _load_cache()
    if cached is not None:
        console.print("  [bold green]OK[/] Using cached models.dev data")
        return cached

    data = await fetch_models_dev_data(client)
    if data is not None:
        _save_cache(data)
        return data

    stale = _load_cache(allow_expired=True)
    if stale is not None:
        console.print("  [bold yellow]WARN[/] Using expired models.dev cache")
        return stale
    return data


def build_flat_index(models_dev_data: Optional[Dict[str, Any]]) -> Dict[str, Dict[str, Any]]:
    """
    Build flat index: normalized_model_id -> {family, cost, limit, modalities, release_date, source_provider}
    From ALL providers in models.dev.
    """
    flat: Dict[str, Dict[str, Any]] = {}
    if not models_dev_data or not isinstance(models_dev_data, dict):
        return flat
    for provider_id, provider_data in models_dev_data.items():
        if provider_id.startswith("_"):
            continue
        if not isinstance(provider_data, dict):
            continue
        models = provider_data.get("models")
        if not isinstance(models, dict):
            continue
        for model_id, model_info in models.items():
            if not isinstance(model_info, dict):
                continue
            norm_id = get_display_name(model_id)
            if norm_id in flat:
                continue
            family = model_info.get("family")
            if not family:
                continue
            flat[norm_id] = {
                key: model_info.get(key)
                for key in METADATA_FIELDS
            }
            flat[norm_id]["source_provider"] = provider_id
    return flat


def get_model_entry(flat_index: Dict[str, Dict[str, Any]], model_id: str) -> Optional[Dict[str, Any]]:
    """Get raw metadata entry from flat index without copying it."""
    return flat_index.get(get_display_name(model_id))


def get_model_family(flat_index: Dict[str, Dict[str, Any]], model_id: str) -> Optional[str]:
    """Get family for a model from flat index (handles provider-prefixed IDs)."""
    entry = get_model_entry(flat_index, model_id)
    if entry:
        return entry.get("family")
    return None


def get_model_metadata(flat_index: Dict[str, Dict[str, Any]], model_id: str) -> Optional[Dict[str, Any]]:
    """Get cost, limit, modalities, release_date, source_provider from flat index."""
    entry = get_model_entry(flat_index, model_id)
    if entry:
        return entry.copy()
    return None
