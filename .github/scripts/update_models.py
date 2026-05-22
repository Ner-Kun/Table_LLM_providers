import io
import json
import os
import re
import sys
import time

from provider_meta import get_display_name, get_plain_provider_name, get_tier_for_family
from models_dev_client import (
    build_flat_index,
    get_model_metadata,
    get_models_dev_data,
)

# Fix Windows console encoding
stdout = sys.stdout
if isinstance(stdout, io.TextIOWrapper) and hasattr(stdout, "reconfigure"):
    stdout.reconfigure(encoding="utf-8")
elif sys.platform == "win32" and hasattr(stdout, "buffer"):
    sys.stdout = io.TextIOWrapper(stdout.buffer, encoding="utf-8")

import urllib.error  # noqa: E402
import urllib.parse  # noqa: E402
import urllib.request  # noqa: E402
from datetime import datetime, timezone  # noqa: E402
from pathlib import Path  # noqa: E402
from typing import Any, Dict, List, Optional, Tuple  # noqa: E402

SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR.parent.parent
DOCS_DIR = REPO_ROOT / "docs"
CACHE_PATH = DOCS_DIR / "models_data.json"
PROVIDERS_JSON = SCRIPT_DIR / "providers.json"

FAMILY_KEY_OVERRIDES = {
    "gpt-oss-120b": "gpt-oss",
    "gpt-oss-20b": "gpt-oss",
}

# API keys configuration: provider name -> auth settings
# header: HTTP header name (default: "Authorization")
# prefix: prefix before the key value (default: "Bearer", empty string = no prefix)
API_KEYS_CONFIG = {
    "Agent Router": {
        "env": "AGENT_ROUTER_API_KEY",
    },
    "CrowAI": {
        "env": "CROWAI_API_KEY",
    },
    "Google AI Studio": {
        "env": "GOOGLE_AI_STUDIO_API_KEY",
    },
    "Mistral": {
        "env": "MISTRAL_API_KEY",
    },
    "Cerebras": {
        "env": "CEREBRAS_API_KEY",
    },
    "Groq": {
        "env": "GROQ_API_KEY",
    },
}


def load_current_tasks() -> List[Dict[str, Any]]:
    """Load all current tasks from providers.json if it exists and is non-empty."""
    if not PROVIDERS_JSON.exists():
        return []
    try:
        data = json.loads(PROVIDERS_JSON.read_text(encoding="utf-8"))
        if isinstance(data, list) and len(data) > 0:
            return data
        if isinstance(data, dict):
            return [data]
    except (json.JSONDecodeError, OSError):
        pass
    return []


def get_base_url_for_provider(provider_name: str, section: str) -> Optional[str]:
    """Try providers.json first, fall back to parsing .md."""
    tasks = load_current_tasks()
    for task in tasks:
        if task.get("name") == provider_name and task.get("base_url"):
            return task["base_url"].rstrip("/")
    return extract_base_url(section)


def get_auth_headers(provider_name: str) -> Dict[str, str]:
    """Build auth headers for a provider from API_KEYS_CONFIG + environment.

    Returns dict with auth header(s), or empty dict if no key configured.
    """
    plain_name = get_plain_provider_name(provider_name)
    entry = API_KEYS_CONFIG.get(plain_name)
    if not entry or not isinstance(entry, dict):
        return {}

    env_var = entry.get("env")
    if not env_var:
        return {}

    api_key = os.environ.get(env_var, "")
    if not api_key:
        return {}

    header = entry.get("header") or "Authorization"
    prefix = entry.get("prefix")
    if prefix is None:
        prefix = "Bearer"

    value = f"{prefix} {api_key}".strip()
    return {header: value}

# priority config 

PRIORITY = {
    "tier1": {
        "keywords": ["claude", "opus", "sonnet", "haiku"],
        "weight": 100,
    },
    "tier2": {
        "keywords": [
            "deepseek-ai",
            "deepseek",
            "gpt",
            "gemini",
            "glm",
            "mimo",
            "kimi",
            "qwen",
            "minimax",
            "grok",
        ],
        "weight": 80,
    },
    "tier3": {
        "keywords": [
            "gemma",
            "llama",
            "mistral",
            "codestral",
            "devstral",
        ],
        "weight": 60,
    },
    "tier4": {
        "keywords": [
            "command",
            "jamba",
            "mixtral",
            "phi",
            "hermes",
        ],
        "weight": 40,
    },
    "tier5": {
        "keywords": [
            "gpt-oss-120b",
            "gpt-oss-20b",
            "gpt-oss",
            "gpt-4o",
            "gpt-4",
            "embed",
            "instruct",
            "mini",
            "image",
            "nemotron",
            "alpaca",
            "openbuddy",
            "codegemma",
            "codellama",
        ],
        
        "weight": 10,
    },
}

