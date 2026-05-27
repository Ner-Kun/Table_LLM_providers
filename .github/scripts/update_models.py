import asyncio
import io
import json
import os
import re
import sys

from scrapers import SCRAPERS

from constants import (
    API_KEYS_CONFIG,
    CACHE_PATH,
    DOCS_DIR,
    FALLBACK_MODELS_PATHS,
    PROVIDERS_JSON,
    REPO_ROOT,
    SETTINGS,
    get_tier_for_family,
)
from provider_meta import get_plain_provider_name
from models_dev_client import (
    build_flat_index,
    get_model_entry,
    get_models_dev_data,
)

# Fix Windows console encoding
stdout = sys.stdout
if isinstance(stdout, io.TextIOWrapper) and hasattr(stdout, "reconfigure"):
    stdout.reconfigure(encoding="utf-8")
elif sys.platform == "win32" and hasattr(stdout, "buffer"):
    sys.stdout = io.TextIOWrapper(stdout.buffer, encoding="utf-8")

import httpx  # noqa: E402
import urllib.parse  # noqa: E402
from datetime import datetime, timezone  # noqa: E402
from pathlib import Path  # noqa: E402
from rich.console import Console  # noqa: E402
from typing import Any, Dict, List, Mapping, Optional, Tuple  # noqa: E402

console = Console()

DEFAULT_HEADERS = {
    "Accept": "application/json",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
}
PROVIDER_HEADING_RE = re.compile(r"^###\s+(.+)$", re.MULTILINE)
BASE_URL_RE = re.compile(r"\|\s*`(https?://[^`]+)`\s*\|")
MANUAL_MODEL_RE = re.compile(r"•\s+\S+")
META_FILES = ("free.md", "freemium.md", "paid.md")


_PROVIDER_SEMAPHORE = asyncio.Semaphore(SETTINGS.get("max_concurrent", 10))


def load_dotenv(path: Path) -> None:
    """Load KEY=VALUE pairs from a .env file into os.environ."""
    if not path.exists():
        return
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, val = line.partition("=")
        key = key.strip()
        val = val.strip().strip('"\'')
        if key:
            os.environ.setdefault(key, val)


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


def load_provider_base_urls() -> Dict[str, str]:
    """Load provider name -> base_url map from providers.json once per run."""
    base_urls: Dict[str, str] = {}
    for task in load_current_tasks():
        if not isinstance(task, dict):
            continue
        name = task.get("name")
        base_url = task.get("base_url")
        if isinstance(name, str) and isinstance(base_url, str) and base_url.strip():
            base_urls[get_plain_provider_name(name)] = base_url.rstrip("/")
    return base_urls


def get_base_url_for_provider(
    provider_name: str,
    section: str,
    provider_base_urls: Optional[Mapping[str, str]] = None,
) -> Optional[str]:
    """Try providers.json first, fall back to parsing .md."""
    if provider_base_urls:
        plain_name = get_plain_provider_name(provider_name)
        base_url = provider_base_urls.get(plain_name)
        if base_url:
            return base_url
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
    console.print(f"[bold green]OK[/] Cache saved ({len(data)} providers, {models_count} unique models)")


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
    parts = PROVIDER_HEADING_RE.split(content)

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
    matches = BASE_URL_RE.findall(section)
    if matches:
        return matches[-1].rstrip("/")
    return None


def has_markers(section: str) -> bool:
    """Check if section contains MODELS_START and MODELS_END markers."""
    return (
        SETTINGS["marker_start"] in section and SETTINGS["marker_end"] in section
    )


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


def parse_models_payload(data: Any) -> Optional[List[Dict[str, Any]]]:
    """Extract a model list from common OpenAI-compatible API response shapes."""
    if isinstance(data, dict):
        if isinstance(data.get("data"), list):
            data = data["data"]
        elif isinstance(data.get("models"), list):
            data = data["models"]
        else:
            return None
    if not isinstance(data, list):
        return None
    return [item for item in data if isinstance(item, dict)]


