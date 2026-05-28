from __future__ import annotations
import re
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple
    
    
# Paths
SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR.parent.parent
DOCS_DIR = REPO_ROOT / "docs"
CACHE_PATH = DOCS_DIR / "models_data.json"
PROVIDERS_JSON = SCRIPT_DIR / "providers.json"
MODELS_DEV_CACHE_PATH = REPO_ROOT / ".github" / "models_dev_cache.json"
CHANGELOG_PATH = DOCS_DIR / "changelog.md"
INDEX_PATH = DOCS_DIR / "index.md"
SKIP_FILES: Set[str] = {"changelog.md", "dangerous.md", "index.md", "index_full.md"}

# Markers for auto-update model injection
MARKER_START = "<!-- MODELS_START -->"
MARKER_END = "<!-- MODELS_END -->"

# API settings
MODELS_DEV_API_URL = "https://models.dev/api.json"
CACHE_TTL_SECONDS = 24 * 60 * 60  # 24 hours

FALLBACK_MODELS_PATHS: List[str] = ["/v1beta/models", "/api/models", "/models"]


# API keys config


# header: HTTP header name (default: "Authorization")
# prefix: prefix before the key value (default: "Bearer", empty string = no prefix)
API_KEYS_CONFIG: Dict[str, Dict[str, Optional[str]]] = {
    "Agent Router": 
        {"env": "AGENT_ROUTER_API_KEY", "header": None, "prefix": None},
    "CrowAI": 
        {"env": "CROWAI_API_KEY", "header": None, "prefix": None},
    "Google AI Studio": 
        {"env": "GOOGLE_AI_STUDIO_API_KEY", "header": None, "prefix": None},
    "Mistral": 
        {"env": "MISTRAL_API_KEY", "header": None, "prefix": None},
    "Cerebras": 
        {"env": "CEREBRAS_API_KEY", "header": None, "prefix": None},
    "Groq": 
        {"env": "GROQ_API_KEY", "header": None, "prefix": None},
    "SwiftRouter": 
        {"env": "SWIFTROUTER_API_KEY", "header": None, "prefix": None},
    "NanoGPT": 
        {"env": "NANO_GPT_API_KEY", "header": None, "prefix": None},
    "DeepInfra": 
        {"env": "DEEPINFRA_API_KEY", "header": None, "prefix": None},
}

# General settings
SETTINGS: Dict[str, Any] = {
    "timeout_seconds": 15,
    "marker_start": MARKER_START,
    "marker_end": MARKER_END,
    "request_delay": 1,
    "skip_files": list(SKIP_FILES),
}

# Category maps and validation sets
CATEGORY_MAP: Dict[str, str] = {
    "freemium": "freemium.md",
    "free": "free.md",
    "paid": "paid.md",
    "caution": "caution.md",
    "dangerous": "dangerous.md",
}

VALID_CATEGORIES: Set[str] = set(CATEGORY_MAP.keys())
VALID_TESTING_STATUSES: Set[Optional[str]] = {"tested", "untested", "in-progress", None}
VALID_SERVICE_STATUSES: Set[str] = {
    "official", "official-partner", "aggregator",
    "development", "unofficial", "unknown",
    "deprecated", "community", "mirror", "experimental",
}

# Family tier prefixes
FAMILY_TIER_PREFIXES: List[Tuple[str, int]] = [
    # Tier 1 — top priority
    ("claude-", 1),
    # Tier 2 — major commercial families
    ("deepseek-reasoner", 2),
    ("deepseek-chat", 2),
    ("deepseek-coder", 2),
    ("deepseek", 2),
    ("mimo", 2),
    ("glm", 2),
    ("gpt", 2),
    ("gemini", 2),
    ("kimi", 2),
    ("qwen3.6", 2),
    ("qwen3.5", 2),
    ("qwen-vl", 2),
    ("qwen-coder", 2),
    ("qwen", 2),
    ("grok", 2),
    ("minimax", 2),
    ("o-pro", 2),
    ("o-mini", 2),
    ("o-", 2),
    # Tier 3 — open / open weights + established commercial
    ("llama", 3),
    ("mistral", 3),
    ("codestral", 3),
    ("devstral", 3),
    ("gemma-4", 3),
    ("gemma-3", 3),
    ("gemma", 3),
    ("phi-4", 3),
    ("phi", 3),
    ("mixtral", 3),
    ("magistral", 3),
    ("ministral", 3),
    ("hermes", 3),
    ("command", 3),
    ("nemotron", 3),
    ("granite", 3),
    ("nova", 3),
    ("sonar", 3),
    # Tier 4 — niche / specialized / embeddings / image / audio
    ("yi", 4),
    ("bge", 4),
    ("flux", 4),
    ("dall-e", 4),
    ("whisper", 4),
    ("text-embedding", 4),
    ("titan-embed", 4),
    ("cohere-embed", 4),
    ("embed", 4),
    ("voyage", 4),
    ("elevenlabs", 4),
    ("recraft", 4),
    ("runway", 4),
    ("sora", 4),
    ("jamba", 4),
    ("stable-diffusion", 4),
    ("veo", 4),
    ("ideogram", 4),
    ("imagen", 4),
    ("bart", 4),
    ("distilbert", 4),
    ("m2m", 4),
    ("voxtral", 4),
    ("melotts", 4),
    ("mm-poly", 4),
    ("smart-turn", 4),
    ("liquid", 4),
    ("mercury", 4),
    ("osmosis", 4),
    ("morph", 4),
    ("longcat", 4),
    ("lyria", 4),
    ("unsloth", 4),
    ("venice", 4),
    ("v0", 4),
    ("ring", 4),
    ("ray", 4),
    ("reka", 4),
    ("rednote", 4),
    ("sarvam", 4),
    ("seed", 4),
    ("solar", 4),
    ("step", 4),
    ("tako", 4),
    ("tngtech", 4),
    ("topazlabs", 4),
    ("trinity", 4),
    ("allenai", 4),
    ("alpha", 4),
    ("aura", 4),
    ("baichuan", 4),
    ("big-pickle", 4),
    ("canopylabs", 4),
    ("chutesai", 4),
    ("cogito", 4),
    ("ernie", 4),
    ("hunyuan", 4),
    ("hy", 4),
    ("hy3-free", 4),
    ("indictrans", 4),
    ("jais", 4),
    ("kat-coder", 4),
    ("ling", 4),
    ("ling-flash-free", 4),
    ("lucid", 4),
    ("mai", 4),
    ("nano-banana", 4),
    ("nousresearch", 4),
    ("palmyra", 4),
    ("pangu", 4),
    ("pixtral", 4),
    ("plamo", 4),
    ("qvq", 4),
    ("qwerky", 4),
    ("rnj", 4),
    ("allam", 4),
    ("auto", 4),
    ("groq", 4),
    ("model-router", 4),
]