SETTINGS = {
    "timeout_seconds": 15,
    "marker_start": "<!-- MODELS_START -->",
    "marker_end": "<!-- MODELS_END -->",
    "request_delay": 1,
    "skip_files": ["changelog.md", "dangerous.md", "index.md", "index_full.md"],
}

# helpers
def load_cache() -> dict:
    if CACHE_PATH.exists():
        with open(CACHE_PATH, encoding="utf-8") as f:
            return json.load(f)
    return {}


def save_cache(data: dict):
    CACHE_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(CACHE_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    models_count = len(data.get("_models", {}))
    print(f"[OK] Cache saved ({len(data)} providers, {models_count} unique models)")


def read_markdown(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def write_markdown(path: Path, content: str):
    path.write_text(content, encoding="utf-8")


# parse markdown sections
def find_provider_sections(content: str) -> List[Tuple[str, str]]:
    """
    Split markdown into provider sections.
    Returns list of (provider_name, section_content).
    """
    pattern = r"^###\s+(.+)$"
    parts = re.split(pattern, content, flags=re.MULTILINE)

    sections = []
    for i in range(1, len(parts), 2):
        if i < len(parts):
            name = parts[i].strip()
            body = parts[i + 1] if i + 1 < len(parts) else ""
            sections.append((name, body))

    return sections


def extract_base_url(section: str) -> Optional[str]:
    """
    Find Base URL in a provider section.
    """
    matches = re.findall(r"\|\s*`(https?://[^`]+)`\s*\|", section)
    if matches:
        return matches[-1].rstrip("/")
    return None


def has_markers(section: str) -> bool:
    """Check if section contains MODELS_START and MODELS_END markers."""
    return (
        SETTINGS["marker_start"] in section and SETTINGS["marker_end"] in section
    )


# API URLs
FALLBACK_MODELS_PATHS = ["/v1beta/models", "/api/models", "/models"]


def build_models_urls(base_url: str) -> List[str]:
    """
    Build model endpoint URLs to try, ordered by preference.
    Primary: standard /v1/models path.
    Fallbacks: alternative paths from the server root.
    """
    base = base_url.rstrip("/")
    urls: List[str] = []

    if base.endswith("/v1"):
        urls.append(f"{base}/models")
    elif "/v1" in base:
        urls.append(f"{base}/models")
    else:
        urls.append(f"{base}/v1/models")

    parsed = urllib.parse.urlparse(base)
    root = f"{parsed.scheme}://{parsed.netloc}"

    for path in FALLBACK_MODELS_PATHS:
        full = f"{root}{path}"
        if full not in urls:
            urls.append(full)

    return urls


# fetch models
def fetch_models(
    api_urls: List[str],
    headers: Optional[Dict[str, str]] = None,
    timeout: int = 15,
    max_retries: int = 2,
) -> Optional[List[Dict[str, Any]]]:
    """
    Fetch model list from model endpoint URLs, trying each in sequence.
    Falls back to alternative paths if the primary URL fails.
    Returns list of model dicts, or None if all URLs fail.
    """
    for idx, api_url in enumerate(api_urls):
        if idx > 0:
            print(f"  Fallback {idx}: trying {api_url}")

        retries = max_retries if idx == 0 else 0
        for attempt in range(retries + 1):
            try:
                req = urllib.request.Request(api_url, method="GET")
                if headers:
                    for k, v in headers.items():
                        req.add_header(k, v)
                req.add_header("Accept", "application/json")

                with urllib.request.urlopen(req, timeout=timeout) as resp:
                    data = json.loads(resp.read().decode())
                    if isinstance(data, list):
                        return data
                    if isinstance(data, dict) and "data" in data:
                        return data["data"]
                    if isinstance(data, dict) and "models" in data:
                        return data["models"]
                    if idx == 0:
                        print(f"  Unexpected JSON format, trying fallbacks...")
                    else:
                        print(f"  Unexpected JSON format from {api_url}")
                    break
            except (
                urllib.error.URLError,
                urllib.error.HTTPError,
                json.JSONDecodeError,
                OSError,
            ) as e:
                print(f"[WARN] {'Attempt ' + str(attempt + 1) + '/' + str(retries + 1) + ' for ' if retries > 0 else ''}{api_url} failed: {e}")
                if attempt < retries:
                    wait = 2 ** attempt
                    print(f"  Retrying in {wait}s...")
                    time.sleep(wait)
                else:
                    print(f"[ERR] Failed to fetch {api_url}")
    return None


def get_model_tier(model_id: str, display_name: str) -> Tuple[int, str]:
    """
    Determine tier and keyword for a model.

    Checks both full ID and display name (without provider prefix).
    Returns (tier_level, keyword) where:
    - lower tier_level = higher priority (tier 1 is best)
    - keyword is the matching keyword from PRIORITY

    Tier 5 acts as a low-priority exclusion/fallback tier: if a model matches
    any tier5 keyword, it is classified as tier5 even if it also matches a
    higher tier keyword such as "gpt" or "deepseek".
    """
    search_targets = [model_id.lower(), display_name.lower()]

    for kw in PRIORITY["tier5"]["keywords"]:
        for target in search_targets:
            if kw in target:
                family_key = FAMILY_KEY_OVERRIDES.get(kw, kw)
                return (5, family_key or kw)

    for tier_name, tier_config in PRIORITY.items():
        if tier_name == "tier5":
            continue
        for kw in tier_config["keywords"]:
            for target in search_targets:
                if kw in target:
                    family_key = FAMILY_KEY_OVERRIDES.get(kw, kw)
                    return (int(tier_name.replace("tier", "")), family_key or kw)

    return (99, "other")


def resolve_model_family(
    model_id: str,
    display_name: str,
    flat_index: Optional[Dict[str, Dict[str, Any]]],
) -> Tuple[int, str, Optional[Dict[str, Any]]]:
    """
    Determine model family and return metadata.

    Priority:
        1. Flat index from models.dev (if model found)
        2. Current PRIORITY heuristic (fallback)

    Returns:
        (tier_level, family_key, metadata_or_None)
    """
    if flat_index and model_id in flat_index:
        entry = flat_index[model_id]
        family = entry.get("family")
        if family:
            tier = get_tier_for_family(family)
            metadata = get_model_metadata(flat_index, model_id)
            return (tier, family, metadata)
    tier, keyword = get_model_tier(model_id, display_name)
    return (tier, keyword, None)


def build_family_map(
    model_ids: List[str],
    flat_index: Optional[Dict[str, Dict[str, Any]]] = None,
) -> Dict[str, List[str]]:
    """Build a map of family_key -> [model_ids] for all models."""
    families: Dict[str, List[str]] = {}

    for model_id in model_ids:
        display = get_display_name(model_id)
        tier, family_key, _ = resolve_model_family(model_id, display, flat_index)
        family_key = family_key if family_key and tier < 99 else "other"
        if family_key not in families:
            families[family_key] = []
        families[family_key].append(model_id)

    return families


# format output─
def format_models_output(total_count: int, provider_name: str) -> str:
    """
    Format the "+N more models. Show all" line for markdown table cell.
    No bullet points — models are specified manually by the user.
    """
    if total_count <= 0:
        return ""
    return (
        f"+{total_count} more models. "
        f'<a class="models-show-all" data-provider="{provider_name}">Show all</a>'
    )


# inject into markdown
def extract_current_models_text(section: str, start_marker: str, end_marker: str) -> str:
    """Extract current text between markers from markdown section."""
    start_idx = section.find(start_marker)
    end_idx = section.find(end_marker)
    if start_idx == -1 or end_idx == -1 or end_idx <= start_idx:
        return ""
    return section[start_idx + len(start_marker) : end_idx]


def inject_models_into_section(
    section: str, models_text: str, start_marker: str, end_marker: str
) -> str:
    """
    Replace content between markers in a section.
    Uses str.find for reliability (works even with single-line table cells).
    """
    start_idx = section.find(start_marker)
    end_idx = section.find(end_marker)

    if start_idx == -1 or end_idx == -1:
        print(f"[DEBUG] Markers not found: start={start_idx}, end={end_idx}")
        return section

    if end_idx <= start_idx:
        print(f"[DEBUG] Invalid marker order: start={start_idx}, end={end_idx}")
        return section
    before = section[: start_idx + len(start_marker)]
    after = section[end_idx:]
    new_section = f"{before}{models_text}{after}"

    print(f"[DEBUG] Replaced content between markers ({len(section)} -> {len(new_section)} chars)")
    return new_section


# process single provider
def _build_families_structure(
    all_ids: List[str],
    flat_index: Optional[Dict[str, Dict[str, Any]]],
    global_models: Dict[str, Dict[str, Any]],
) -> Dict[str, Dict[str, Any]]:
    """Build families dict with deduplicated model IDs.

    Model metadata is collected into a shared global_models dict
    instead of being duplicated per-provider.
    """
    family_map = build_family_map(all_ids, flat_index)

    families: Dict[str, Dict[str, Any]] = {}
    for fam_key, model_ids in family_map.items():
        for mid in model_ids:
            if flat_index and mid not in global_models:
                meta = get_model_metadata(flat_index, mid)
                if meta:
                    global_models[mid] = meta
        families[fam_key] = {"models": model_ids}

    return families


def count_manual_models(section: str) -> int:
    """Count manually listed models in section (before MODELS_START)."""
    idx = section.find(SETTINGS["marker_start"])
    before = section[:idx] if idx != -1 else section
    return len(re.findall(r'•\s+\S+', before))


def _handle_api_failure(
    plain_name: str, cache: dict, section: str, provider_name: str
) -> Tuple[bool, Optional[str], str]:
    """Try cache fallback on API failure, then check for manual models."""
    cached = cache.get(plain_name)
    if cached and cached.get("models_text"):
        print(f"[WARN] Using cached data from {cached.get('timestamp', 'unknown')}")
        section = inject_models_into_section(
            section, cached["models_text"], SETTINGS["marker_start"], SETTINGS["marker_end"]
        )
        print("[OK] Updated with cached models")
        return True, None, section

    manual_count = count_manual_models(section)
    if manual_count > 0:
        print(f"[INFO] No API /v1/models endpoint for '{provider_name}', "
              f"preserving {manual_count} manually added model(s)")
        return True, None, section

    print(f"[WARN] API unavailable for '{provider_name}' "
          f"and no manually added models found. Section unchanged.")
    return True, None, section


def process_provider(
    provider_name: str,
    section: str,
    cache: dict,
    flat_index: Optional[Dict[str, Dict[str, Any]]] = None,
    global_models: Optional[Dict[str, Dict[str, Any]]] = None,
) -> Tuple[bool, Optional[str], str]:
    """
    Process one provider section.

    Returns (success, error_message, updated_section).
    """
    print(f"\n{'='*50}")
    print(f"Processing: {provider_name}")
    print(f"{'='*50}")

    if not has_markers(section):
        print("[SKIP] No markers found, skipping")
        return True, None, section

    base_url = get_base_url_for_provider(provider_name, section)
    if not base_url:
        msg = f"Could not find Base URL for '{provider_name}'"
        print(f"[ERR] {msg}")
        return False, msg, section

    print(f"Base URL: {base_url}")
    api_urls = build_models_urls(base_url)
    print(f"API URL:  {api_urls[0]}")
    if len(api_urls) > 1:
        print(f"Fallbacks: {', '.join(api_urls[1:])}")

    headers = { "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36" }
    auth = get_auth_headers(provider_name)
    headers.update(auth)
    if auth:
        print(f"[AUTH] Using API key ({list(auth.keys())[0]})")
    else:
        print("[AUTH] No API key, requesting without auth")

    models = fetch_models(api_urls, headers=headers, timeout=SETTINGS["timeout_seconds"])
    plain_name = get_plain_provider_name(provider_name)

    if models is None:
        return _handle_api_failure(plain_name, cache, section, provider_name)

    print(f"Fetched {len(models)} models total")

    if SETTINGS.get("request_delay", 0) > 0:
        time.sleep(SETTINGS["request_delay"])

    all_ids = list(dict.fromkeys(m.get("id", "") for m in models if m.get("id")))
    families = _build_families_structure(all_ids, flat_index, global_models if global_models is not None else {})
    print(f"Built family map: {len(families)} families")

    models_text = format_models_output(len(models), plain_name)
    print(f"Formatted output: {models_text}")

    cache[plain_name] = {
        "all": all_ids,
        "families": families,
        "models_text": models_text,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "total_count": len(models),
    }

    section = inject_models_into_section(
        section, models_text, SETTINGS["marker_start"], SETTINGS["marker_end"]
    )
    print("[OK] Section updated")

    return True, None, section


# main
def process_file(
    file_path: Path, cache: dict, flat_index: Optional[Dict[str, Dict[str, Any]]] = None,
    global_models: Optional[Dict[str, Dict[str, Any]]] = None,
) -> Tuple[bool, int, int]:
    """
    Process one markdown file.

    Returns (file_changed, success_count, fail_count).
    """
    print(f"\n{'#'*60}")
    print(f"# File: {file_path.name}")
    print(f"{'#'*60}")

    content = read_markdown(file_path)
    sections = find_provider_sections(content)

    if not sections:
        print("  No provider sections found")
        return False, 0, 0

    success_count = 0
    fail_count = 0
    changed = False
    new_sections = []

    header_match = re.search(r"^###\s+(.+)$", content, re.MULTILINE)
    if header_match:
        prefix = content[: header_match.start()]
    else:
        prefix = content

    for provider_name, section in sections:
        original_section = section
        ok, _, updated_section = process_provider(
            provider_name, section, cache, flat_index, global_models
        )
        if ok:
            success_count += 1
            if updated_section != original_section:
                changed = True
        else:
            fail_count += 1
        new_sections.append((provider_name, updated_section))

    if changed:
        result = prefix
        for name, body in new_sections: 
            result += f"### {name}{body}"
        write_markdown(file_path, result)
        print(f"\n[OK] File saved: {file_path}")

    return changed, success_count, fail_count


def main():
    print("=" * 60)
    print("LLM Provider Models Auto-Updater")
    print("=" * 60)
    print(f"Started: {datetime.now(timezone.utc).isoformat()}")

    cache = load_cache()
    print(f"Cache loaded: {len(cache)} entries")

    print("  Loading models.dev data...")
    models_dev_data = get_models_dev_data()
    flat_index = build_flat_index(models_dev_data) if models_dev_data else None
    if flat_index:
        print(f"[OK] models.dev flat index: {len(flat_index)} models")
    else:
        print("[WARN] models.dev unavailable, using PRIORITY fallback only")

    skip_files = set(SETTINGS.get("skip_files", []))
    md_files = [
        p for p in sorted(DOCS_DIR.glob("*.md"))
        if p.name not in skip_files
    ]
    print(f"Found {len(md_files)} markdown files (skipped: {len(skip_files)})")

    global_models: Dict[str, Dict[str, Any]] = {}

    total_success = 0
    total_fail = 0
    total_changed = 0

    for file_path in md_files:
        changed, ok, fail = process_file(file_path, cache, flat_index, global_models)
        if changed:
            total_changed += 1
        total_success += ok
        total_fail += fail
        if SETTINGS.get("request_delay", 0) > 0:
            time.sleep(SETTINGS["request_delay"])
    meta_files = ["free.md", "freemium.md", "paid.md"]
    total_providers = 0
    for fname in meta_files:
        path = DOCS_DIR / fname
        if path.exists():
            content = path.read_text(encoding="utf-8")
            total_providers += len(re.findall(r"^###\s+", content, re.MULTILINE))
    cache["_models"] = global_models
    cache["_providers_count"] = total_providers
    timestamps = []
    for k, v in cache.items():
        if isinstance(v, dict) and v.get("timestamp") and not k.startswith("_"):
            timestamps.append(v["timestamp"])
    if timestamps:
        timestamps.sort(reverse=True)
        dt = datetime.fromisoformat(timestamps[0])
        cache["_models_updated"] = dt.strftime("%Y-%m-%d %H:%M UTC")
    save_cache(cache)

    print(f"\n{'='*60}")
    print(f"Results: {total_success} OK, {total_fail} failed")
    print(f"Files changed: {total_changed}/{len(md_files)}")
    print(f"Finished: {datetime.now(timezone.utc).isoformat()}")
    print(f"{'='*60}")
    if total_fail > 0:
        sys.exit(1)


if __name__ == "__main__":
    main()