# fetch models
async def fetch_models(
    api_urls: List[str],
    headers: Optional[Mapping[str, str]] = None,
    timeout: int = 15,
    max_retries: int = 2,
    provider_label: str = "",
    client: Optional[httpx.AsyncClient] = None,
) -> Optional[List[Dict[str, Any]]]:
    """
    Fetch model list from model endpoint URLs, trying each in sequence.
    Falls back to alternative paths if the primary URL fails.
    Returns list of model dicts, or None if all URLs fail.
    """
    tag = f"[{provider_label}] " if provider_label else ""
    req_headers = dict(DEFAULT_HEADERS)
    if headers:
        req_headers.update(headers)

    close_client = client is None
    if client is None:
        client = httpx.AsyncClient(timeout=timeout)

    try:
        for idx, api_url in enumerate(api_urls):
            if idx > 0:
                console.print(f"{tag}[bold]Fallback {idx}:[/] trying {api_url}")

            retries = max_retries if idx == 0 else 0
            for attempt in range(retries + 1):
                try:
                    resp = await client.get(api_url, headers=req_headers, timeout=timeout)
                    resp.raise_for_status()
                    models = parse_models_payload(resp.json())
                    if models is not None:
                        return models
                    if idx == 0:
                        console.print(f"{tag}[bold]Unexpected JSON format, trying fallbacks...[/]")
                    else:
                        console.print(f"{tag}[bold]Unexpected JSON format from[/] {api_url}")
                    break
                except (httpx.RequestError, httpx.HTTPStatusError, json.JSONDecodeError, ValueError) as e:
                    prefix = f"Attempt {attempt + 1}/{retries + 1} for " if retries > 0 else ""
                    console.print(f"{tag}[bold yellow]WARN[/] {prefix}{api_url} failed: {e}")
                    if attempt < retries:
                        wait = 2 ** attempt
                        console.print(f"{tag}  Retrying in {wait}s...")
                        await asyncio.sleep(wait)
                    else:
                        console.print(f"{tag}[bold red]ERR[/] Failed to fetch {api_url}")
        return None
    finally:
        if close_client:
            await client.aclose()


def resolve_model_family(
    model_id: str,
    flat_index: Optional[Dict[str, Dict[str, Any]]],
) -> Tuple[int, str, Optional[Dict[str, Any]]]:
    """Determine model family from models.dev flat index.

    Returns:
        (tier_level, family_key, metadata_or_None)

    If flat_index is unavailable or model is unknown, returns (5, "other", None).
    """
    if not flat_index:
        return (5, "other", None)

    entry = get_model_entry(flat_index, model_id)
    if entry:
        family = entry.get("family")
        if family:
            tier = get_tier_for_family(family)
            return (tier, family, entry)
    return (5, "other", None)


def build_family_map(
    model_ids: List[str],
    flat_index: Optional[Dict[str, Dict[str, Any]]] = None,
) -> Dict[str, List[str]]:
    """Build a map of family_key -> [model_ids] for all models."""
    families: Dict[str, List[str]] = {}

    for model_id in model_ids:
        tier, family_key, _ = resolve_model_family(model_id, flat_index)
        family_key = family_key if family_key and tier < 99 else "other"
        families.setdefault(family_key, []).append(model_id)

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
        console.print(f"[bold]DEBUG[/] Markers not found: start={start_idx}, end={end_idx}")
        return section

    if end_idx <= start_idx:
        console.print(f"[bold]DEBUG[/] Invalid marker order: start={start_idx}, end={end_idx}")
        return section
    before = section[: start_idx + len(start_marker)]
    after = section[end_idx:]
    new_section = f"{before}{models_text}{after}"

    return new_section


