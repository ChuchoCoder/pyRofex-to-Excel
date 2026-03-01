import glob
import os
import pathlib
import re


def main() -> None:
    wheels = sorted(glob.glob("dist/*.whl"))
    if not wheels:
        print("No wheel found in dist/; skipping summary generation")
        raise SystemExit(0)

    wheel = pathlib.Path(wheels[0]).name
    match = re.match(r"^(?P<name>.+)-(?P<version>[^-]+)-[^-]+-[^-]+-[^-]+\.whl$", wheel)
    if not match:
        print(f"Could not parse wheel filename: {wheel}")
        raise SystemExit(0)

    package_name = match.group("name").replace("_", "-")
    version = match.group("version")

    summary = os.environ.get("GITHUB_STEP_SUMMARY")
    if not summary:
        raise SystemExit(0)

    install_cmd = (
        "pip install "
        "--index-url https://test.pypi.org/simple/ "
        "--extra-index-url https://pypi.org/simple/ "
        f"{package_name}=={version}"
    )

    github_env = os.environ.get("GITHUB_ENV")
    if github_env:
        with open(github_env, "a", encoding="utf-8") as env_file:
            env_file.write(f"TESTPYPI_PACKAGE={package_name}\n")
            env_file.write(f"TESTPYPI_VERSION={version}\n")
            env_file.write(f"TESTPYPI_INSTALL_CMD={install_cmd}\n")

    with open(summary, "a", encoding="utf-8") as summary_file:
        summary_file.write("## 📦 TestPyPI Package\n")
        summary_file.write(f"- **Package:** `{package_name}`\n")
        summary_file.write(f"- **Version:** `{version}`\n")
        summary_file.write("- **Status:** ⏳ Publishing...\n")
        summary_file.write("- **Install command:**\n")
        summary_file.write("```bash\n")
        summary_file.write(f"{install_cmd}\n")
        summary_file.write("```\n")

    print(f"Generated TestPyPI install command: {install_cmd}")


if __name__ == "__main__":
    main()