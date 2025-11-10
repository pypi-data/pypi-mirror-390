#!/usr/bin/env python3
"""Release script for creating new versions of a python package.

This script:
- Validates that you're on the main branch
- Increments the version number (major/minor/patch)
- Updates pyproject.toml
- Updates pixi.lock
- Creates a git tag
- Pushes the tag to remote
- Provides instructions for creating a GitHub release
"""

from __future__ import annotations

import argparse
import re
import subprocess
import sys
from pathlib import Path


class ReleaseError(Exception):
    """Custom exception for release-related errors."""


def get_current_branch() -> str:
    """Get the current git branch name.

    Returns:
        Current branch name as a string

    Raises:
        ReleaseError: If unable to determine current branch

    """
    try:
        result = subprocess.run(
            ['git', 'rev-parse', '--abbrev-ref', 'HEAD'],
            capture_output=True,
            text=True,
            check=True,
        )
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        msg = f'Failed to get current branch: {e}'
        raise ReleaseError(msg) from e


def check_branch_is_main() -> None:
    """Verify that the current branch is 'main'.

    Raises:
        ReleaseError: If not on main branch

    """
    current_branch = get_current_branch()
    if current_branch != 'main':
        msg = (
            f'❌ Error: Must be on "main" branch to create a release.\n'
            f'   Current branch: "{current_branch}"\n'
            f'   Please switch to main: git checkout main'
        )
        raise ReleaseError(msg)
    print(f'✓ On main branch: {current_branch}')


def check_working_directory_clean() -> None:
    """Verify that the working directory has no uncommitted changes.

    Raises:
        ReleaseError: If there are uncommitted changes

    """
    try:
        result = subprocess.run(
            ['git', 'status', '--porcelain'],
            capture_output=True,
            text=True,
            check=True,
        )
        if result.stdout.strip():
            msg = (
                '❌ Error: Working directory has uncommitted changes.\n'
                '   Please commit or stash changes before releasing.\n'
                f'---- Git status output ----\n{result.stdout.strip()}'
            )
            raise ReleaseError(msg)
        print('✓ Working directory is clean')
    except subprocess.CalledProcessError as e:
        msg = f'Failed to check git status: {e}'
        raise ReleaseError(msg) from e


def get_current_version() -> str:
    """Read the current version from pyproject.toml.

    Returns:
        Current version string (e.g., '0.1.0')

    Raises:
        ReleaseError: If version cannot be found or parsed

    """
    pyproject_path = Path('pyproject.toml')
    if not pyproject_path.exists():
        msg = 'pyproject.toml not found in current directory'
        raise ReleaseError(msg)

    content = pyproject_path.read_text()
    # Match version = "x.y.z" in the [project] section
    match = re.search(
        r'^version\s*=\s*["\']([^"\']+)["\']', content, re.MULTILINE
    )
    if not match:
        msg = 'Could not find version in pyproject.toml'
        raise ReleaseError(msg)

    return match.group(1)


def parse_version(version: str) -> tuple[int, int, int]:
    """Parse a semantic version string into components.

    Args:
        version: Version string (e.g., '0.1.0')

    Returns:
        Tuple of (major, minor, patch)

    Raises:
        ReleaseError: If version format is invalid

    """
    match = re.match(r'^(\d+)\.(\d+)\.(\d+)$', version)
    if not match:
        msg = f'Invalid version format: {version}'
        raise ReleaseError(msg)

    return int(match.group(1)), int(match.group(2)), int(match.group(3))


def increment_version(version: str, part: str = 'patch') -> str:
    """Increment a version number.

    Args:
        version: Current version string (e.g., '0.1.0')
        part: Which part to increment ('major', 'minor', or 'patch')

    Returns:
        New version string

    Raises:
        ReleaseError: If part is invalid

    """
    major, minor, patch = parse_version(version)

    if part == 'major':
        major += 1
        minor = 0
        patch = 0
    elif part == 'minor':
        minor += 1
        patch = 0
    elif part == 'patch':
        patch += 1
    else:
        msg = f'Invalid part: {part}. Must be major, minor, or patch'
        raise ReleaseError(msg)

    return f'{major}.{minor}.{patch}'


def update_version_in_pyproject(new_version: str) -> None:
    """Update the version in pyproject.toml.

    Args:
        new_version: New version string to write

    """
    pyproject_path = Path('pyproject.toml')
    content = pyproject_path.read_text()

    # Replace the version line
    updated_content = re.sub(
        r'^(version\s*=\s*["\'])[^"\']+(["\'])',
        rf'\g<1>{new_version}\g<2>',
        content,
        count=1,
        flags=re.MULTILINE,
    )

    pyproject_path.write_text(updated_content)
    print(f'✓ Updated pyproject.toml to version {new_version}')


