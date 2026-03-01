import glob
import os
import pathlib
import re


def main() -> None:
    wheels = sorted(glob.glob("dist/*.whl"))
    if not wheels:
        print("No wheel found in dist/; skipping metadata extraction")
        raise SystemExit(0)

    wheel = pathlib.Path(wheels[0]).name
    match = re.match(r"^(?P<name>.+)-(?P<version>[^-]+)-[^-]+-[^-]+-[^-]+\.whl$", wheel)
    if not match:
        print(f"Could not parse wheel filename: {wheel}")
        raise SystemExit(0)

    package_name = match.group("name").replace("_", "-")
    version = match.group("version")

    github_env = os.environ.get("GITHUB_ENV")
    if github_env:
        with open(github_env, "a", encoding="utf-8") as env_file:
            env_file.write(f"PYPI_PACKAGE={package_name}\n")
            env_file.write(f"PYPI_VERSION={version}\n")

    print(f"Detected PyPI package: {package_name}=={version}")


if __name__ == "__main__":
    main()