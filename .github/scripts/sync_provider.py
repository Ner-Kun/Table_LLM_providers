"""
[
    {
        "name": "Provider Name",
        "category": "free",
        "service_status": "official",
        "testing_status": "tested",
        "requirements": ["email", "registration"],
        "requirements_notes": "",
        "limits": "• RPM - 20\n• RPD - 50",
        "limits_url": "https://example.com/limits",
        "models_url": "https://example.com/models",
        "manual_models": ["vagina", "dick"],
        "auto_update_models": false,
        "registration_url": "https://example.com/signup",
        "api_key_url": "https://example.com/keys",
        "base_url": "https://api.example.com/v1",
        "features": [
        "Feature one.",
        "Feature two with [bold green]highlighted text[/bold green]."
        ],
        "disadvantages": [
        "Disadvantage one.",
        "Disadvantage two with [red]warning[/red]."
        ]
    }
]



FIELD DESCRIPTIONS
    name               (string, required)   — Provider display name.
    category           (string, required)   — "free" | "freemium" | "paid" | "dangerous"
    service_status     (string, required)   — "official" | "official-partner" | "development" | "unofficial"
    testing_status     (string|null)        — "tested" | "untested" | "in-progress" | null
    requirements       (string[])           — Requirement icon keys (see below).
    requirements_notes (string)             — Extra text after requirement icons.
    limits             (string)             — Rate limits. Use "—" for none.
    limits_url         (string|null)        — URL to rate-limits page (globe icon).
    models_url         (string|null)        — URL to full models list (globe icon).
    manual_models      (string[])           — Static model names (shown if auto_update_models=false).
    auto_update_models (boolean|null)        — true = enable auto-update via API markers.
    registration_url   (string, required)   — Sign-up page URL.
    api_key_url        (string|null)        — API key page URL.
    base_url           (string, required)   — API endpoint, e.g. https://api.example.com/v1
    features           (string[])           — List of feature bullet points.
    disadvantages      (string[])           — List of disadvantage bullet points.

REQUIREMENT ICON KEYS
    "email"        — Email required
    "registration" — Standard registration
    "phone"        — Phone verification required
    "card"         — Bank card required
    "special"      — Special registration conditions
    "discord"      — Discord account required



INLINE FORMATTING (features / disadvantages / limits / requirements_notes)


Colors:
    [green]text[/green]     → green text
    [red]text[/red]         → red text
    [orange]text[/orange]   → orange text
    [blue]text[/blue]       → blue text
    [yellow]text[/yellow]   → yellow text
    [purple]text[/purple]   → purple text

Styles:
    [bold]text[/bold]               → bold
    [italic]text[/italic]           → italic
    [bold italic]text[/bold italic] → bold + italic

Short aliases: b → bold, i → italic, bi → bold italic

Combined:
    [bold green]text[/bold green]         → bold green
    [italic red]text[/italic red]         → italic red
    [bold italic orange]text[/bold italic orange] → bold italic orange

Examples:
    "[green]**$10 bonus**[/green] upon registration"
    "[red]**Phone verification is buggy**[/red]"
    "[bold blue]Important[/bold blue] note here"



AUTO-UPDATE MODELS


Set "auto_update_models": true to enable automatic model list refresh.
The script inserts HTML markers:
    <!-- MODELS_START --> ... <!-- MODELS_END -->

update_models.py detects these markers and fetches /v1/models from base_url.
Set to false or omit to disable auto-update (static manual_models only).

Requirements for auto-update:
    - base_url must be a working OpenAI-compatible API endpoint
    - models_url is still shown as the globe icon link
"""

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from provider_meta import (
    get_plain_provider_name,
    render_link_icon,
    render_provider_meta_badges,
    render_requirement_icons,
    VALID_SVG_REQUIREMENTS,
)

SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR.parent.parent
DOCS_DIR = REPO_ROOT / "docs"
PROVIDERS_JSON = SCRIPT_DIR / "providers.json"

CATEGORY_MAP: Dict[str, str] = {
    "freemium": "freemium.md",
    "free": "free.md",
    "paid": "paid.md",
    "caution": "caution.md",
    "dangerous": "dangerous.md",
}

