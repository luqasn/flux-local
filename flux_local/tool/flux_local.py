"""Command line tool for building, diffing, validating flux local repositories."""

import argparse
import asyncio
import logging
import pathlib

import yaml

from . import build, diff, manifest, test

_LOGGER = logging.getLogger(__name__)


def main() -> None:
    """Flux-local command line tool main entry point."""
    # https://github.com/yaml/pyyaml/issues/89
    yaml.Loader.yaml_implicit_resolvers.pop("=")

    parser = argparse.ArgumentParser(
        description="Manages local kubernetes objects in a flux repository."
    )
    parser.add_argument(
        "--log-level", choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
    )
    subparsers = parser.add_subparsers(dest="command", help="Command", required=True)

    build_args = subparsers.add_parser(
        "build",
        help="Build local flux Kustomization target from a local directory",
    )
    build_args.add_argument(
        "path", type=pathlib.Path, help="Path to the kustomization or charts"
    )
    build_args.add_argument(
        "--enable-helm",
        type=bool,
        action=argparse.BooleanOptionalAction,
        help="Enable use of HelmRelease inflation",
    )
    build_args.add_argument(
        "--skip-crds",
        type=bool,
        default=False,
        action=argparse.BooleanOptionalAction,
        help="Allows disabling of outputting CRDs to reduce output size",
    )
    build_args.set_defaults(cls=build.BuildAction)

    diff_args = subparsers.add_parser(
        "diff", help="Build local flux Kustomization target from a local directory"
    )
    diff_args.add_argument(
        "path", type=pathlib.Path, help="Path to the kustomization or charts"
    )
    diff_args.add_argument(
        "--enable-helm",
        type=bool,
        action=argparse.BooleanOptionalAction,
        help="Enable use of HelmRelease inflation",
    )
    diff_args.add_argument(
        "--skip-crds",
        type=bool,
        default=False,
        action=argparse.BooleanOptionalAction,
        help="Allows disabling of outputting CRDs to reduce output size",
    )
    diff_args.set_defaults(cls=diff.DiffAction)

    manifest_args = subparsers.add_parser(
        "manifest", help="Build a yaml manifest file representing the cluster"
    )
    manifest_args.add_argument(
        "path", type=pathlib.Path, help="Path to the kustomization or charts"
    )
    manifest_args.set_defaults(cls=manifest.ManifestAction)

    test_args = subparsers.add_parser("test", help="Build and validate the cluster")
    test_args.add_argument(
        "path", type=pathlib.Path, help="Path to the kustomization or charts"
    )
    test_args.set_defaults(cls=test.TestAction)

    args = parser.parse_args()

    if args.log_level:
        logging.basicConfig(level=args.log_level)

    command = args.cls()
    asyncio.run(command.run(**vars(args)))


if __name__ == "__main__":
    main()