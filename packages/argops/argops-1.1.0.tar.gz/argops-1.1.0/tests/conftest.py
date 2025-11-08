"""Store the classes and fixtures used throughout the tests."""

import os
import shutil
from pathlib import Path
from typing import Generator

import pytest

from argops.adapters.git import Git


@pytest.fixture(name="work_dir")
def work_dir_(tmp_path: Path) -> Path:
    """Create the work directory for the tests."""
    shutil.copytree("tests/assets/gpg", tmp_path / "gpg")
    shutil.copytree("tests/assets/repo", tmp_path / "repo")
    shutil.copytree("tests/assets/sops", tmp_path / "sops")
    os.environ["GNUPGHOME"] = str(tmp_path / "gpg")

    return tmp_path


@pytest.fixture
def set_current_dir(work_dir: Path) -> Generator[Path, None, None]:
    """Change the working directory for the test."""
    old_cwd = os.getcwd()
    os.chdir(work_dir / "repo")

    yield work_dir

    # Reset the current working directory after the test is done
    os.chdir(old_cwd)


@pytest.fixture(name="repo")
def repo_(work_dir: Path) -> Git:
    """Create a temporary Git repository with some test files."""
    # Create a temporary directory for the repo
    repo_path = work_dir / "repo"
    repo = Git(repo_path=repo_path, init=True)

    # Create a new file in the repo
    file_path = repo_path / "test.yaml"
    with open(file_path, "w", encoding="utf8") as f:
        f.write("key: value\n")

    # Create a secrets file in the repo
    project_root = Path(__file__).parent.parent
    secrets_source = project_root / "tests/assets/sops/secrets.yaml"
    shutil.copyfile(secrets_source, repo_path / "secrets.yaml")

    # Stage and commit the file
    repo.add(["*.yaml"])
    repo.commit("Initial commit")

    return repo