VALID_CATEGORIES = set(CATEGORY_MAP.keys())
VALID_TESTING_STATUSES = {"tested", "untested", "in-progress", None}
VALID_SERVICE_STATUSES = {"official", "official-partner", "development", "unofficial"}
VALID_REQUIREMENTS = VALID_SVG_REQUIREMENTS
HEADING_RE = re.compile(r"^### (.+)$")


# Validation
class ValidationError(Exception):
    """Raised when a provider entry fails validation."""


def validate_provider(entry: Dict[str, Any], index: int) -> None:
    """Validate a single provider entry. Raises ValidationError on failure."""
    errors: List[str] = []

    name = entry.get("name")
    if not isinstance(name, str) or not name.strip():
        errors.append("'name' is required and must be a non-empty string")

    category = entry.get("category")
    if category not in VALID_CATEGORIES:
        errors.append(
            f"'category' must be one of {sorted(VALID_CATEGORIES)}, got {category!r}"
        )

    reg_url = entry.get("registration_url")
    if not isinstance(reg_url, str) or not reg_url.strip():
        errors.append("'registration_url' is required and must be a non-empty string")

    base_url = entry.get("base_url")
    if not isinstance(base_url, str) or not base_url.strip():
        errors.append("'base_url' is required and must be a non-empty string")

    service_status = entry.get("service_status")
    if service_status not in VALID_SERVICE_STATUSES:
        errors.append(
            f"'service_status' must be one of {sorted(VALID_SERVICE_STATUSES)}, got {service_status!r}"
        )

    testing_status = entry.get("testing_status")
    if testing_status is not None and testing_status not in VALID_TESTING_STATUSES:
        errors.append(
            f"'testing_status' must be one of {sorted(s for s in VALID_TESTING_STATUSES if s is not None)} or null, "
            f"got {testing_status!r}"
        )

    warning_id = entry.get("warning_id")
    if warning_id is not None and not isinstance(warning_id, str):
        errors.append("'warning_id' must be a string or null")

    requirements = entry.get("requirements", [])
    if not isinstance(requirements, list):
        errors.append("'requirements' must be a list")
    else:
        for req in requirements:
            if req not in VALID_REQUIREMENTS:
                errors.append(
                    f"Invalid requirement {req!r}; must be one of {sorted(VALID_REQUIREMENTS)}"
                )

    req_notes = entry.get("requirements_notes", "")
    if not isinstance(req_notes, str):
        errors.append("'requirements_notes' must be a string")

    limits = entry.get("limits", "—")
    if not isinstance(limits, str):
        errors.append("'limits' must be a string")

    limits_url = entry.get("limits_url")
    if limits_url is not None and not isinstance(limits_url, str):
        errors.append("'limits_url' must be a string or null")

    models_url = entry.get("models_url")
    if models_url is not None and not isinstance(models_url, str):
        errors.append("'models_url' must be a string or null")

    manual_models = entry.get("manual_models", [])
    if not isinstance(manual_models, list):
        errors.append("'manual_models' must be a list")
    else:
        for m in manual_models:
            if not isinstance(m, str):
                errors.append(f"Each item in 'manual_models' must be a string, got {type(m).__name__}")

    api_key_url = entry.get("api_key_url")
    if api_key_url is not None and not isinstance(api_key_url, str):
        errors.append("'api_key_url' must be a string or null")

    features = entry.get("features", [])
    if not isinstance(features, list):
        errors.append("'features' must be a list")
    else:
        for f in features:
            if not isinstance(f, str):
                errors.append(f"Each item in 'features' must be a string, got {type(f).__name__}")

    disadvantages = entry.get("disadvantages", [])
    if not isinstance(disadvantages, list):
        errors.append("'disadvantages' must be a list")
    else:
        for d in disadvantages:
            if not isinstance(d, str):
                errors.append(f"Each item in 'disadvantages' must be a string, got {type(d).__name__}")

    auto_update = entry.get("auto_update_models")
    if auto_update is not None and not isinstance(auto_update, bool):
        errors.append("'auto_update_models' must be a boolean (true/false) or null")

    if errors:
        label = name or f"entry #{index}"
        raise ValidationError(f"Provider {label}:\n  " + "\n  ".join(errors))

# Inline formatting

