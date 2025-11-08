"""Integration tests of the services."""

from pathlib import Path

import pytest

from argops.adapters.git import Git
from argops.services import load_sops_file, promote_changes, save_sops_file


@pytest.mark.usefixtures("set_current_dir")
class TestPromoteChanges:
    def test_promote_staging_values_when_production_doesnt_exist(
        self, repo: "Git"
    ) -> None:
        staging_dir = Path("staging/application-3")
        staging_dir.mkdir(parents=True, exist_ok=True)
        production_dir = Path("production/application-3")
        production_dir.mkdir(parents=True, exist_ok=True)
        staging_file = staging_dir / "values-staging.yaml"
        staging_file.write_text("foo: bar-staging", encoding="utf8")
        production_file = production_dir / "values-production.yaml"
        assert not production_file.exists()
        repo.add(["staging"])
        repo.commit("Add staging's values file")

        promote_changes(repo)  # act

        assert production_file.exists()
        result_content = production_file.read_text(encoding="utf8")
        assert "\nfoo: bar-production  # New key in source\n" in result_content
        assert not (production_dir / "values-staging.yaml").exists()

    def test_promote_staging_values_when_production_differs(self, repo: "Git") -> None:
        """
        Test the case where some staging values were promoted, the user has
        changed the production values, and we promote again without changing
        the staging values file.
        """
        staging_dir = Path("staging/application-3")
        staging_dir.mkdir(parents=True, exist_ok=True)
        production_dir = Path("production/application-3")
        production_dir.mkdir(parents=True, exist_ok=True)
        staging_file = staging_dir / "values-staging.yaml"
        staging_file.write_text("foo: bar-staging", encoding="utf8")
        production_file = production_dir / "values-production.yaml"
        assert not production_file.exists()
        repo.add(["staging"])
        repo.commit("Add staging's values file")
        promote_changes(repo)
        assert production_file.exists()
        content = production_file.read_text(encoding="utf8")
        assert "\nfoo: bar-production  # New key in source\n" in content
        # Simulate manual user changes
        content = content.replace(
            "foo: bar-production  # New key in source", "foo: bar"
        )
        production_file.write_text(content, encoding="utf8")
        repo.add(["production"])
        repo.commit("Manual production changes")

        promote_changes(repo)  # act

        result_content = production_file.read_text(encoding="utf8")
        # promote_changes is not trying to write again the changes as nothing has
        # changed
        assert "\nfoo: bar-production  # New key in source\n" not in result_content
        # promote_changes respects the user made changes.
        assert "\nfoo: bar\n" in result_content

    def test_promote_staging_secret_when_production_doesnt_exist(
        self, repo: "Git"
    ) -> None:
        file_name = "secrets.yaml"
        staging_file = Path("staging/application-3") / file_name
        save_sops_file(staging_file, "foo: bar")
        production_file = Path("production/application-3") / file_name
        assert not production_file.exists()
        repo.add(["staging"])
        repo.commit("Add staging's secret file")

        promote_changes(repo)  # act

        assert production_file.exists(), "the file was not created"
        result_content = load_sops_file(production_file)
        # Note: sops doesn't support yaml inline comments well. It adds
        # the comment before the key.
        assert "# New key in source\nfoo: bar" in result_content
