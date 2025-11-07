from collections.abc import Sequence
import os
from pathlib import Path
import tomllib

from packaging.requirements import Requirement


class JitxTool:
    exclude: Sequence[str] = ()

    def __init__(self, *, exclude: list[str] | None = None, **kwargs):
        if exclude:
            self.exclude = exclude
        if kwargs:
            print("Warning, unexpected tool option:", ", ".join(kwargs))


class PyProject:
    PYPROJECT_BASENAME = "pyproject.toml"

    def __init__(self, search_path: str = "."):
        self.path = self._discover_pyproject(search_path)
        if self.path:
            with self.path.open("rb") as f:
                self.data = tomllib.load(f)
        else:
            self.data = {}

    @classmethod
    def _discover_pyproject(cls, start: str) -> Path | None:
        p = Path(start).resolve()
        for base in (p, *p.parents):
            candidate = base / cls.PYPROJECT_BASENAME
            if os.access(candidate, os.R_OK):
                return candidate
        return None

    def __bool__(self):
        return bool(self.path)

    def tool(self, *tool: str) -> dict | None:
        data = self.data.get("tool")
        for t in tool:
            if not isinstance(data, dict):
                return None
            data = data.get(t)
        return data

    @property
    def jitxtool(self):
        data = self.tool("jitx") or {}
        return JitxTool(**data)

    def dependencies(
        self, include_optional_groups: Sequence[str] | None = None
    ) -> Sequence[Requirement]:
        project = self.data.get("project", {})
        dependencies = project.get("dependencies", [])

        if include_optional_groups:
            optionals = project.get("optional-dependencies", {})
            for group in include_optional_groups:
                dependencies.extend(optionals.get(group, []))

        def _validate(dep: str) -> Requirement | None:
            dep = dep.strip()
            if not dep:
                return None
            try:
                return Requirement(dep)
            except Exception as e:
                print(f"Invalid dependency '{dep}' in {self.path}: {e}")

        return [r for r in (_validate(dep) for dep in dependencies) if r]