# Mapping of tag names
_INLINE_TAG_MAP: Dict[str, Tuple[Optional[str], Optional[str]]] = {
    "bold": ("strong", None),
    "italic": ("em", None),
    "bold italic": ("strong", "em"),
    "italic bold": ("strong", "em"),
    "b": ("strong", None),
    "i": ("em", None),
    "bi": ("strong", "em"),
    "ib": ("strong", "em"),
}
_INLINE_COLORS = {"green", "red", "orange", "blue", "yellow", "purple"}

_INLINE_TAG_RE = re.compile(
    r'\[('
    r'bold\s+italic|italic\s+bold|' # combined full
    r'bi|ib|' # combined short
    r'bold|italic|b|i' # single
    r')(?:\s+(' + '|'.join(_INLINE_COLORS) + r'))?' # optional color
    r'\](.*?)\[/\1(?:\s+\2)?\]', # content + closing tag
    re.DOTALL,
)
_INLINE_COLOR_RE = re.compile(
    r'\[(' + '|'.join(_INLINE_COLORS) + r')\](.*?)\[/\1\]',
    re.DOTALL,
)


def render_inline_formatting(text: str) -> str:
    """Convert custom inline tags in text to HTML."""
    def _replace_tag(m: re.Match) -> str:
        tag_names = m.group(1).strip()
        color = m.group(2)
        content = m.group(3)

        entry = _INLINE_TAG_MAP.get(tag_names)
        if entry is None:
            return m.group(0)

        outer_tag, inner_tag = entry

        if color:
            if inner_tag:
                inner = f'<{inner_tag} class="text-{color}">{content}</{inner_tag}>'
                return f'<{outer_tag}>{inner}</{outer_tag}>'
            else:
                return f'<{outer_tag} class="text-{color}">{content}</{outer_tag}>'
        else:
            if inner_tag:
                return f'<{outer_tag}><{inner_tag}>{content}</{inner_tag}></{outer_tag}>'
            else:
                return f'<{outer_tag}>{content}</{outer_tag}>'
    result = _INLINE_TAG_RE.sub(_replace_tag, text)

    def _replace_color(m: re.Match) -> str:
        color = m.group(1)
        content = m.group(2)
        return f'<span class="text-{color}">{content}</span>'
    result = _INLINE_COLOR_RE.sub(_replace_color, result)
    return result


# Markdown generation
def _build_models_cell(
    models_url: Optional[str],
    manual_models: List[str],
    auto_update: bool = False,
) -> str:
    """Build the Models table cell content with SVG globe icon.

    Manual models are always rendered outside markers.
    Markers are only used for the auto-update counter (+N more models).
    """
    parts: List[str] = []
    globe_icon = render_link_icon()
    if models_url:
        parts.append(f"[{globe_icon}]({models_url})")
    for model in manual_models:
        parts.append(f" • {model}")

    if auto_update:
        parts.append("<!-- MODELS_START --><!-- MODELS_END -->")

    return "<br>".join(parts) if parts else "—"


def _build_links_row(
    registration_url: str,
    api_key_url: Optional[str],
    base_url: str,
) -> str:
    """Build the second table (links) as a markdown string."""
    globe_icon = render_link_icon()
    api_key_cell = f"[{globe_icon}]({api_key_url})" if api_key_url else "—"
    return (
        "| Registration | API key | Base URL |\n"
        "|:---:|:---:|:---:|\n"
        f"| [{globe_icon}]({registration_url}) | {api_key_cell} | `{base_url}` |"
    )


def _build_admonition_block(title: str, items: List[str]) -> str:
    """Build an admonition block (tip/danger) from a list of items."""
    if not items:
        return ""
    admon_type = "tip" if title == "Features" else "danger"
    lines = [f'!!! {admon_type} "{title}"']
    for item in items:
        lines.append(f"    - {render_inline_formatting(item)}")
    return "\n".join(lines)

