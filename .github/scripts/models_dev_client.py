import json
import time
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any, Dict, Optional
from provider_meta import get_display_name

SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR.parent.parent
CACHE_PATH = REPO_ROOT / ".github" / "models_dev_cache.json"
MODELS_DEV_API_URL = "https://models.dev/api.json"
CACHE_TTL_SECONDS = 24 * 60 * 60  # 24 hours


def fetch_models_dev_data() -> Optional[Dict[str, Any]]:
    """Fetch https://models.dev/api.json, return parsed dict or None."""
    req = urllib.request.Request(MODELS_DEV_API_URL, method="GET")
    req.add_header("Accept", "application/json")
    req.add_header("User-Agent", "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36")
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            data = json.loads(resp.read().decode())
            if isinstance(data, dict):
                return data
            return None
    except (urllib.error.URLError, urllib.error.HTTPError, json.JSONDecodeError, OSError) as e:
        print(f"  [WARN] Failed to fetch models.dev API: {e}")
        return None


def _load_cache() -> Optional[Dict[str, Any]]:
    """Load cached models.dev data if it exists and is not expired."""
    if not CACHE_PATH.exists():
        return None
    try:
        with open(CACHE_PATH, encoding="utf-8") as f:
            cached = json.load(f)
        if not isinstance(cached, dict):
            return None
        timestamp = cached.get("_cached_at", 0)
        if time.time() - timestamp > CACHE_TTL_SECONDS:
            return None
        return cached.get("data")
    except (json.JSONDecodeError, OSError):
        return None


def _save_cache(data: Dict[str, Any]):
    """Save models.dev data to cache with timestamp."""
    CACHE_PATH.parent.mkdir(parents=True, exist_ok=True)
    cached = {"_cached_at": time.time(), "data": data}
    with open(CACHE_PATH, "w", encoding="utf-8") as f:
        json.dump(cached, f, indent=2, ensure_ascii=False)
    print(f"  [OK] models.dev cache saved to {CACHE_PATH}")


def get_models_dev_data() -> Optional[Dict[str, Any]]:
    """Get models.dev data with caching (TTL 24h)."""
    cached = _load_cache()
    if cached is not None:
        print("  [OK] Using cached models.dev data")
        return cached

    data = fetch_models_dev_data()
    if data is not None:
        _save_cache(data)
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
                "family": family,
                "cost": model_info.get("cost"),
                "limit": model_info.get("limit"),
                "modalities": model_info.get("modalities"),
                "release_date": model_info.get("release_date"),
                "source_provider": provider_id,
                "reasoning": model_info.get("reasoning"),
                "tool_call": model_info.get("tool_call"),
                "attachment": model_info.get("attachment"),
                "temperature": model_info.get("temperature"),
                "open_weights": model_info.get("open_weights"),
            }
    return flat


def get_model_family(flat_index: Dict[str, Dict[str, Any]], model_id: str) -> Optional[str]:
    """Get family for a model from flat index (handles provider-prefixed IDs)."""
    entry = flat_index.get(get_display_name(model_id))
    if entry:
        return entry.get("family")
    return None


def get_model_metadata(flat_index: Dict[str, Dict[str, Any]], model_id: str) -> Optional[Dict[str, Any]]:
    """Get cost, limit, modalities, release_date from flat index (handles provider-prefixed IDs)."""
    entry = flat_index.get(get_display_name(model_id))
    if entry:
        return {
            k: v
            for k, v in entry.items()
            if k not in ("source_provider",)
        }
    return None
