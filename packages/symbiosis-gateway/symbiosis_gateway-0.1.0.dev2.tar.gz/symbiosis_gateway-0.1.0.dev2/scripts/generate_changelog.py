#!/usr/bin/env python3
"""Generate CHANGELOG.md for a release."""

import re
import subprocess
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path


def run_git_command(args: list[str]) -> str:
    """Run a git command and return its output."""
    result = subprocess.run(  # noqa: S603
        ["git"] + args,
        capture_output=True,
        text=True,
        check=True,
    )
    return result.stdout.strip()


def get_tags() -> list[str]:
    """Return all tags sorted descending by version refname (latest first)."""
    try:
        tags = run_git_command(["tag", "--sort=-version:refname"]).split("\n")
        return [t for t in tags if t]
    except subprocess.CalledProcessError:
        return []


def resolve_tag_commit(tag: str) -> str:
    """Return the commit hash a tag points to."""
    return run_git_command(["rev-list", "-n", "1", tag])


def determine_commit_range() -> tuple[str | None, str | None, str]:
    """Determine (previous_tag, latest_tag, commit_range) for the changelog.

    Logic:
      - No tags: (None, None, "HEAD")
      - >=1 tag and HEAD == latest tag commit:
           * If previous tag exists: range previous..latest
           * Else: range latest (all history up to that tag)
      - >=1 tag and HEAD != latest tag commit: range latest..HEAD
    """
    tags = get_tags()
    if not tags:
        return None, None, "HEAD"

    latest = tags[0]
    previous = tags[1] if len(tags) > 1 else None

    head = run_git_command(["rev-parse", "HEAD"])  # current commit hash
    latest_hash = resolve_tag_commit(latest)

    if head == latest_hash:
        if previous:
            return previous, latest, f"{previous}..{latest}"
        # Only one tag; using just the tag as range includes all its reachable commits
        return None, latest, latest
    # Not at a tag; treat as unreleased changes since latest
    return latest, None, f"{latest}..HEAD"


def get_commits_for_range(commit_range: str) -> list[dict[str, str]]:
    """Get commits for a given range or single ref."""
    args = ["log", commit_range, "--format=%H|||%s|||%b|||%an|||%aI"]
    try:
        log_output = run_git_command(args)
        if not log_output:
            return []
        commits: list[dict[str, str]] = []
        for line in log_output.split("\n"):
            if not line:
                continue
            parts = line.split("|||")
            if len(parts) >= 5:
                commits.append(
                    {
                        "hash": parts[0],
                        "subject": parts[1],
                        "body": parts[2],
                        "author": parts[3],
                        "date": parts[4],
                    }
                )
        return commits
    except subprocess.CalledProcessError:
        return []


def parse_conventional_commit(commit: dict[str, str]) -> dict[str, str]:
    """Parse a conventional commit message."""
    # Pattern: type(scope)!?: subject
    # The ! indicates a breaking change
    pattern = r"^(\w+)(?:\(([^)]+)\))?(!)?: (.+)$"
    match = re.match(pattern, commit["subject"])

    if match:
        commit_type = match.group(1)
        scope = match.group(2) or ""
        breaking = match.group(3) == "!"
        description = match.group(4)

        # Check body for BREAKING CHANGE
        if not breaking and commit["body"]:
            breaking = "BREAKING CHANGE" in commit["body"]

        return {
            "type": commit_type,
            "scope": scope,
            "description": description,
            "breaking": breaking,
            "hash": commit["hash"][:7],
            "author": commit["author"],
        }

    # If it doesn't match conventional commit format, categorize as "other"
    return {
        "type": "other",
        "scope": "",
        "description": commit["subject"],
        "breaking": False,
        "hash": commit["hash"][:7],
        "author": commit["author"],
    }


def group_commits_by_type(
    commits: list[dict[str, str]],
) -> dict[str, list[dict[str, str]]]:
    """Group commits by their type."""
    grouped = defaultdict(list)

    for commit in commits:
        parsed = parse_conventional_commit(commit)
        grouped[parsed["type"]].append(parsed)

    return dict(grouped)


