#!/usr/bin/env python3
"""
Create version tag based on conventional commits since last release.

Conventional commit rules:
- fix: -> patch bump (1.0.0 -> 1.0.1)
- feat: -> minor bump (1.0.0 -> 1.1.0)
- BREAKING CHANGE or feat!:/fix!: -> major bump (1.0.0 -> 2.0.0)

This script creates git tags; version is derived from tags during build.
"""

import re
import subprocess
import sys


def run_command(cmd: list[str]) -> str:
    """Run a shell command and return output."""
    result = subprocess.run(cmd, capture_output=True, text=True, check=False)
    return result.stdout.strip()


def get_last_tag() -> str | None:
    """Get the most recent git tag, or None if no tags exist."""
    tags = run_command(["git", "tag", "--sort=-v:refname"])
    if not tags:
        return None
    return tags.split("\n")[0]


def get_commits_since(ref: str | None) -> list[str]:
    """Get commit messages since the given ref (or all if ref is None)."""
    if ref:
        commit_range = f"{ref}..HEAD"
    else:
        commit_range = "HEAD"

    commits = run_command(["git", "log", commit_range, "--pretty=format:%s"])
    if not commits:
        return []
    return commits.split("\n")


def determine_bump_type(commits: list[str]) -> str:
    """
    Determine version bump type from conventional commits.

    Returns: "major", "minor", "patch", or "none"
    """
    has_breaking = False
    has_feat = False
    has_fix = False

    for commit in commits:
        commit_lower = commit.lower()

        # Check for breaking changes
        if "breaking change" in commit_lower or re.match(r"^(feat|fix)!:", commit_lower):
            has_breaking = True
            break

        # Check for features
        if commit_lower.startswith("feat:") or commit_lower.startswith("feat("):
            has_feat = True

        # Check for fixes
        if commit_lower.startswith("fix:") or commit_lower.startswith("fix("):
            has_fix = True

    if has_breaking:
        return "major"
    if has_feat:
        return "minor"
    if has_fix:
        return "patch"
    return "none"


def parse_version(version_str: str) -> tuple[int, int, int]:
    """Parse semantic version string into tuple (strips leading 'v' if present)."""
    # Remove leading 'v' if present
    version_str = version_str.lstrip('v')
    match = re.match(r"(\d+)\.(\d+)\.(\d+)", version_str)
    if not match:
        raise ValueError(f"Invalid version format: {version_str}")
    return int(match.group(1)), int(match.group(2)), int(match.group(3))


def bump_version(version: str, bump_type: str) -> str:
    """Bump version according to bump type."""
    major, minor, patch = parse_version(version)

    if bump_type == "major":
        return f"{major + 1}.0.0"
    elif bump_type == "minor":
        return f"{major}.{minor + 1}.0"
    elif bump_type == "patch":
        return f"{major}.{minor}.{patch + 1}"
    else:
        return version


def create_tag(tag_name: str, message: str) -> bool:
    """Create an annotated git tag."""
    result = subprocess.run(
        ["git", "tag", "-a", tag_name, "-m", message],
        capture_output=True,
        text=True,
        check=False
    )
    return result.returncode == 0


def main() -> int:
    """Main entry point."""
    try:
        # Get last tag
        last_tag = get_last_tag()

        if last_tag:
            print(f"Last release tag: {last_tag}")
            current_version = last_tag
        else:
            print("No previous tags found, will start from v1.0.0")
            current_version = "v1.0.0"

        # Get commits since last tag
        commits = get_commits_since(last_tag)

        if not commits:
            print("No new commits since last release")
            clean_version = current_version.lstrip('v')
            print(f"Current version: {clean_version}")
            print(f"version={clean_version}")
            print(f"bumped=false")
            print(f"tag={current_version}")
            return 0

        print(f"\nAnalyzing {len(commits)} commits:")
        for commit in commits[:10]:  # Show first 10
            print(f"  - {commit}")
        if len(commits) > 10:
            print(f"  ... and {len(commits) - 10} more")

        # Determine bump type
        bump_type = determine_bump_type(commits)
        print(f"\nBump type: {bump_type}")

        if bump_type == "none":
            print("No version bump needed (no conventional commits found)")
            clean_version = current_version.lstrip('v')
            print(f"Current version: {clean_version}")
            print(f"version={clean_version}")
            print(f"bumped=false")
            print(f"tag={current_version}")
            return 0

        # Calculate new version
        new_version = bump_version(current_version, bump_type)
        new_tag = f"v{new_version}"

        print(f"\nVersion bump: {current_version} -> {new_tag}")

        # Create git tag
        tag_message = f"Release {new_tag} ({bump_type} bump)"
        if create_tag(new_tag, tag_message):
            print(f"✓ Created tag {new_tag}")
        else:
            print(f"✗ Failed to create tag {new_tag}", file=sys.stderr)
            return 1

        # Output for GitHub Actions (no ::set-output, just plain output to parse)
        print(f"version={new_version}")
        print(f"bumped=true")
        print(f"bump_type={bump_type}")
        print(f"tag={new_tag}")

        return 0

    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