def generate_provider_markdown(entry: Dict[str, Any]) -> str:
    """
    Generate a complete markdown block for a single provider."""
    if entry.get("category") == "caution":
        return f"### {entry['name']}\n\n---\n"

    name = entry["name"]
    service_status = entry.get("service_status", "")
    testing_status = entry.get("testing_status")
    requirements = entry.get("requirements", [])
    limits = entry.get("limits", "—")
    limits_url = entry.get("limits_url")
    models_url = entry.get("models_url")
    manual_models = entry.get("manual_models", [])
    registration_url = entry["registration_url"]
    api_key_url = entry.get("api_key_url")
    base_url = entry["base_url"]
    features = entry.get("features", [])
    disadvantages = entry.get("disadvantages", [])
    requirements_notes = entry.get("requirements_notes", "")
    auto_update = entry.get("auto_update_models", False)
    warning_id = entry.get("warning_id") or ""
    testing_str = testing_status or ""
    meta_badges = render_provider_meta_badges(service_status, testing_str, warning_id)
    if isinstance(requirements, list) and requirements_notes and "special" not in requirements:
        requirements = requirements + ["special"]
    req_str = "\n".join(requirements) if requirements else ""
    req_html = render_requirement_icons(req_str, requirements_notes)
    models_cell = _build_models_cell(models_url, manual_models, auto_update)
    
    limits_html = render_inline_formatting(limits).replace("\n", "<br>")
    if limits_url:
        globe_icon = render_link_icon()
        limits_html = f'[{globe_icon}]({limits_url})<br>{limits_html}'
    table1 = (
        "| Requirements | Limits | Models |\n"
        "|:---|:---:|:---:|\n"
        f"| {req_html} | {limits_html} | {models_cell} |"
    )
    table2 = _build_links_row(registration_url, api_key_url, base_url)

    features_block = _build_admonition_block("Features", features)
    disadvantages_block = _build_admonition_block("Disadvantages", disadvantages)

    parts = [f"### {name}{meta_badges}", "", table1, "", table2]
    if features_block:
        parts.extend(["", features_block])
    if disadvantages_block:
        parts.extend(["", disadvantages_block])
    parts.extend(["", "---"])
    return "\n".join(parts)


def remove_provider(file_path: Path, provider_name: str, dry_run: bool = False) -> Optional[str]:
    """
    Remove a provider block from a markdown file."""
    if not file_path.exists():
        return None
    content = file_path.read_text(encoding="utf-8")
    lines = content.splitlines(keepends=True)
    block_range = _find_provider_block(lines, provider_name)
    if block_range is None:
        return "NOT_FOUND"
    start_idx, end_idx = block_range
    if dry_run:
        return f"WOULD_REMOVE (lines {start_idx + 1}-{end_idx + 1})"

    new_lines = lines[:start_idx] + lines[end_idx + 1:]

    cleaned_lines: List[str] = []
    blank_count = 0
    for line in new_lines:
        if line.strip() == "":
            blank_count += 1
            if blank_count <= 2:
                cleaned_lines.append(line)
        else:
            blank_count = 0
            cleaned_lines.append(line)

    file_path.write_text("".join(cleaned_lines), encoding="utf-8")
    return "REMOVED"


def find_provider_across_files(provider_name: str) -> Optional[Tuple[str, Path]]:
    """Search for a provider in all category markdown files."""
    for category, file_name in CATEGORY_MAP.items():
        file_path = DOCS_DIR / file_name
        if not file_path.exists():
            continue
        content = file_path.read_text(encoding="utf-8")
        lines = content.splitlines(keepends=True)
        if _find_provider_block(lines, provider_name) is not None:
            return (category, file_path)
    return None


def _find_provider_block(
    lines: List[str], provider_name: str
) -> Optional[Tuple[int, int]]:
    start_idx = None

    for i, line in enumerate(lines):
        m = HEADING_RE.match(line.strip())
        if m:
            plain = get_plain_provider_name(m.group(1).strip())
            if plain.lower() == provider_name.lower():
                start_idx = i
                break

    if start_idx is None:
        return None

    for i in range(start_idx + 1, len(lines)):
        if lines[i].strip() == "---":
            return (start_idx, i)

    next_heading_idx = None
    for i in range(start_idx + 1, len(lines)):
        if HEADING_RE.match(lines[i].strip()):
            next_heading_idx = i
            break

    if next_heading_idx is not None:
        return (start_idx, next_heading_idx - 1)

    return (start_idx, len(lines) - 1)


def _find_insertion_point(lines: List[str], provider_name: str) -> int:
    """
    Find the line index where a new provider block should be inserted
    to maintain alphabetical order.
    """

    for i, line in enumerate(lines):
        m = HEADING_RE.match(line.strip())
        if m:
            existing_plain = get_plain_provider_name(m.group(1).strip()).lower()
            new_plain = provider_name.lower()
            if new_plain < existing_plain:
                return i

    return len(lines)