def format_commit_entry(commit: dict[str, str]) -> str:
    """Format a single commit entry for the changelog."""
    scope_text = f"**{commit['scope']}**: " if commit["scope"] else ""
    breaking_text = " **BREAKING CHANGE**" if commit["breaking"] else ""
    return f"- {scope_text}{commit['description']}{breaking_text} ({commit['hash']})"


def generate_changelog(
    grouped_commits: dict[str, list[dict[str, str]]],
    previous_tag: str | None,
    latest_tag: str | None,
) -> str:
    """Generate the changelog markdown content."""
    # Type labels and their order
    type_labels = {
        "feat": "✨ Features",
        "fix": "🐛 Bug Fixes",
        "docs": "📚 Documentation",
        "style": "💅 Styles",
        "refactor": "♻️ Code Refactoring",
        "perf": "⚡ Performance Improvements",
        "test": "✅ Tests",
        "build": "📦 Build System",
        "ci": "👷 Continuous Integration",
        "chore": "🔧 Chores",
        "revert": "⏪ Reverts",
        "other": "📝 Other Changes",
    }

    # Determine version info
    if latest_tag and previous_tag:
        version_text = f"Release {latest_tag} (since {previous_tag})"
    elif latest_tag and not previous_tag:
        version_text = f"Release {latest_tag}"
    elif previous_tag and not latest_tag:
        version_text = f"Unreleased changes since {previous_tag}"
    else:
        version_text = "All changes"

    # Build changelog
    lines = [
        "# Changelog",
        "",
        f"## {version_text}",
        "",
        f"*Generated on {datetime.now(timezone.utc).strftime('%Y-%m-%d')}*",
        "",
    ]

    # Check for breaking changes first
    breaking_changes = []

    for commits in grouped_commits.values():
        breaking_changes.extend([c for c in commits if c["breaking"]])

    if breaking_changes:
        lines.extend(
            [
                "### ⚠️ BREAKING CHANGES",
                "",
            ]
        )
        for commit in breaking_changes:
            lines.append(format_commit_entry(commit))
        lines.append("")

    # Add sections for each commit type
    for commit_type, label in type_labels.items():
        if commit_type in grouped_commits:
            commits = grouped_commits[commit_type]
            lines.extend(
                [
                    f"### {label}",
                    "",
                ]
            )
            for commit in commits:
                lines.append(format_commit_entry(commit))
            lines.append("")

    return "\n".join(lines)


def filter_commits(commits: list[dict[str, str]]) -> list[dict[str, str]]:
    """Filter out commits that should not be included in the changelog."""
    filtered = []
    for commit in commits:
        parsed = parse_conventional_commit(commit)
        # Exclude chore and style commits from changelog
        if parsed["type"] not in ["chore", "style", "other"]:
            filtered.append(commit)

    return filtered


def main() -> None:
    """Generate the changelog."""
    print("🔍 Generating changelog...")

    previous_tag, latest_tag, commit_range = determine_commit_range()
    if latest_tag and previous_tag:
        print(
            f"📌 Release context: latest tag {latest_tag}, previous tag {previous_tag}"
        )
    elif latest_tag and not previous_tag:
        print(f"📌 Single tag context: {latest_tag} (first release)")
    elif previous_tag and not latest_tag:
        print(f"📌 Unreleased changes since {previous_tag}")
    else:
        print("⚠️  No tags found, including all commits")

    print(f"🔁 Using commit range: {commit_range}")

    commits = get_commits_for_range(commit_range)

    if not commits:
        print("ℹ️  No commits found since the last tag")
        return

    # Filter unwanted commits
    filtered_commits = filter_commits(commits)

    print(f"📝 Found {len(filtered_commits)} commit(s)")

    # Group commits by type
    grouped_commits = group_commits_by_type(filtered_commits)

    # Generate changelog content
    changelog_content = generate_changelog(grouped_commits, previous_tag, latest_tag)

    # Write to CHANGELOG.md
    changelog_path = Path("CHANGELOG.md")
    changelog_path.write_text(changelog_content)

    print(f"✅ Changelog generated: {changelog_path.absolute()}")


if __name__ == "__main__":
    main()
