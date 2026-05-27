import re
from html import escape
from typing import Tuple

from constants import (
    PROVIDER_META_TOOLTIPS,
    REQUIREMENT_TOOLTIPS,
    SERVICE_STATUS_TOOLTIPS,
    VALID_SVG_REQUIREMENTS,
    WARNING_TOOLTIP,
)
from icons import SVG_ICONS

TESTING_STATUS_SVG_MAP = {
    "tested": "testing-tested",
    "untested": "testing-untested",
    "in-progress": "testing-in-progress",
}

TESTING_STATUS_CSS_MAP = {
    "tested": "provider-meta__testing--tested",
    "untested": "provider-meta__testing--untested",
    "in-progress": "provider-meta__testing--in-progress",
}


def get_plain_provider_name(provider_name: str) -> str:
    """Strip generated provider meta badges from a provider heading."""
    return re.sub(r'\s*<span class="provider-meta">.*</span>\s*$', "", provider_name).strip()


def get_display_name(model_id: str) -> str:
    """Strip provider prefix from model ID for display.

    Examples:
        openai/gpt-4o        -> gpt-4o
        anthropic/claude-3   -> claude-3
        deepseek-v3          -> deepseek-v3
    """
    if "/" in model_id:
        return model_id.split("/", 1)[1]
    return model_id


def build_tooltip_button(symbol: str, tooltip: str, class_name: str) -> str:
    """Render a tooltip-enabled button for a badge or requirement icon."""
    safe_tooltip = escape(tooltip, quote=True)
    safe_symbol = escape(symbol)
    return (
        f'<button type="button" class="{class_name}" '
        f'data-tooltip="{safe_tooltip}" aria-label="{safe_tooltip}">{safe_symbol}</button>'
    )


def build_tooltip_svg(svg: str, tooltip: str, class_name: str) -> str:
    """Render a tooltip-enabled button containing an inline SVG."""
    safe_tooltip = escape(tooltip, quote=True)
    return (
        f'<button type="button" class="{class_name}" '
        f'data-tooltip="{safe_tooltip}" aria-label="{safe_tooltip}">{svg}</button>'
    )


def render_warning_badge(warning_id: str) -> str:
    """Render a clickable warning badge linking to caution page section."""
    svg = SVG_ICONS.get("warning-caution", "")
    href = f"../caution/#{escape(warning_id, quote=True)}"
    safe_tooltip = escape(WARNING_TOOLTIP, quote=True)
    return (
        f'<a href="{href}" class="provider-meta__item provider-meta__warning" '
        f'data-tooltip="{safe_tooltip}" aria-label="{safe_tooltip}">{svg}</a>'
    )


def render_service_status_badge(status: str) -> str:
    """Render a service status badge with inline SVG and tooltip."""
    if status not in SERVICE_STATUS_TOOLTIPS:
        return ""
    icon_key = f"status-{status}"
    svg = SVG_ICONS.get(icon_key, "")
    tooltip = SERVICE_STATUS_TOOLTIPS[status]
    return build_tooltip_svg(svg, tooltip, f"provider-meta__item provider-meta__status--{status}")


def render_link_icon() -> str:
    """Return an inline SVG globe icon for use in markdown links."""
    return f'<span class="link-icon">{SVG_ICONS["globe"]}</span>'


def render_provider_meta_badges(service_status: str | list[str], testing_cell: str, warning_id: str = "") -> str:
    """Render provider service status and testing badges.
    
    service_status can be a single string or a list of strings.
    When a list, all statuses are rendered as badges.
    """
    badges = []

    if warning_id:
        badges.append(render_warning_badge(warning_id))
    if isinstance(service_status, str):
        service_status = [service_status]
    for status in service_status:
        status_badge = render_service_status_badge(status)
        if status_badge:
            badges.append(status_badge)
    testing_statuses = ("tested", "untested", "in-progress")
    status = next((s for s in testing_statuses if s in testing_cell), "")
    if status:
        svg_key = TESTING_STATUS_SVG_MAP.get(status)
        svg = SVG_ICONS.get(svg_key, "") if svg_key else ""
        css_class = f"provider-meta__item provider-meta__testing {TESTING_STATUS_CSS_MAP.get(status, '')}".strip()
        if svg:
            badges.append(
                build_tooltip_svg(
                    svg,
                    PROVIDER_META_TOOLTIPS[status],
                    css_class,
                )
            )
        else:
            badges.append(
                build_tooltip_button(
                    status,
                    PROVIDER_META_TOOLTIPS[status],
                    css_class,
                )
            )

    if not badges:
        return ""

    return f' <span class="provider-meta">{"".join(badges)}</span>'


def render_requirement_icons(requirements_cell: str, requirements_notes: str = "") -> str:
    """Render requirement SVG keys as tooltip-enabled buttons.

    When *requirements_notes* is non-empty, the ``"special"`` icon
    receives that text as its tooltip instead of the generic fallback.
    """
    if "requirement-icon" in requirements_cell or "requirements-list" in requirements_cell:
        return requirements_cell

    items = []
    for part in re.split(r"<br\s*/?>|\n", requirements_cell):
        item = part.strip()
        if not item:
            continue
        if item in VALID_SVG_REQUIREMENTS:
            svg = SVG_ICONS.get(item, "")
            if item == "special" and requirements_notes:
                tooltip = requirements_notes
            else:
                tooltip = REQUIREMENT_TOOLTIPS.get(item, item)
            items.append(build_tooltip_svg(svg, tooltip, "requirement-icon"))
            continue
        items.append(item)

    if not items:
        return requirements_cell.strip()

    return f'<span class="requirements-list">{"".join(items)}</span>'


def normalize_provider_metadata(
    provider_name: str, section: str, requirements_notes: str = ""
) -> Tuple[str, str]:
    """
    Normalize compact provider markup into interactive HTML badges.
    """
    if "provider-meta" in provider_name or "requirements-list" in section:
        return provider_name, section
    if "requirements-icon" in section:
        return provider_name, section

    lines = section.splitlines()
    header_idx = None
    for i, line in enumerate(lines):
        if re.match(
            r"^\|\s*Requirements\s*\|\s*Limits\s*\|\s*Models\s*\|\s*Testing\s*\|\s*$",
            line.strip(),
        ):
            header_idx = i
            break

    if header_idx is None:
        return provider_name, section

    row_idx = header_idx + 2
    if row_idx >= len(lines):
        return provider_name, section

    row_line = lines[row_idx].strip()
    if not row_line.startswith("|"):
        return provider_name, section

    cells = [cell.strip() for cell in row_line.strip().strip("|").split("|")]
    if len(cells) < 4:
        return provider_name, section

    requirements_cell, limits_cell, models_cell, testing_cell = cells[:4]
    requirements_html = render_requirement_icons(requirements_cell, requirements_notes)
    provider_meta_html = render_provider_meta_badges("", testing_cell)
    plain_provider_name = get_plain_provider_name(provider_name)
    updated_provider_name = plain_provider_name + provider_meta_html if provider_meta_html else provider_name

    new_lines = []
    new_lines.extend(lines[:header_idx])
    new_lines.append("| Requirements | Limits | Models |")
    new_lines.append("|:---|:---:|:---:|")
    new_lines.append(f"| {requirements_html} | {limits_cell} | {models_cell} |")
    new_lines.extend(lines[row_idx + 1 :])

    return updated_provider_name, "\n".join(new_lines)