def sync_provider(file_path: Path, entry: Dict[str, Any], dry_run: bool = False) -> str:
    """
    Sync a single provider entry into the markdown file.
    """
    provider_name = entry["name"]
    md_block = generate_provider_markdown(entry)
    content = file_path.read_text(encoding="utf-8")
    lines = content.splitlines(keepends=True)
    block_range = _find_provider_block(lines, provider_name)

    if entry.get("category") == "caution" and block_range is not None:
        return "SKIPPED (caution is manual)"

    if block_range is not None:
        start_idx, end_idx = block_range
        old_block = "".join(lines[start_idx : end_idx + 1])

        if old_block.strip() == md_block.strip():
            return "SKIPPED (no changes)"
        if dry_run:
            return f"WOULD_UPDATE (lines {start_idx + 1}-{end_idx + 1})"
        new_lines = lines[:start_idx] + [md_block + "\n"] + lines[end_idx + 1 :]
        file_path.write_text("".join(new_lines), encoding="utf-8")
        return "UPDATED"

    else:
        first_sep_idx = None
        for i, line in enumerate(lines):
            if line.strip() == "---":
                first_sep_idx = i
                break
        if first_sep_idx is None:
            insert_idx = len(lines)
        else:
            insert_idx = _find_insertion_point(lines[first_sep_idx + 1 :], provider_name)
            insert_idx += first_sep_idx + 1
        if dry_run:
            return f"WOULD_ADD at line {insert_idx + 1}"
        if insert_idx >= len(lines):
            if lines and not lines[-1].endswith("\n"):
                lines[-1] += "\n"
            lines.append(md_block + "\n")
        else:
            lines.insert(insert_idx, md_block + "\n")
        file_path.write_text("".join(lines), encoding="utf-8")
        return "ADDED"


# Markdown extraction for partial-update merge
_MD_LINK_RE = re.compile(r"\[([^\]]*)\]\(([^)]*)\)")
_BACKTICK_RE = re.compile(r"`([^`]+)`")
_ADMONITION_RE = re.compile(r'^!!!\s+(tip|danger)\s+"(.+)"\s*$')
_META_STATUS_RE = re.compile(r"provider-meta__status--(\w+)")
_META_TESTING_RE = re.compile(r"provider-meta__testing--([\w-]+)")
_MODELS_MARKER_RE = re.compile(r"<!--\s*MODELS_START\s*-->")


def _extract_md_link(text: str) -> Optional[str]:
    """Extract URL from a markdown link like [text](url). Returns None if not found."""
    m = _MD_LINK_RE.search(text)
    return m.group(2) if m else None


def _extract_backtick(text: str) -> Optional[str]:
    """Extract content between backticks like `content`. Returns None if not found."""
    m = _BACKTICK_RE.search(text)
    return m.group(1) if m else None


def _find_table_row(lines: List[str], start: int, header: str) -> Optional[int]:
    """Find a table header line starting at `start` and return index of data row (header+2)."""
    for i in range(start, len(lines)):
        if header in lines[i] and lines[i].strip().startswith("|"):
            data_idx = i + 2
            if data_idx < len(lines) and lines[data_idx].strip().startswith("|"):
                return data_idx
    return None


def _split_table_row(line: str) -> List[str]:
    """Split a markdown table row into cell values, stripping leading/trailing whitespace."""
    return [cell.strip() for cell in line.strip().strip("|").split("|")]