def update_pixi_lock() -> str:
    """Update pixi.lock file to reflect changes in pyproject.toml.

    Returns:
        Command that was executed

    Raises:
        ReleaseError: If pixi update fails

    """
    try:
        print('🔄 Updating pixi.lock...', end=' ', flush=True)
        subprocess.run(
            ['pixi', 'update'], capture_output=True, text=True, check=True
        )
    except subprocess.CalledProcessError as e:
        msg = f'Failed to update pixi.lock: {e}'
        raise ReleaseError(msg) from e
    else:
        print('done')
        return 'pixi update'


def create_git_tag(version: str) -> list[str]:
    """Create a git tag for the new version.

    Args:
        version: Version string for the tag

    Returns:
        List of git commands that were executed

    """
    tag_name = f'v{version}'
    commands_executed = []

    # Add pyproject.toml and pixi.lock
    cmd = ['git', 'add', 'pyproject.toml', 'pixi.lock']
    subprocess.run(cmd, capture_output=True, text=True, check=True)
    commands_executed.append(' '.join(cmd))

    # Commit the version change
    cmd = ['git', 'commit', '-m', f'Bump version to {version}']
    subprocess.run(cmd, capture_output=True, text=True, check=True)
    commands_executed.append(' '.join(cmd))

    # Create annotated tag
    cmd = ['git', 'tag', '-a', tag_name, '-m', f'Release version {version}']
    subprocess.run(cmd, capture_output=True, text=True, check=True)
    commands_executed.append(' '.join(cmd))

    print(f'✓ Created git tag: {tag_name}')
    return commands_executed


def push_tag_to_remote(version: str) -> list[str]:
    """Push the commit and tag to remote repository.

    Args:
        version: Version string

    Returns:
        List of git commands that were executed

    """
    tag_name = f'v{version}'
    commands_executed = []

    # Push the commit
    cmd = ['git', 'push', 'origin', 'main']
    subprocess.run(cmd, capture_output=True, text=True, check=True)
    commands_executed.append(' '.join(cmd))

    # Push the tag
    cmd = ['git', 'push', 'origin', tag_name]
    subprocess.run(cmd, capture_output=True, text=True, check=True)
    commands_executed.append(' '.join(cmd))

    print('✓ Pushed commit and tag to remote')
    return commands_executed


def get_previous_tag() -> str | None:
    """Get the most recent git tag (previous release version).

    Returns:
        Previous tag name (e.g., 'v0.2.1') or None if no tags exist

    """
    try:
        result = subprocess.run(
            ['git', 'tag', '--sort=-version:refname'],
            capture_output=True,
            text=True,
            check=True,
        )
        tags = result.stdout.strip().split('\n')
        # Return the first tag (most recent) if any exist
        return tags[0] if tags and tags[0] else None
    except subprocess.CalledProcessError:
        return None


def get_commits_since_tag(tag: str | None) -> list[str]:
    """Get commit titles since the specified tag.

    Args:
        tag: Git tag to compare from (e.g., 'v0.2.1'), or None for all commits

    Returns:
        List of commit titles (one-line summaries)

    """
    try:
        # If no tag, get all commits from HEAD
        range_spec = f'{tag}..HEAD' if tag else 'HEAD'
        result = subprocess.run(
            ['git', 'log', range_spec, '--oneline', '--no-decorate'],
            capture_output=True,
            text=True,
            check=True,
        )
        commits = result.stdout.strip().split('\n')
        # Filter out empty strings and return
        return [c for c in commits if c]
    except subprocess.CalledProcessError:
        return []


def show_commits_since_last_release() -> None:
    """Display commits since the last git tag (release)."""
    previous_tag = get_previous_tag()
    commits = get_commits_since_tag(previous_tag)
    print('\nCommits since last release:')
    if previous_tag:
        print(f'(since tag: {previous_tag})\n')
    else:
        print('(no previous tags found)\n')
    if commits:
        for commit in commits:
            print(f'  • {commit}')
    else:
        print('  (No new commits)')


def get_github_repo_url() -> str | None:
    """Get the GitHub repository URL from git remote.

    Returns:
        GitHub repo URL or None if not found

    """
    try:
        result = subprocess.run(
            ['git', 'remote', 'get-url', 'origin'],
            capture_output=True,
            text=True,
            check=True,
        )
        remote_url = result.stdout.strip()

        # Convert SSH URL to HTTPS
        if remote_url.startswith('ssh://git@github.com'):
            remote_url = remote_url.replace(
                'ssh://git@github.com', 'https://github.com'
            )

        # Remove .git suffix
        return remote_url.removesuffix('.git')

    except subprocess.CalledProcessError:
        return None


