import re
import subprocess
from datetime import datetime
from pathlib import Path
from rich.console import Console
from typing import Dict, List, Set, Tuple

from constants import (
    CATEGORY_MAP,
    CHANGELOG_PATH,
    INDEX_PATH,
)
from provider_meta import get_plain_provider_name

console = Console()


def get_git_diff(file_path: str) -> Tuple[str, str]:
    """Get old and new content of a file from git."""
    try:
        old_content = subprocess.run(
            ["git", "show", f"HEAD:{file_path}"],
            capture_output=True,
            text=True,
            check=False
        ).stdout
        
        new_content = Path(file_path).read_text(encoding="utf-8")
        
        return old_content, new_content
    except Exception as e:
        console.print(f"[bold yellow]WARN[/] Could not get git diff for {file_path}: {e}")
        return "", Path(file_path).read_text(encoding="utf-8")


def extract_providers(content: str) -> Set[str]:
    """Extract provider names from markdown headers (### Provider Name)."""
    providers = set()
    pattern = r'^###\s+(.+?)$'
    
    for match in re.finditer(pattern, content, re.MULTILINE):
        provider_name = match.group(1).strip()
        provider_name = get_plain_provider_name(provider_name)
        if provider_name and provider_name.lower() not in ['features', 'disadvantages', 'notes']:
            providers.add(provider_name)
    
    return providers


def detect_changes() -> Dict[str, List[str]]:
    """Detect provider additions, deletions, and moves across categories via git diff."""
    changes = {
        "added": [],
        "removed": [],
        "moved": []
    }
    
    old_providers: Dict[str, Set[str]] = {}
    new_providers: Dict[str, Set[str]] = {}
    
    for category_key, filename in CATEGORY_MAP.items():
        if category_key == "caution":
            continue
        git_path = f"docs/{filename}"
        display_name = category_key.capitalize()
        old_content, new_content = get_git_diff(git_path)
        old_providers[display_name] = extract_providers(old_content)
        new_providers[display_name] = extract_providers(new_content)
    
    all_old = {p for providers in old_providers.values() for p in providers}
    all_new = {p for providers in new_providers.values() for p in providers}
    
    for category, providers in new_providers.items():
        for provider in providers:
            if provider not in all_old:
                changes["added"].append(f"**{provider}** to *{category}*")
    
    for category, providers in old_providers.items():
        for provider in providers:
            if provider not in all_new:
                changes["removed"].append(f"**{provider}** from *{category}*")
    
    for provider in all_old & all_new:
        old_cat = next((cat for cat, provs in old_providers.items() if provider in provs), None)
        new_cat = next((cat for cat, provs in new_providers.items() if provider in provs), None)
        
        if old_cat and new_cat and old_cat != new_cat:
            changes["moved"].append(f"**{provider}** from *{old_cat}* to *{new_cat}*")
    
    return changes


def format_changelog_entry(changes: Dict[str, List[str]], date: str) -> str:
    """Format changes into a changelog entry."""
    if not any(changes.values()):
        return ""
    
    lines = [f"### {date}\n"]
    
    if changes["added"]:
        for item in changes["added"]:
            lines.append(f"- Added {item}")
    
    if changes["moved"]:
        for item in changes["moved"]:
            lines.append(f"- Moved {item}")
    
    if changes["removed"]:
        for item in changes["removed"]:
            lines.append(f"- Removed {item}")
    
    lines.append("")
    return "\n".join(lines)


def _parse_changelog_date(entry_str: str) -> str:
    """Extract ISO date (YYYY-MM-DD) from a changelog entry line."""
    match = re.match(r"^###\s+(\d{4}-\d{2}-\d{2})", entry_str)
    return match.group(1) if match else ""


def _sort_changelog_entries(entries: list[str]) -> list[str]:
    """Sort changelog entries in reverse chronological order (newest first)."""
    return sorted(entries, key=_parse_changelog_date, reverse=True)