# process single provider
def _build_families_structure(
    all_ids: List[str],
    flat_index: Optional[Dict[str, Dict[str, Any]]],
    global_models: Dict[str, Dict[str, Any]],
) -> Dict[str, Dict[str, Any]]:
    """Build families dict with deduplicated model IDs.

    Model metadata is collected into the provided global_models dict
    instead of being duplicated per-provider.
    """
    family_map = build_family_map(all_ids, flat_index)

    families: Dict[str, Dict[str, Any]] = {}
    for fam_key, model_ids in family_map.items():
        if flat_index:
            for mid in model_ids:
                if mid in global_models:
                    continue
                meta = get_model_entry(flat_index, mid)
                if meta:
                    global_models[mid] = meta.copy()
        families[fam_key] = {"models": model_ids}

    return families


def count_manual_models(section: str) -> int:
    """Count manually listed models in section (before MODELS_START)."""
    idx = section.find(SETTINGS["marker_start"])
    before = section[:idx] if idx != -1 else section
    return len(MANUAL_MODEL_RE.findall(before))


def build_provider_headers(provider_name: str) -> Tuple[Dict[str, str], Dict[str, str]]:
    """Build request headers and return auth headers separately for logging."""
    auth = get_auth_headers(provider_name)
    headers = dict(DEFAULT_HEADERS)
    headers.update(auth)
    return headers, auth


def extract_model_ids(models: List[Dict[str, Any]]) -> List[str]:
    """Return stable, deduplicated model IDs from API model dicts."""
    ids = (
        model_id
        for model in models
        if isinstance(model_id := model.get("id"), str) and model_id
    )
    return list(dict.fromkeys(ids))


def build_models_dev_pricing(
    all_ids: List[str],
    global_models: Mapping[str, Dict[str, Any]],
) -> Dict[str, Any]:
    """Build fallback pricing from models.dev metadata."""
    pricing: Dict[str, Any] = {"badge": "Reference", "models": {}}
    pricing_models = pricing["models"]

    for mid in all_ids:
        meta = global_models.get(mid)
        if not meta:
            continue
        cost = meta.get("cost")
        if not isinstance(cost, dict) or not cost:
            continue
        limit = meta.get("limit")
        pricing_models[mid] = {
            "input": cost.get("input"),
            "output": cost.get("output"),
            "cache": cost.get("cache_read") or cost.get("cache_write"),
            "source_provider": meta.get("source_provider"),
            "context": limit.get("context") if isinstance(limit, dict) else None,
        }

    return pricing


def merge_pricing(
    provider_cache: Dict[str, Any],
    scraper_pricing: Optional[Dict[str, Any]],
    models_pricing: Dict[str, Any],
) -> None:
    """Attach scraper pricing and models.dev fallback pricing to provider cache."""
    fallback_models = models_pricing.get("models", {})
    if scraper_pricing:
        scraper_models = scraper_pricing.setdefault("models", {})
        for mid, pricing in fallback_models.items():
            scraper_models.setdefault(mid, pricing)
        provider_cache["pricing"] = scraper_pricing
        provider_cache["pricing_fallback"] = models_pricing
        if scraper_pricing.get("metadata"):
            provider_cache["metadata"] = scraper_pricing["metadata"]
    elif fallback_models:
        provider_cache["pricing"] = models_pricing


def _handle_api_failure(
    plain_name: str, cache: dict, section: str
) -> Tuple[bool, Optional[str], str]:
    """Try cache fallback on API failure, then check for manual models."""
    cached = cache.get(plain_name)
    if cached and cached.get("models_text"):
        console.print(f"[bold yellow]WARN[/] [{plain_name}] Using cached data from {cached.get('timestamp', 'unknown')}")
        section = inject_models_into_section(
            section, cached["models_text"], SETTINGS["marker_start"], SETTINGS["marker_end"]
        )
        console.print(f"[bold green]OK[/] [{plain_name}] Updated with cached models")
        return True, None, section

    manual_count = count_manual_models(section)
    if manual_count > 0:
        console.print(f"[bold]INFO[/] [{plain_name}] No API /v1/models endpoint, "
            f"preserving {manual_count} manually added model(s)")
        return True, None, section

    console.print(f"[bold yellow]WARN[/] [{plain_name}] API unavailable "
        f"and no manually added models found. Section unchanged.")
    return True, None, section


