"""
Upgrade declared dependencies to the highest allowed (based on pyproject.toml specifiers)
without uninstalling anything.

Usage:
    python -m jitx dependencies                          # check for updates (no changes)
    python -m jitx dependencies --upgrade                # upgrade to latest allowed
    python -m jitx dependencies --no-dependency-check    # do neither

For use in other code:
    from jitx.run.dependencies import sync_venv
    sync_venv() # will default to check mode with no prereleases
"""

import subprocess
import sys
import time
import argparse
import importlib.metadata
from pathlib import Path
from collections.abc import Sequence
import json
import os
import tempfile
from packaging.requirements import Requirement
from packaging.utils import canonicalize_name

from .pyproject import PyProject

COOLDOWN_SECONDS_DEFAULT = 3600
TIMESTAMP_FILE_DEFAULT = Path(".venv_sync_last")


def _time_since_sync(timestamp_file: Path) -> float | None:
    if not timestamp_file.exists():
        return None
    return time.time() - timestamp_file.stat().st_mtime


def _bump_timestamp(timestamp_file: Path) -> None:
    timestamp_file.parent.mkdir(parents=True, exist_ok=True)
    if timestamp_file.exists():
        timestamp_file.touch()
    else:
        timestamp_file.write_text(
            "Tracks when dependencies were last checked. Delete to force a recheck."
        )


def _run_pip_command(
    requirements: list[str], *, allow_prereleases: bool, dry_run: bool
):
    """
    Runs the pip command upgrade with the given requirements.
    Dry-run mode will not make any changes but will report what would be changed ( used for check mode)
    The report is written to a temporary file to avoid mixing with other output.
    """
    report_file_path = None
    try:
        # Create a temporary file to hold the pip report
        with tempfile.NamedTemporaryFile(mode="w+", delete=False) as temp_file:
            report_file_path = temp_file.name

        cmd = [
            sys.executable,
            "-m",
            "pip",
            "install",
            "--upgrade",  # Upgrade packages
            "--no-input",
            *requirements,  # (the packages)
            "--report",
            report_file_path,  # file to write the report to
        ]

        if dry_run:
            cmd.append("--dry-run")  # No changes made, just report what would be done

        if allow_prereleases:
            cmd.append("--pre")

        cp = subprocess.run(cmd, text=True, check=False, capture_output=True)

        # Read the JSON from the temp file if it exists
        report_json = ""
        if os.path.exists(report_file_path):
            with open(report_file_path) as f:
                report_json = f.read()

        return cp.returncode, report_json, cp.stderr

    finally:
        # Temp file clean up
        if report_file_path and os.path.exists(report_file_path):
            os.remove(report_file_path)


def _normalize_name(name: str) -> str:
    return canonicalize_name(name)


def _updates_from_report(
    installed_packages, dependencies: Sequence[Requirement]
) -> list[tuple[Requirement, str | None, str]]:
    target_versions = {
        _normalize_name(item.get("name")): item.get("version")
        for item in installed_packages
        if item.get("name") and item.get("version")
    }

    updates = []
    for dep in dependencies:
        dep_name = dep.name
        normalized_name = _normalize_name(dep_name)
        try:
            installed = importlib.metadata.version(dep_name)
        except importlib.metadata.PackageNotFoundError:
            installed = None

        target = target_versions.get(normalized_name)
        if target and installed != target:
            updates.append((dep, installed, target))
    return updates


def _parse_pip_report(report_json: str) -> list | None:
    """Parses a the pip JSON report and returns a list of installed packages."""
    try:
        report = json.loads(report_json)
        # Filter the report to include only installed packages
        installed_packages = [
            {"name": item["metadata"]["name"], "version": item["metadata"]["version"]}
            for item in report.get("install", [])
            if not item.get("is_direct", False) and not item.get("is_yanked", False)
        ]
        return installed_packages
    except (json.JSONDecodeError, KeyError) as e:
        print(f"Failed to parse pip's report: {e}", file=sys.stderr)
        print("Failed to get dependency information.", file=sys.stderr)
        return None


def sync_venv(
    *,
    mode: str = "check",
    allow_prereleases: bool = False,
    include_optional_groups: Sequence[str] | None = None,
    editable_install: bool = False,
) -> None:
    """
    - check  -> dry-run and list dependencies that would update (respects cooldown).
    - update -> apply the updates.
    """
    if mode is None:
        return
    pyproject = PyProject()
    if not pyproject:
        print("No pyproject.toml found.")
        return

    dependencies = pyproject.dependencies(include_optional_groups)
    if not dependencies:
        print("No dependencies declared.")
        return

    is_dry_run = mode == "check"
    if is_dry_run:
        tss = _time_since_sync(TIMESTAMP_FILE_DEFAULT)
        if tss is not None and tss <= COOLDOWN_SECONDS_DEFAULT:
            remaining_minutes = int(COOLDOWN_SECONDS_DEFAULT - tss) // 60
            if remaining_minutes > 0:
                print(
                    f"Dependencies recently checked, skipping. Will check again in {remaining_minutes} minutes."
                )
            else:
                print(
                    "Dependencies recently checked, skipping. Will check again in less than a minute."
                )
            return

    rc, report_json, err = _run_pip_command(
        [str(d) for d in dependencies],
        allow_prereleases=allow_prereleases,
        dry_run=is_dry_run,
    )

    if rc != 0 or not report_json:
        if err:
            print("Pip log output (stderr):", file=sys.stderr)
            print(err, file=sys.stderr)
        print("Failed to get dependency information.", file=sys.stderr)
        _bump_timestamp(TIMESTAMP_FILE_DEFAULT)
        return

    installed_packages = _parse_pip_report(report_json)
    if installed_packages is None:
        _bump_timestamp(TIMESTAMP_FILE_DEFAULT)
        return

    if is_dry_run:
        updates = _updates_from_report(installed_packages, dependencies)
        if not updates:
            print("All dependencies up to date.")
        else:
            print("Updates available:")
            for dep, installed, target in updates:
                if installed is None:
                    print(f"  {dep.name}: not installed → {target}")
                else:
                    print(f"  {dep.name}: {installed} → {target}")
    else:  # mode == "update"
        if not installed_packages:
            print("No new dependencies were installed or updated.")
        else:
            print("Dependencies updated:")
            for package in installed_packages:
                print(f"  {package['name']}: {package['version']}")

        if editable_install:
            cp2 = subprocess.run(
                [sys.executable, "-m", "pip", "install", "-e", "."],
                text=True,
                check=False,
            )
            if cp2.returncode != 0:
                print("Editable install failed.", file=sys.stderr)

    _bump_timestamp(TIMESTAMP_FILE_DEFAULT)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--upgrade", action="store_true", help="Upgrade dependencies")
    group.add_argument(
        "--no-dependency-check",
        action="store_true",
        help="Dont check for dependencies nor upgrade them",
    )
    parser.add_argument(
        "--allow-prereleases",
        action="store_true",
        help="Allow pre-release versions",
    )
    parser.add_argument(
        "--check-include-group",
        action="append",
        default=None,
        help="Optional-dependency group(s) to include (repeatable)",
    )
    parser.add_argument(
        "--editable-install",
        action="store_true",
        help="Reinstall the current project in editable mode after upgrading dependencies",
    )

    args = parser.parse_args()
    if args.no_dependency_check:
        sys.exit()
    mode = "update" if args.upgrade else "check"

    sync_venv(
        mode=mode,
        allow_prereleases=args.allow_prereleases,
        include_optional_groups=args.check_include_group,
        editable_install=args.editable_install,
    )
