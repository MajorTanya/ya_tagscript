import dataclasses
import difflib
import logging
import re
import shlex
import subprocess
import sys
import textwrap
import tomllib
from argparse import ArgumentParser

logging.basicConfig(
    format="[{asctime}.{msecs:03.0f}] [{levelname:<8}] [{name:<12}]: {message}",
    datefmt="%Y-%m-%d %H:%M:%S",
    style="{",
    stream=sys.stdout,
)
_log = logging.getLogger("make_release")

"""
A helper script to bump the project version and replace it everywhere referenced.

Inspired by the release mechanism/scripts used in https://github.com/nedbat/coveragepy/
but written in pure Python with only the options this project needs.
"""


@dataclasses.dataclass
class MakeReleaseNamespace:
    dry_run: bool = False
    verbose: bool = False
    interactive: bool = False
    create_tag: bool = False
    alpha: bool = False
    patch: bool = False
    minor: bool = False
    major: bool = False


def init_argparse() -> ArgumentParser:
    arg_parser = ArgumentParser(
        usage="python -m %(prog)s [OPTION]...",
        description=(
            "Command-line utility to create releases for ya_tagscript and ensure all "
            "version mentions are updated properly"
        ),
    )
    arg_parser.add_argument(
        "--verbose",
        action="store_true",
        help="Print debug output",
    )
    arg_parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Run version bump with debug output and without actually changing files.",
    )
    arg_parser.add_argument(
        "--interactive",
        action="store_true",
        help="Require confirmation of the new version number before proceeding.",
    )
    release_type_group = arg_parser.add_mutually_exclusive_group(required=True)
    release_type_group.add_argument(
        "--create-tag",
        action="store_true",
        help="Create a (signed) git tag with the new project version",
    )
    release_type_group.add_argument(
        "--alpha",
        action="store_true",
        help="Bump the alpha qualifier",
    )
    release_type_group.add_argument(
        "--patch",
        action="store_true",
        help="Bump the project version with a SemVer patch increase",
    )
    release_type_group.add_argument(
        "--minor",
        action="store_true",
        help="Bump the project version with a SemVer minor increase",
    )
    release_type_group.add_argument(
        "--major",
        action="store_true",
        help="Bump the project version with a SemVer major increase",
    )

    return arg_parser


def commit_release_with_tag(project_version: str, *, dry_run: bool, verbose: bool):
    git_signed_tag_cmd = (
        "git",
        "tag",
        "-s",
        f"v{project_version}",
        "-m",
        f"Release v{project_version}",
    )
    if dry_run or verbose:
        _log.debug("%s", shlex.join(git_signed_tag_cmd))
        if dry_run:
            return
    subprocess.run(git_signed_tag_cmd, shell=False)


def update_changelog(project_version: str, *, dry_run: bool, verbose: bool):
    with open("./CHANGELOG.md", mode="r", encoding="utf8") as cf:
        old_changelog_text = cf.read()
        already_released_version = re.search(
            rf"^# v{project_version}$",
            old_changelog_text,
            flags=re.MULTILINE,
        )
        if already_released_version is not None:
            raise RuntimeError(
                f"v{project_version} already has a CHANGELOG entry. Aborting "
                f"docs update process without changes..."
            )

    match = re.match(
        r"(^# Unreleased\n\n(.+?^# v))",
        old_changelog_text,
        flags=re.MULTILINE | re.DOTALL,
    )
    if match is None or (release_content := match.group(2)) == "":
        raise RuntimeError(
            "Nothing to update in CHANGELOG.md — Did something go wrong?"
        )

    updated_changelog_text = (
        textwrap.dedent(
            f"""\
            # Unreleased

            *Currently none*

            # v{project_version}
            """
        )
        + release_content
        + old_changelog_text[len(match.group(1)) :]
    )
    if dry_run or verbose:
        diff = difflib.unified_diff(
            old_changelog_text.splitlines(keepends=True),
            updated_changelog_text.splitlines(keepends=True),
        )
        diff_str = "".join(diff)

        _log.debug("Changelog diff below:\n%s", diff_str.strip())
        _log.debug("Changelog diff above")
        if dry_run:
            return

    with open("./CHANGELOG.md", mode="w", encoding="utf8") as cf:
        cf.write(updated_changelog_text)


def update_pyproject(project_version: str, *, dry_run: bool, verbose: bool):
    with open("./pyproject.toml", mode="r", encoding="utf8") as pypf:
        old_pyproject_content = pypf.read()

    match = re.search(
        r'(.+?)(\[project]\nname = "ya_tagscript"\nversion = "1\.2\.1")',
        old_pyproject_content,
        flags=re.MULTILINE | re.DOTALL,
    )
    if match is None or match.group(2) is None:
        raise RuntimeError("Could not find version in pyproject.toml")

    updated_pyproject_content = (
        old_pyproject_content[: len(match.group(1))]
        + textwrap.dedent(
            f'''\
            [project]
            name = "ya_tagscript"
            version = "{project_version}"'''
        )
        + old_pyproject_content[len(match.group(1)) + len(match.group(2)) :]
    )
    if dry_run or verbose:
        diff = difflib.unified_diff(
            old_pyproject_content.splitlines(keepends=True),
            updated_pyproject_content.splitlines(keepends=True),
        )
        diff_str = "".join(diff)
        _log.debug("pyproject.toml diff below:\n%s", diff_str.strip())
        _log.debug("pyproject.toml diff above")
        if dry_run:
            return

    with open("./pyproject.toml", mode="w", encoding="utf8") as pypf:
        pypf.write(updated_pyproject_content)