async def process_provider_async(
    provider_name: str,
    section: str,
    cache: dict,
    flat_index: Optional[Dict[str, Dict[str, Any]]] = None,
    global_models: Optional[Dict[str, Dict[str, Any]]] = None,
    provider_base_urls: Optional[Mapping[str, str]] = None,
    client: Optional[httpx.AsyncClient] = None,
) -> Tuple[bool, Optional[str], str]:
    """
    Process one provider section.

    Returns (success, error_message, updated_section).
    """
    plain_name = get_plain_provider_name(provider_name)
    console.print(f"\n[bold]Processing:[/] {plain_name}")
    if not has_markers(section):
        console.print("[bold blue]SKIP[/] No markers found, skipping")
        return True, None, section

    base_url = get_base_url_for_provider(provider_name, section, provider_base_urls)
    if not base_url:
        msg = f"Could not find Base URL for '{provider_name}'"
        console.print(f"[bold red]ERR[/] {msg}")
        return False, msg, section

    console.print(f"Base URL: {base_url}")
    api_urls = build_models_urls(base_url)
    console.print(f"API URL:  {api_urls[0]}")
    if len(api_urls) > 1:
        console.print(f"Fallbacks: {', '.join(api_urls[1:])}")

    headers, auth = build_provider_headers(provider_name)
    if auth:
        console.print(f"[bold yellow]AUTH[/] Using API key ({list(auth.keys())[0]})")
    else:
        console.print("[bold]AUTH[/] No API key, requesting without auth")

    async with _PROVIDER_SEMAPHORE:
        models = await fetch_models(
            api_urls,
            headers=headers,
            timeout=SETTINGS["timeout_seconds"],
            provider_label=plain_name,
            client=client,
        )

    if models is None:
        return _handle_api_failure(plain_name, cache, section)

    console.print(f"[bold]{plain_name}:[/] Fetched {len(models)} models total")

    all_ids = extract_model_ids(models)
    global_models = global_models if global_models is not None else {}
    families = _build_families_structure(all_ids, flat_index, global_models)
    console.print(f"[bold]{plain_name}:[/] Built family map: {len(families)} families")

    models_text = format_models_output(len(models), plain_name)

    provider_cache = {
        "all": all_ids,
        "families": families,
        "models_text": models_text,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "total_count": len(models),
    }
    cache[plain_name] = provider_cache

    scraper_pricing = None
    if plain_name in SCRAPERS:
        console.print(f"[bold]{plain_name}:[/] Fetching pricing...")
        async with _PROVIDER_SEMAPHORE:
            scraper_pricing = await SCRAPERS[plain_name].fetch_pricing()
        if scraper_pricing:
            console.print(f"[bold green]OK[/] [{plain_name}] Scraper returned {len(scraper_pricing['models'])} prices")
        else:
            console.print(f"[bold yellow]WARN[/] [{plain_name}] Scraper failed")

    models_pricing = build_models_dev_pricing(all_ids, global_models)
    merge_pricing(provider_cache, scraper_pricing, models_pricing)
    if not scraper_pricing and models_pricing.get("models"):
        console.print(f"[bold green]OK[/] [{plain_name}] Using models.dev pricing ({len(models_pricing['models'])} models)")

    section = inject_models_into_section(
        section, models_text, SETTINGS["marker_start"], SETTINGS["marker_end"]
    )
    console.print(f"[bold green]OK[/] [{plain_name}] Section updated")

    return True, None, section