def print_summary(
    old_version: str, new_version: str, commands: list[str], *, dry_run: bool
) -> None:
    """Print a summary of the release process.

    Args:
        old_version: Previous version string
        new_version: New version string
        commands: List of git commands that were executed
        dry_run: Whether this was a dry run

    """
    print('\n' + '=' * 70)
    print('📦 RELEASE SUMMARY')
    print('=' * 70)
    print(f'Old version: {old_version}')
    print(f'New version: {new_version}')

    if dry_run:
        print('\n⚠️  DRY RUN MODE - No changes were made')
    else:
        print('\n✓ Release completed successfully!')

    print(f'\nGit commands {"that would be" if dry_run else ""} executed:')
    for cmd in commands:
        print(f'  $ {cmd}')

    # GitHub release instructions
    repo_url = get_github_repo_url()
    print('\n' + '=' * 70)
    print('📝 NEXT STEPS: Create GitHub Release')
    print('=' * 70)

    if repo_url:
        release_url = f'{repo_url}/releases/new?tag=v{new_version}'
        print(f'\n1. Visit: {release_url}')
    else:
        print('\n1. Go to your GitHub repository')
        print('2. Navigate to: Releases → Draft a new release')
        print(f'3. Choose tag: v{new_version}')

    print('\n2. Fill in the release details:')
    print(f'   - Release title: v{new_version}')
    print(
        '   - Description: Add release notes '
        '(what changed, new features, fixes)'
    )
    print('\n3. Click "Publish release"')
    print('\n' + '=' * 70)


def main() -> None:
    """Execute the release process."""
    parser = argparse.ArgumentParser(
        description='Create a new release version',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python release_new_version.py             # Increment patch (0.1.0 → 0.1.1)
  python release_new_version.py --minor     # Increment minor (0.1.0 → 0.2.0)
  python release_new_version.py --major     # Increment major (0.1.0 → 1.0.0)
  python release_new_version.py --dry-run   # Preview changes without executing
        """,
    )

    parser.set_defaults(part='patch')
    group = parser.add_mutually_exclusive_group()
    group.add_argument(
        '--major',
        action='store_const',
        const='major',
        dest='part',
        help='Increment major version (X.0.0)',
    )
    group.add_argument(
        '--minor',
        action='store_const',
        const='minor',
        dest='part',
        help='Increment minor version (x.Y.0)',
    )
    group.add_argument(
        '--patch',
        action='store_const',
        const='patch',
        dest='part',
        help='Increment patch version (x.y.Z) [default]',
    )

    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Show what would be done without making changes',
    )

    args = parser.parse_args()

    try:
        # Validation checks
        print('🔍 Running pre-release checks...\n')
        check_branch_is_main()
        check_working_directory_clean()

        # Get and increment version
        old_version = get_current_version()
        new_version = increment_version(old_version, args.part)

        # Show commits since previous release
        print('\n' + '=' * 70)
        show_commits_since_last_release()
        print('=' * 70)

        print(
            f'\n📊 Version increment: {old_version} → {new_version} '
            f'({args.part})'
        )

        if args.dry_run:
            print('\n⚠️  DRY RUN MODE - No changes will be made')
            commands = [
                'pixi update',
                'git add pyproject.toml pixi.lock',
                f'git commit -m "Bump version to {new_version}"',
                f'git tag -a v{new_version} -m "Release version {new_version}"',  # noqa: E501
                'git push origin main',
                f'git push origin v{new_version}',
            ]
            print_summary(old_version, new_version, commands, dry_run=True)
            return sys.exit(0)

        # Confirm with user
        print('\n⚠️  This will:')
        print(f'   1. Update pyproject.toml to version {new_version}')
        print('   2. Update pixi.lock')
        print('   3. Commit the changes')
        print(f'   4. Create tag v{new_version}')
        print('   5. Push to remote')

        response = input('\nProceed? [y/N]: ')
        if response.lower() not in ('y', 'yes'):
            print('❌ Release cancelled')
            return sys.exit(1)

        # Execute release steps
        print('\n🚀 Creating release...\n')
        update_version_in_pyproject(new_version)
        commands = []
        pixi_cmd = update_pixi_lock()
        commands.append(pixi_cmd)
        commands.extend(create_git_tag(new_version))
        commands.extend(push_tag_to_remote(new_version))

        # Print summary
        print_summary(old_version, new_version, commands, dry_run=False)

        return sys.exit(0)

    except ReleaseError as e:
        print(f'\n{e}', file=sys.stderr)
        return sys.exit(1)
    except KeyboardInterrupt:
        print('\n\n❌ Release cancelled by user', file=sys.stderr)
        return sys.exit(1)
    except (OSError, subprocess.SubprocessError) as e:
        print(f'\n❌ Unexpected error: {e}', file=sys.stderr)
        return sys.exit(1)


if __name__ == '__main__':
    main()