def get_tier_for_family(family: str) -> int:
    """Return tier level for a known family; unknown families get tier 5."""
    for prefix, tier in FAMILY_TIER_PREFIXES:
        if family.startswith(prefix):
            return tier
    return 5


# Tooltips
SERVICE_STATUS_TOOLTIPS: Dict[str, str] = {
    "official": "Official service",
    "official-partner": "Official Partner",
    "aggregator": "Aggregator / AI Gateway",
    "development": "In Development",
    "unofficial": "Unofficial",
    "unknown": "Unknown",
    "deprecated": "Deprecated / No longer active",
    "community": "Community-driven project",
    "mirror": "Mirror of another provider's API",
    "experimental": "Experimental / May be unstable",
}

PROVIDER_META_TOOLTIPS: Dict[str, str] = {
    "tested": "Tested by the author",
    "untested": "Not tested yet",
    "in-progress": "Currently being tested",
}

REQUIREMENT_TOOLTIPS: Dict[str, str] = {
    "email": "Email required",
    "registration": "Standard registration",
    "phone": "Phone verification required",
    "card": "Bank card required",
    "special": "Special registration conditions",
    "discord": "Discord account required",
}

WARNING_TOOLTIP: str = "Has concerns - see Warning page. Hold to navigate"
VALID_SVG_REQUIREMENTS: Set[str] = {"email", "registration", "phone", "card", "special", "discord"}
VALID_REQUIREMENTS: Set[str] = VALID_SVG_REQUIREMENTS


# Regular expressions for markdown parsing
HEADING_RE: re.Pattern = re.compile(r"^### (.+)$")
MD_LINK_RE: re.Pattern = re.compile(r"\[([^\]]*)\]\(([^)]*)\)")
BACKTICK_RE: re.Pattern = re.compile(r"`([^`]+)`")
ADMONITION_RE: re.Pattern = re.compile(r'^!!!\s+(tip|danger)\s+"(.+)"\s*$')
META_STATUS_RE: re.Pattern = re.compile(r"provider-meta__status--(\w+)")
META_TESTING_RE: re.Pattern = re.compile(r"provider-meta__testing--([\w-]+)")
META_WARNING_RE: re.Pattern = re.compile(r'href="[^"]*#([^"]+)"[^>]*provider-meta__warning')
MODELS_MARKER_RE: re.Pattern = re.compile(r"<!--\s*MODELS_START\s*-->")


# Inline formatting constants (for custom BBCode-like tags in markdown)
INLINE_TAG_MAP: Dict[str, Tuple[Optional[str], Optional[str]]] = {
    "bold": ("strong", None),
    "italic": ("em", None),
    "bold italic": ("strong", "em"),
    "italic bold": ("strong", "em"),
    "b": ("strong", None),
    "i": ("em", None),
    "bi": ("strong", "em"),
    "ib": ("strong", "em"),
}

_INLINE_COLORS: Set[str] = {"green", "red", "orange", "blue", "yellow", "purple"}
INLINE_TAG_RE: re.Pattern = re.compile(
    r'\[('
    r'bold\s+italic|italic\s+bold|'
    r'bi|ib|'
    r'bold|italic|b|i'
    r')(?:\s+(' + '|'.join(_INLINE_COLORS) + r'))?'
    r'\](.*?)\[/\1(?:\s+\2)?\]',
    re.DOTALL,
)
INLINE_COLOR_RE: re.Pattern = re.compile(
    r'\[(' + '|'.join(_INLINE_COLORS) + r')\](.*?)\[/\1\]',
    re.DOTALL,
)