def update_readme(project_version: str, *, dry_run: bool, verbose: bool):
    with open("./README.md", mode="r", encoding="utf8") as rf:
        old_readme_text = rf.read()

    new_readme_text = re.sub(
        r"^Current stable version: .+?$",
        f"Current stable version: v{project_version}",
        old_readme_text,
        count=1,
        flags=re.MULTILINE,
    )

    updated_tag_section = textwrap.dedent(
        f"""\
        <!--VERSIONED TAG SECTION START-->

        ```
        pip install git+https://github.com/MajorTanya/ya_tagscript.git@v{project_version}
        ```

        <!--VERSIONED TAG SECTION END-->"""
    )
    new_readme_text = re.sub(
        r"^<!--VERSIONED TAG SECTION START-->$.+?^<!--VERSIONED TAG SECTION END-->$",
        updated_tag_section,
        new_readme_text,
        count=1,
        flags=re.MULTILINE | re.DOTALL,
    )
    if dry_run or verbose:
        diff = difflib.unified_diff(
            old_readme_text.splitlines(keepends=True),
            new_readme_text.splitlines(keepends=True),
        )
        diff_str = "".join(diff)
        _log.debug("Readme diff below:\n%s", diff_str.strip())
        _log.debug("Readme diff above")
        if dry_run:
            return

    with open("./README.md", mode="w", encoding="utf8") as rf:
        rf.write(new_readme_text)


def update_sphinx_conf(project_version: str, *, dry_run: bool, verbose: bool):
    with open("./docs/conf.py", mode="r", encoding="utf8") as scf:
        old_sphinx_conf = scf.read()

    updated_version_section = textwrap.dedent(
        f"""\
        ### VERSION SECTION START
        version = "{project_version}"
        ### VERSION SECTION END"""
    )
    new_sphinx_conf = re.sub(
        r"^### VERSION SECTION START$\n^version = .+?$\n^### VERSION SECTION END$",
        updated_version_section,
        old_sphinx_conf,
        count=1,
        flags=re.MULTILINE,
    )
    if dry_run or verbose:
        diff = difflib.unified_diff(
            old_sphinx_conf.splitlines(keepends=True),
            new_sphinx_conf.splitlines(keepends=True),
        )
        diff_str = "".join(diff)
        _log.debug("conf.py diff below:\n%s", diff_str.strip())
        _log.debug("conf.py diff above")
        if dry_run:
            return

    with open("./docs/conf.py", mode="w", encoding="utf8") as scf:
        scf.write(new_sphinx_conf)


def main():
    args = MakeReleaseNamespace()
    parser = init_argparse()
    parser.parse_args(
        args=None if sys.argv[1:] else ["--help"],
        namespace=args,
    )

    is_dry_run = args.dry_run
    is_verbose = args.verbose
    if is_dry_run or is_verbose:
        _log.setLevel(logging.DEBUG)

    _log.debug(f"Invoked with {args=}")

    with open("./pyproject.toml", mode="r", encoding="utf8") as pf:
        pyproject_config = tomllib.loads(pf.read())
        current_version = str(pyproject_config["project"]["version"])

    if (match := re.match(r"(\d+\.\d+\.\d+)([ab]\d+)?", current_version)) is None:
        raise ValueError("Current project version does not match SemVer, exiting...")

    _log.debug(f"current_version=%r", current_version)

    main_semver = match.group(1)
    _log.debug(f"main_semver=%r", main_semver)

    current_prerelease_section = match.group(2)
    _log.debug(f"current_prerelease_section=%r", current_prerelease_section)

    currently_is_full_release = current_prerelease_section is None
    _log.debug(f"currently_is_full_release=%r", currently_is_full_release)

    if args.alpha:
        _log.debug("Alpha bump requested")
        if currently_is_full_release:
            major, minor, patch = main_semver.split(".", maxsplit=2)
            main_semver = f"{major}.{minor}.{int(patch) + 1}"
            new_alpha = "a1"
        elif current_prerelease_section.startswith("a"):
            new_alpha = f"a{int(current_prerelease_section[1:]) + 1}"
        else:
            _log.debug(
                "Could not recognize prelease type: %r",
                current_prerelease_section,
            )
            raise RuntimeError("Unsupported current prerelease type.")
        new_version = f"{main_semver}{new_alpha}"
        new_is_stable_release = False
    elif args.patch:
        _log.debug("Patch bump requested")
        major, minor, patch = main_semver.split(".", maxsplit=2)
        new_version = f"{major}.{minor}.{int(patch) + 1}"
        new_is_stable_release = True
    elif args.minor:
        _log.debug("Minor bump requested")
        major, minor, _ = main_semver.split(".", maxsplit=2)
        new_version = f"{major}.{int(minor) + 1}.0"
        new_is_stable_release = True
    elif args.major:
        _log.debug("Major bump requested")
        major, _, _ = main_semver.split(".", maxsplit=2)
        new_version = f"{int(major) + 1}.0.0"
        new_is_stable_release = True
    else:
        raise RuntimeError("Missing bump type (must be one of alpha|patch|minor|major)")

    _log.debug(f"new_version=%r", new_version)

    if args.interactive:
        approved = input(f"New version will be {new_version!r}. Proceed? (Y/n) ")
        if approved.strip().lower() != "y":
            _log.info("Version not accepted, exiting...")
            return

    update_pyproject(new_version, dry_run=is_dry_run, verbose=is_verbose)
    update_sphinx_conf(new_version, dry_run=is_dry_run, verbose=is_verbose)
    if new_is_stable_release:
        update_changelog(new_version, dry_run=is_dry_run, verbose=is_verbose)
        update_readme(new_version, dry_run=is_dry_run, verbose=is_verbose)
        if args.create_tag:
            commit_release_with_tag(new_version, dry_run=is_dry_run, verbose=is_verbose)


if __name__ == "__main__":
    main()
