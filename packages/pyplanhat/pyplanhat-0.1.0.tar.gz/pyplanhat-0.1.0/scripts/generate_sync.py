#!/usr/bin/env python3
"""Generate synchronous code from async source using unasync."""

import sys
from pathlib import Path

import unasync


def collect_python_files(directory: Path) -> list[str]:
    """Collect all Python files in a directory recursively."""
    if not directory.exists():
        return []
    return [str(f) for f in directory.rglob("*.py")]


def remove_async_markers(directory: Path) -> None:
    """Remove @pytest.mark.asyncio decorators from sync test files."""
    if not directory.exists():
        return

    for filepath in directory.rglob("*.py"):
        content = filepath.read_text()
        # Remove @pytest.mark.asyncio decorator lines
        lines = content.split("\n")
        filtered_lines = [line for line in lines if "@pytest.mark.asyncio" not in line]
        filepath.write_text("\n".join(filtered_lines))


def main() -> None:
    """Run unasync to generate sync code from async source."""
    project_root = Path(__file__).parent.parent

    # Define source and destination directories
    src_async = project_root / "src" / "pyplanhat" / "_async"
    src_sync = project_root / "src" / "pyplanhat" / "_sync"
    tests_async = project_root / "tests" / "_async"
    tests_sync = project_root / "tests" / "_sync"

    # Additional replacements beyond the defaults
    additional_replacements = {
        "AsyncPyPlanhat": "PyPlanhat",
        "AsyncClient": "Client",
        "@pytest.mark.asyncio": "",
        "__aenter__": "__enter__",
        "__aexit__": "__exit__",
        "aclose": "close",
        "_async": "_sync",  # Transform import paths
    }

    # Create rules for transformations
    rules = [
        unasync.Rule(
            fromdir=str(src_async) + "/",
            todir=str(src_sync) + "/",
            additional_replacements=additional_replacements,
        ),
    ]

    # Add test rules if tests exist
    if tests_async.exists():
        rules.append(
            unasync.Rule(
                fromdir=str(tests_async) + "/",
                todir=str(tests_sync) + "/",
                additional_replacements=additional_replacements,
            )
        )

    # Collect all Python files from async directories
    files_to_process = []
    files_to_process.extend(collect_python_files(src_async))
    if tests_async.exists():
        files_to_process.extend(collect_python_files(tests_async))

    if not files_to_process:
        print("No async Python files found to process", file=sys.stderr)
        sys.exit(1)

    print(f"Processing {len(files_to_process)} files...")
    print("Generating sync source code...")

    try:
        # Use unasync API to generate sync code
        unasync.unasync_files(files_to_process, rules=rules)

        # Post-process: Remove @pytest.mark.asyncio decorators from sync tests
        print("Removing async test markers from sync tests...")
        remove_async_markers(tests_sync)

        print("✓ Sync code generation complete!")
        print("\nGenerated sync code in:")
        print(f"  - {src_sync}")
        if tests_async.exists():
            print(f"  - {tests_sync}")
        print("\nNext steps:")
        print("  1. Run: uv run ruff format src/pyplanhat/_sync/ tests/_sync/")
        print("  2. Run: uv run ruff check src/pyplanhat/_sync/ tests/_sync/ --fix")
        print("  3. Run: uv run pytest tests/_sync/ -v")
    except Exception as e:
        print(f"Failed to generate sync code: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
