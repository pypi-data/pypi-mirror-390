# jitx/__main__.py
from argparse import ArgumentParser
from logging import basicConfig
import sys

from jitx.run import (
    DesignBuilder,
    DesignFactory,
    DesignFinder,
    DryRunBuilder,
    json_formatter,
    text_formatter,
)
from jitx.run.dependencies import sync_venv

parser = ArgumentParser("jitx")
parser.add_argument("--format", choices=["json", "text"])
parser.add_argument(
    "--logging",
    type=str,
    default="INFO",
    choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
    help="Logging level",
)

subparser = parser.add_subparsers(dest="cmd")

# find
find_design_parser = subparser.add_parser("find")
find_design_parser.add_argument("path", nargs="*")

# build
build_design_parser = subparser.add_parser("build")
build_design_parser.add_argument("--dump")
build_design_parser.add_argument("--dry", default=False, action="store_true")
build_design_parser.add_argument("--host", type=str, default="localhost")
build_design_parser.add_argument("--port", type=int)
build_design_parser.add_argument("--uri", type=str)
build_design_parser.add_argument("--socket", metavar="FILE", default=None, type=str)
build_design_parser.add_argument("--no-dependency-check", action="store_true")
build_design_parser.add_argument("--check-include-group", action="append", default=None)
build_design_parser.add_argument("design", nargs="+")

# build-all
build_all_design_parser = subparser.add_parser("build-all")
build_all_design_parser.add_argument("--host", type=str, default="localhost")
build_all_design_parser.add_argument("--port", type=int)
build_all_design_parser.add_argument("--uri", type=str)
build_all_design_parser.add_argument("--socket", metavar="FILE", default=None, type=str)
build_all_design_parser.add_argument("--generate-config", action="store_true")
build_all_design_parser.add_argument("--no-dependency-check", action="store_true")
build_all_design_parser.add_argument(
    "--check-include-group", action="append", default=None
)

# upgrade-dependencies
dependency_parser = subparser.add_parser(
    "dependencies", help="Check or upgrade Python dependencies"
)
dependency_parser.add_argument(
    "--upgrade",
    action="store_true",
    help="Upgrade to highest allowed (otherwise just check)",
)
dependency_parser.add_argument(
    "--allow-prereleases",
    "--pre",
    action="store_true",
    help="Include prereleases during resolution",
)
dependency_parser.add_argument(
    "--check-include-group",
    action="append",
    default=None,
    help="Optional-dependency group(s) to include (repeatable)",
)
dependency_parser.add_argument(
    "--editable-install",
    action="store_true",
    help="Reinstall the current project in editable mode after upgrading dependencies",
)

build_config_parser = subparser.add_parser(
    "run-config", help="Generate VSCode run and debug configuration"
)

args = parser.parse_args()
basicConfig(level=args.logging)

formatter = {"json": json_formatter, "text": text_formatter}.get(
    args.format, text_formatter
)

if args.cmd == "find":
    DesignFactory(DesignFinder(args.path), DryRunBuilder(), formatter=formatter).list()
elif args.cmd == "build":
    if not args.no_dependency_check:
        sync_venv(
            mode="check",
            allow_prereleases=False,
            include_optional_groups=args.check_include_group,
        )

    if args.dry:
        builder = DryRunBuilder()
    elif args.uri:
        builder = DesignBuilder(uri=args.uri)
    elif args.port:
        builder = DesignBuilder(port=args.port, host=args.host)
    elif args.socket:
        builder = DesignBuilder(spec=args.socket)
    else:
        builder = DesignBuilder()

    finder = DesignFinder(".")
    factory = DesignFactory(finder, builder, formatter=formatter, dump=args.dump)
    for design in args.design:
        if design.endswith(".py"):
            factory.by_file(design)
        else:
            factory.by_name(design)
    factory.build()
    if not factory.success:
        sys.exit(1)

elif args.cmd == "build-all":
    if not args.no_dependency_check:
        sync_venv(
            mode="check",
            allow_prereleases=False,
            include_optional_groups=args.check_include_group,
        )

    finder = DesignFinder(".")
    builder = (
        DesignBuilder(uri=args.uri)
        if args.uri
        else DesignBuilder(port=args.port, host=args.host)
        if args.port
        else DesignBuilder()
    )
    factory = DesignFactory(finder, builder, formatter=formatter)
    factory.add_all()
    factory.build()
    if args.generate_config:
        from jitx.vscode.config import generate_config

        generate_config()
    if not factory.success:
        sys.exit(1)

elif args.cmd == "dependencies":
    mode = "upgrade" if args.upgrade else "check"
    sync_venv(
        mode=mode,
        allow_prereleases=bool(args.allow_prereleases),
        include_optional_groups=args.check_include_group,
        editable_install=args.editable_install,
    )
elif args.cmd == "run-config":
    from jitx.vscode.config import generate_config

    generate_config()
else:
    parser.print_help()