# main
async def process_file_async(
    file_path: Path, cache: dict, flat_index: Optional[Dict[str, Dict[str, Any]]] = None,
    global_models: Optional[Dict[str, Dict[str, Any]]] = None,
    provider_base_urls: Optional[Mapping[str, str]] = None,
    client: Optional[httpx.AsyncClient] = None,
) -> Tuple[bool, int, int]:
    """
    Process one markdown file.
    All providers in the file are fetched concurrently.

    Returns (file_changed, success_count, fail_count).
    """
    console.print(f"\n[bold]File:[/] {file_path.name}")
    content = read_markdown(file_path)
    sections = find_provider_sections(content)

    if not sections:
        console.print("  No provider sections found")
        return False, 0, 0

    header_match = PROVIDER_HEADING_RE.search(content)
    if header_match:
        prefix = content[: header_match.start()]
    else:
        prefix = content

    tasks = [
        process_provider_async(
            name,
            section,
            cache,
            flat_index,
            global_models,
            provider_base_urls,
            client,
        )
        for name, section in sections
    ]
    results = await asyncio.gather(*tasks, return_exceptions=True)

    success_count = 0
    fail_count = 0
    changed = False
    new_sections = []

    for (provider_name, section), result in zip(sections, results):
        if isinstance(result, BaseException):
            console.print(f"[bold red]ERR[/] {get_plain_provider_name(provider_name)} raised: {result}")
            fail_count += 1
            new_sections.append((provider_name, section))
            continue

        ok, _, updated_section = result
        if ok:
            success_count += 1
            if updated_section != section:
                changed = True
        else:
            fail_count += 1
        new_sections.append((provider_name, updated_section))

    if changed:
        result_content = prefix + "".join(
            f"### {name}{body}"
            for name, body in new_sections
        )
        write_markdown(file_path, result_content)
        console.print(f"\n[bold green]OK[/] File saved: {file_path}")

    return changed, success_count, fail_count


async def main_async() -> None:
    console.print("[bold]LLM Provider Models Auto-Updater[/]")
    console.print(f"Started: {datetime.now(timezone.utc).isoformat()}")

    env_file = REPO_ROOT / ".env"
    if env_file.exists():
        load_dotenv(env_file)
        console.print(f"[bold green]OK[/] Loaded env variables from {env_file}")
    else:
        console.print(f"[bold]INFO[/] No .env file found at {env_file}")

    cache = load_cache()
    console.print(f"Cache loaded: {len(cache)} entries")

    console.print("  Loading models.dev data...")
    async with httpx.AsyncClient(timeout=SETTINGS["timeout_seconds"]) as client:
        models_dev_data = await get_models_dev_data(client)
        flat_index = build_flat_index(models_dev_data) if models_dev_data else None
        if flat_index:
            console.print(f"[bold green]OK[/] models.dev flat index: {len(flat_index)} models")
        else:
            console.print("[bold yellow]WARN[/] models.dev unavailable, all models will be grouped as 'other'")

        skip_files = set(SETTINGS.get("skip_files", []))
        md_files = [
            p for p in sorted(DOCS_DIR.glob("*.md"))
            if p.name not in skip_files
        ]
        console.print(f"Found {len(md_files)} markdown files (skipped: {len(skip_files)})")

        provider_base_urls = load_provider_base_urls()
        if provider_base_urls:
            console.print(f"Provider config loaded: {len(provider_base_urls)} base URLs")

        global_models: Dict[str, Dict[str, Any]] = {}

        total_success = 0
        total_fail = 0
        total_changed = 0

        for file_path in md_files:
            changed, ok, fail = await process_file_async(
                file_path,
                cache,
                flat_index,
                global_models,
                provider_base_urls,
                client,
            )
            if changed:
                total_changed += 1
            total_success += ok
            total_fail += fail
            if SETTINGS.get("request_delay", 0) > 0:
                await asyncio.sleep(SETTINGS["request_delay"])

    total_providers = 0
    for fname in META_FILES:
        path = DOCS_DIR / fname
        if path.exists():
            content = path.read_text(encoding="utf-8")
            total_providers += len(PROVIDER_HEADING_RE.findall(content))
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

    console.print(f"\nResults: [bold green]{total_success} OK[/], [bold red]{total_fail} failed[/]")
    console.print(f"Files changed: {total_changed}/{len(md_files)}")
    console.print(f"Finished: {datetime.now(timezone.utc).isoformat()}")
    if total_fail > 0:
        sys.exit(1)


def main():
    """Sync entry point — wraps the async main."""
    asyncio.run(main_async())


if __name__ == "__main__":
    main()
