import os
import pathlib
import re


def _write_actions_output(key: str, value: str) -> None:
    github_output = os.environ.get("GITHUB_OUTPUT")
    if github_output:
        with open(github_output, "a", encoding="utf-8") as file:
            file.write(f"{key}={value}\n")


def _write_actions_env(key: str, value: str) -> None:
    github_env = os.environ.get("GITHUB_ENV")
    if github_env:
        with open(github_env, "a", encoding="utf-8") as file:
            file.write(f"{key}={value}\n")


def main() -> None:
    pyproject = pathlib.Path("pyproject.toml")
    content = pyproject.read_text(encoding="utf-8")

    match = re.search(r'^version\s*=\s*"([^"]+)"', content, flags=re.MULTILINE)
    if not match:
        raise RuntimeError("No se encontró la versión en pyproject.toml")

    current_version = match.group(1)
    semver_match = re.match(r"^(\d+)\.(\d+)\.(\d+)$", current_version)
    if not semver_match:
        raise RuntimeError(
            f"Versión no soportada para auto-bump: {current_version}. Se espera formato MAJOR.MINOR.PATCH"
        )

    major, minor, patch = semver_match.groups()
    next_version = f"{major}.{minor}.{int(patch) + 1}"

    updated = re.sub(
        r'^version\s*=\s*"[^"]+"',
        f'version = "{next_version}"',
        content,
        count=1,
        flags=re.MULTILINE,
    )
    pyproject.write_text(updated, encoding="utf-8")

    release_tag = f"v{next_version}"
    _write_actions_output("release_version", next_version)
    _write_actions_output("release_tag", release_tag)
    _write_actions_env("RELEASE_VERSION", next_version)
    _write_actions_env("RELEASE_TAG", release_tag)

    print(f"Bumped version: {current_version} -> {next_version}")


if __name__ == "__main__":
    main()