def update_changelog(entry: str):
    """Update or create changelog.md with new entry."""
    if not entry:
        console.print("[bold]No changes detected, skipping changelog update.[/]")
        return

    today = datetime.now().strftime("%Y-%m-%d")

    if CHANGELOG_PATH.exists():
        content = CHANGELOG_PATH.read_text(encoding="utf-8")
        entries = re.split(r"^### ", content, flags=re.MULTILINE)
        header = entries[0]
        rest = ["### " + e for e in entries[1:]]

        if any(e.startswith(today) for e in rest):
            entry_items = [line for line in entry.split("\n")[1:] if line.strip() and not line.startswith("###")]
            rest = [
                (e + "\n" + "\n".join(entry_items)) if e.startswith(today) else e
                for e in rest
            ]
            new_content = header + "".join(rest)
            console.print(f"[bold green]OK[/] Added new items to existing {today} entry in changelog.")
        else:
            rest = _sort_changelog_entries(rest)
            new_content = header + entry + "".join(rest)
            console.print(f"[bold green]OK[/] Added new {today} entry at the top of changelog.")
    else:
        new_content = "# Changelog\n\n"
        new_content += "!!! info \"About\"\n"
        new_content += "    This page tracks all provider additions, removals, and category changes.\n\n"
        new_content += "---\n\n"
        new_content += entry

    CHANGELOG_PATH.write_text(new_content, encoding="utf-8")
    console.print(f"[bold green]OK[/] Updated {CHANGELOG_PATH}")


def update_index_latest_updates():
    """Update index.md with latest 3 updates from changelog."""
    if not CHANGELOG_PATH.exists():
        console.print("[bold yellow]WARN[/] Changelog doesn't exist yet, skipping index update.")
        return
    
    changelog_content = CHANGELOG_PATH.read_text(encoding="utf-8")
    entries = []
    current_date = None
    current_items = []
    
    for line in changelog_content.split("\n"):
        if line.startswith("### "):
            if current_date and current_items:
                entries.append((current_date, current_items))
            current_date = line.replace("### ", "").strip()
            current_items = []
        elif line.startswith("- ") and current_date:
            current_items.append(line[2:])
    if current_date and current_items:
        entries.append((current_date, current_items))
    latest_entries = entries[:3]
    
    if not latest_entries:
        console.print("[bold yellow]WARN[/] No entries found in changelog.")
        return
    updates_section = "## Latest Updates\n\n"
    
    for date, items in latest_entries:
        for item in items:
            updates_section += f"* **{date}** — {item}\n"
    
    updates_section += "\n[View all updates](changelog.md)\n\n"
    
    if not INDEX_PATH.exists():
        console.print(f"[bold yellow]WARN[/] {INDEX_PATH} does not exist, skipping index update.")
        return
        
    index_content = INDEX_PATH.read_text(encoding="utf-8")
    categories_pos = index_content.find("## Categories")
    
    if categories_pos == -1:
        console.print("[bold yellow]WARN[/] Could not find '## Categories' in index.md — appending updates to end")
        new_content = index_content.rstrip() + "\n\n" + updates_section
    elif "## Latest Updates" in index_content:
        start = index_content.find("## Latest Updates")
        end = index_content.find("## Categories", start)
        if end != -1:
            new_content = index_content[:start].rstrip() + "\n\n" + updates_section + index_content[end:]
        else:
            console.print("[bold yellow]WARN[/] Could not find end of Latest Updates section")
            return
    else:
        new_content = index_content[:categories_pos].rstrip() + "\n\n" + updates_section + index_content[categories_pos:]
    
    INDEX_PATH.write_text(new_content, encoding="utf-8")
    console.print(f"[bold green]OK[/] Updated {INDEX_PATH} with latest updates.")


def main():
    console.print("[bold]Tracking provider changes...[/]")
    changes = detect_changes()
    today = datetime.now().strftime("%Y-%m-%d")
    entry = format_changelog_entry(changes, today)
    update_changelog(entry)
    update_index_latest_updates()
    console.print("[bold green]OK[/] Done!")


if __name__ == "__main__":
    main()
