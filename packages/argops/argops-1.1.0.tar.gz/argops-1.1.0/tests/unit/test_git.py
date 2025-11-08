"""Test the git adapter."""

from pathlib import Path

import pytest

from argops.adapters.git import Git, GitRepositoryError


class TestGit:
    def test_init_invalid_repo(self) -> None:
        invalid_repo_path = Path("/invalid/path/to/repo")

        with pytest.raises(GitRepositoryError) as exc_info:
            Git(invalid_repo_path)

        assert (
            str(exc_info.value)
            == f"Could not find a git repository from the directory {invalid_repo_path}"
        )

    def test_init_in_a_directory_that_is_not_a_repo(self, tmp_path: Path) -> None:
        non_repo_path = tmp_path / "not_a_repo"
        non_repo_path.mkdir()

        with pytest.raises(GitRepositoryError) as exc_info:
            Git(non_repo_path)

        assert (
            str(exc_info.value)
            == f"Could not find a git repository from the directory {non_repo_path}"
        )


class TestCurrentCommitId:

    def test_get_current_commit_id_valid_repo(self, repo: "Git") -> None:
        result = repo.current_commit_id

        assert isinstance(result, str)
        assert len(result) == 40  # A valid Git commit SHA-1 hash is 40 characters long


class TestCurrentBranch:

    def test_get_current_branch(self, repo: "Git") -> None:
        result = repo.current_branch

        assert result == "main"
