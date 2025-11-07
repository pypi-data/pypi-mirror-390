import argparse
from collections import OrderedDict
from collections.abc import Mapping
from dataclasses import dataclass
import json
from logging import getLogger
from pathlib import Path
from typing import Any

from jitx.run import DesignFactory, DesignFinder

LAUNCH_JSON_FILENAME = "launch.json"
TASKS_JSON_FILENAME = "tasks.json"
RUN_MODULE = "jitx"
BUILD_COMMAND = "build"
TASK_GROUP = {"kind": "build"}
JITX_TASK_DETAIL = "JITX Build task"
RUN_ALL_LABEL = "RunAll JITX Designs in Project"

logger = getLogger("jitx.launch_config")


@dataclass
class VSCodePaths:
    vscode_dir: Path
    launch_json: Path
    tasks_json: Path


def get_vscode_paths(project_path) -> VSCodePaths:
    vscode_dir = Path(project_path).resolve() / ".vscode"
    return VSCodePaths(
        vscode_dir=vscode_dir,
        launch_json=vscode_dir / LAUNCH_JSON_FILENAME,
        tasks_json=vscode_dir / TASKS_JSON_FILENAME,
    )


def get_designs(project_path):
    designs = []

    def collect(ob: Mapping[str, Any] | str, file=None):
        if isinstance(ob, Mapping):
            designs.extend(ob.get("designs", ()))

    DesignFactory(DesignFinder([str(project_path)]), formatter=collect).list()
    filtered = [d for d in designs if d != "jitx.sample.SampleDesign"]

    return sorted(filtered)


def load_existing_json(path):
    if path.exists():
        try:
            with path.open("r", encoding="utf-8") as f:
                return json.load(f)
        except json.JSONDecodeError:
            logger.warning(f"Invalid JSON in {path}. Resetting file.")

    config_key = "configurations" if "launch" in str(path) else "tasks"
    return {"version": "2.0.0", config_key: []}


def make_args(design=None):
    base = [
        "--port",
        "${command:jitx.get-websocket-port}",
    ]
    return [BUILD_COMMAND, design, *base] if design else ["build-all", *base]


def make_launch_config(name, args):
    return OrderedDict(
        [
            ("name", name),
            ("type", "debugpy"),
            ("request", "launch"),
            ("console", "integratedTerminal"),
            ("module", RUN_MODULE),
            ("args", args),
            ("justMyCode", False),
        ]
    )


def update_launch_json(paths, designs):
    launch_data = load_existing_json(paths.launch_json)
    existing_configs = launch_data.get("configurations", [])

    non_jitx_configs = [
        cfg for cfg in existing_configs if cfg.get("module") != RUN_MODULE
    ]
    run_all_config = next(
        (cfg for cfg in existing_configs if cfg.get("name") == RUN_ALL_LABEL), None
    )

    if not run_all_config:
        run_all_config = make_launch_config(RUN_ALL_LABEL, make_args())

    jitx_configs = [
        make_launch_config(f"Run {design}", make_args(design)) for design in designs
    ]
    launch_data["configurations"] = [*non_jitx_configs, run_all_config, *jitx_configs]

    with paths.launch_json.open("w", encoding="utf-8") as f:
        json.dump(launch_data, f, indent=4)

    logger.info(f"Updated {paths.launch_json}")


def make_task(design_label, args):
    return {
        "label": f"Run {design_label}",
        "type": "process",
        "command": "python",
        "args": ["-m", RUN_MODULE] + args,
        "problemMatcher": [],
        "group": TASK_GROUP,
        "detail": JITX_TASK_DETAIL,
    }


def create_tasks_json(paths, designs):
    tasks_data = load_existing_json(paths.tasks_json)
    existing_tasks = tasks_data.get("tasks", [])

    retained_tasks = [
        task for task in existing_tasks if task.get("detail") != JITX_TASK_DETAIL
    ]

    jitx_tasks = [make_task(design, make_args(design)) for design in designs]
    if designs:
        jitx_tasks.append(make_task("All JITX Designs in Project", make_args()))

    tasks_data["tasks"] = [*retained_tasks, *jitx_tasks]
    tasks_data.pop("inputs", None)

    with paths.tasks_json.open("w", encoding="utf-8") as f:
        json.dump(tasks_data, f, indent=4)

    logger.info(f"Updated {paths.tasks_json}")


def generate_config(project_path="."):
    """Generate or update launch.json and tasks.json for a JITX project."""
    project_path = Path(project_path).resolve()
    if project_path.exists():
        paths = get_vscode_paths(project_path)
        paths.vscode_dir.mkdir(parents=True, exist_ok=True)
        designs = get_designs(project_path)

        update_launch_json(paths, designs)
        create_tasks_json(paths, designs)
    else:
        logger.error(f"The specified project path does not exist: {project_path}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Generate or update launch.json and tasks.json for a JITX project."
    )
    parser.add_argument(
        "project_path", type=str, help="Path to the target project folder"
    )
    args = parser.parse_args()
    generate_config(args.project_path)