def _parse_first_table(
    lines: List[str], start: int
) -> Dict[str, Any]:
    """Parse the Requirements | Limits | Models table."""
    data: Dict[str, Any] = {}
    row_idx = _find_table_row(lines, start, "Requirements")
    if row_idx is None:
        return data

    cells = _split_table_row(lines[row_idx])
    if len(cells) < 3:
        return data

    _, limits_raw, models_raw = cells[0], cells[1], cells[2]

    limits_url = _extract_md_link(limits_raw)
    if limits_url:
        data["limits_url"] = limits_url
        limits_text = _MD_LINK_RE.sub("", limits_raw).strip()
        limits_text = limits_text.replace('<span class="link-icon">', "").replace("</span>", "")
        limits_text = limits_text.replace("[]( )", "").strip()
        limits_text = limits_text.lstrip("<br>").lstrip("<br/>").lstrip("<br />").strip()
        limits_text = limits_text.rstrip("<br>").rstrip("<br/>").rstrip("<br />").strip()
        limits_text = re.sub(r'\s*<svg[^>]*>.*?</svg>\s*', "", limits_text, flags=re.DOTALL).strip()
        if limits_text:
            data["limits"] = limits_text
    else:
        data["limits"] = limits_raw

    models_url = _extract_md_link(models_raw)
    if models_url:
        data["models_url"] = models_url

    data["auto_update_models"] = bool(_MODELS_MARKER_RE.search(models_raw))

    manual_models = []
    for part in re.split(r"<br\s*/?>", models_raw):
        part = part.strip()
        part_no_link = _MD_LINK_RE.sub("", part).strip()
        part_no_link = re.sub(r'\s*<span class="link-icon">.*?</span>\s*', "", part_no_link, flags=re.DOTALL).strip()
        if part_no_link.startswith("•") or part_no_link.startswith("-"):
            item = part_no_link[1:].strip()
            if item:
                manual_models.append(item)
    if manual_models:
        data["manual_models"] = manual_models

    return data


def _parse_links_table(
    lines: List[str], start: int
) -> Dict[str, Any]:
    """Parse the Registration | API key | Base URL table."""
    data: Dict[str, Any] = {}
    row_idx = _find_table_row(lines, start, "Registration")
    if row_idx is None:
        return data

    cells = _split_table_row(lines[row_idx])
    if len(cells) < 3:
        return data

    reg_raw, api_raw, base_raw = cells[0], cells[1], cells[2]

    reg_url = _extract_md_link(reg_raw)
    if reg_url:
        data["registration_url"] = reg_url

    if api_raw and api_raw != "—":
        api_url = _extract_md_link(api_raw)
        if api_url:
            data["api_key_url"] = api_url

    base_url = _extract_backtick(base_raw)
    if base_url:
        data["base_url"] = base_url

    return data


def _parse_heading_badges(
    line: str,
) -> Dict[str, Any]:
    """Parse provider heading to extract service_status and testing_status from badges."""
    data: Dict[str, Any] = {}

    m = _META_STATUS_RE.search(line)
    if m:
        data["service_status"] = m.group(1)

    m = _META_TESTING_RE.search(line)
    if m:
        val = m.group(1)
        if val == "tested":
            data["testing_status"] = "tested"
        elif val == "untested":
            data["testing_status"] = "untested"
        elif val == "in-progress":
            data["testing_status"] = "in-progress"

    return data


def _parse_admonition_blocks(
    lines: List[str], start: int, end: int
) -> Dict[str, Any]:
    """Extract features and disadvantages from admonition blocks (tip/danger)."""
    data: Dict[str, Any] = {}
    current_key: Optional[str] = None
    items: List[str] = []

    for i in range(start, end):
        line = lines[i].strip()
        m = _ADMONITION_RE.match(line)
        if m:
            if current_key and items:
                data[current_key] = items
            admon_type, title = m.group(1), m.group(2)
            if admon_type == "tip" and title == "Features":
                current_key = "features"
            elif admon_type == "danger" and title == "Disadvantages":
                current_key = "disadvantages"
            else:
                current_key = None
            items = []
        elif current_key and line.startswith("-"):
            item_text = line[1:].strip()
            if item_text:
                items.append(item_text)

    if current_key and items:
        data[current_key] = items

    return data


def _get_block_range(
    lines: List[str], provider_name: str
) -> Optional[Tuple[int, int]]:
    """Find the start and end line indices of a provider block."""
    start_idx = None
    for i, line in enumerate(lines):
        m = HEADING_RE.match(line.strip())
        if m:
            plain = get_plain_provider_name(m.group(1).strip())
            if plain.lower() == provider_name.lower():
                start_idx = i
                break
    if start_idx is None:
        return None

    for i in range(start_idx + 1, len(lines)):
        if lines[i].strip() == "---":
            return (start_idx, i)

    next_heading_idx = None
    for i in range(start_idx + 1, len(lines)):
        if HEADING_RE.match(lines[i].strip()):
            next_heading_idx = i
            break

    if next_heading_idx is not None:
        return (start_idx, next_heading_idx - 1)

    return (start_idx, len(lines) - 1)


