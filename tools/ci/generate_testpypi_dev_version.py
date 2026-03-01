import hashlib
import os
import pathlib
import re


def main() -> None:
    pyproject = pathlib.Path("pyproject.toml")
    content = pyproject.read_text(encoding="utf-8")
    match = re.search(r'^version\s*=\s*"([^"]+)"', content, flags=re.MULTILINE)
    if not match:
        raise RuntimeError("No se encontró la versión en pyproject.toml")

    base_version = match.group(1)
    base_version = re.sub(r"(?i)(\.dev\d+|a\d+|b\d+|rc\d+|post\d+)$", "", base_version)

    branch_name = os.environ.get("BRANCH_NAME", "unknown")
    branch_slug = re.sub(r"[^a-z0-9]+", "-", branch_name.lower()).strip("-") or "branch"
    branch_hash = int(hashlib.sha256(branch_slug.encode("utf-8")).hexdigest()[:8], 16)

    pr_number = int(os.environ.get("PR_NUMBER", "0"))
    run_number = int(os.environ.get("GITHUB_RUN_NUMBER", "0"))

    dev_number = f"{pr_number:04d}{run_number:06d}{branch_hash % 10000:04d}"
    test_version = f"{base_version}.dev{dev_number}"

    updated = re.sub(
        r'^version\s*=\s*"[^"]+"',
        f'version = "{test_version}"',
        content,
        count=1,
        flags=re.MULTILINE,
    )
    pyproject.write_text(updated, encoding="utf-8")

    github_env = os.environ.get("GITHUB_ENV")
    if github_env:
        with open(github_env, "a", encoding="utf-8") as env_file:
            env_file.write(f"TESTPYPI_VERSION={test_version}\n")

    print(f"Generated TestPyPI version: {test_version}")


if __name__ == "__main__":
    main()