def extract_existing_provider_data(provider_name: str) -> Optional[Dict[str, Any]]:
    """Extract existing provider data from category markdown files.

    Returns a dict with all extractable fields, or None if provider not found.
    """
    for category, file_name in CATEGORY_MAP.items():
        file_path = DOCS_DIR / file_name
        if not file_path.exists():
            continue
        content = file_path.read_text(encoding="utf-8")
        lines = content.splitlines(keepends=True)

        block_range = _get_block_range(lines, provider_name)
        if block_range is None:
            continue

        start_idx, end_idx = block_range
        data: Dict[str, Any] = {"category": category}
        block_lines = [ln.rstrip("\n").rstrip("\r") for ln in lines[start_idx:end_idx]]
        heading_line = block_lines[0] if block_lines else ""
        data.update(_parse_heading_badges(heading_line))
        data.update(_parse_first_table(block_lines, 0))
        data.update(_parse_links_table(block_lines, 0))
        data.update(_parse_admonition_blocks(block_lines, 0, len(block_lines)))

        return data

    return None


def merge_with_existing(entry: Dict[str, Any]) -> Dict[str, Any]:
    """Merge a partial JSON entry with existing provider data from markdown.

    JSON fields take precedence over existing data.
    """
    provider_name = entry.get("name", "")
    if not provider_name:
        return entry

    existing = extract_existing_provider_data(provider_name)
    if existing is None:
        return entry

    merged = {**existing, **entry}
    return merged


# Main

def load_providers(json_path: Path) -> List[Dict[str, Any]]:
    """Load, merge with existing markdown data, and validate all providers."""
    try:
        data = json.loads(json_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        print(f"[ERROR] Invalid JSON in {json_path}: {e}", file=sys.stderr)
        sys.exit(1)

    if not isinstance(data, list):
        print(
            f"[ERROR] {json_path} must contain a JSON array, got {type(data).__name__}",
            file=sys.stderr,
        )
        sys.exit(1)

    merged_providers = []
    for i, entry in enumerate(data):
        merged = merge_with_existing(entry)
        merged_providers.append(merged)

    for i, entry in enumerate(merged_providers):
        validate_provider(entry, i)
    return merged_providers


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Sync providers from JSON config to markdown files. "
        "Adds new providers, updates existing ones, and moves between categories."
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Preview what would be changed without modifying files.",
    )
    args = parser.parse_args()

    if not PROVIDERS_JSON.exists():
        print(f"[ERROR] {PROVIDERS_JSON} not found", file=sys.stderr)
        sys.exit(1)

    providers = load_providers(PROVIDERS_JSON)
    print(f"Loaded {len(providers)} provider(s) from {PROVIDERS_JSON}")

    any_changes = False

    for entry in providers:
        provider_name = entry["name"]
        target_category = entry["category"]
        target_file_name = CATEGORY_MAP[target_category]
        target_file_path = DOCS_DIR / target_file_name

        if not target_file_path.exists():
            print(f"[ERROR] Target file {target_file_path} does not exist", file=sys.stderr)
            continue

        found = find_provider_across_files(provider_name)
        if found is not None:
            current_category, current_file_path = found
            if current_category != target_category:
                remove_status = remove_provider(
                    current_file_path, provider_name, dry_run=args.dry_run
                )
                if remove_status == "REMOVED":
                    print(f"[MOVE] {provider_name}: {current_category}.md -> {target_file_name}")
                    any_changes = True
                elif remove_status and remove_status.startswith("WOULD_REMOVE"):
                    print(f"[DRY-RUN] {remove_status}: {provider_name} from {current_category}.md")
                    any_changes = True

        status = sync_provider(target_file_path, entry, dry_run=args.dry_run)
        if status == "ADDED":
            print(f"[ADD] {provider_name} -> {target_file_name}")
            any_changes = True
        elif status.startswith("UPDATED"):
            print(f"[UPDATE] {provider_name} -> {target_file_name} ({status})")
            any_changes = True
        elif status.startswith("WOULD_"):
            print(f"[DRY-RUN] {status}: {provider_name} -> {target_file_name}")
            any_changes = True
        else:
            print(f"[SKIP] {provider_name} ({status})")

    if not any_changes:
        print("No changes to apply.")


if __name__ == "__main__":
    main()
