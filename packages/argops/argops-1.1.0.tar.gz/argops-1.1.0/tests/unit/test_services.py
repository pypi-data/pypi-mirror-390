"""Test the services."""

import logging
import os
import re
from collections import OrderedDict
from pathlib import Path
from textwrap import dedent
from typing import TYPE_CHECKING

import pytest
from _pytest.logging import LogCaptureFixture

from argops.services import (
    GREEN,
    RED,
    RESET,
    compare_yaml_contents,
    find_application_directories,
    get_content,
    get_last_promoted_commit_id,
    load_sops_file,
    promote_changes,
    replace_in_nested_object,
    save_sops_file,
    set_content,
    show_diff,
    update_values,
)

if TYPE_CHECKING:
    from argops.adapters.git import Git


class TestGetContent:

    def test_get_content(self, repo: "Git") -> None:
        result = get_content(repo, Path("test.yaml"))

        assert result == "key: value\n"

    def test_get_content_non_existent_file(
        self, repo: "Git", caplog: LogCaptureFixture
    ) -> None:
        """Test getting content of a non-existent file."""
        result = get_content(repo, Path("non_existent_file.yaml"))

        assert result == ""
        assert (
            "The 'non_existent_file.yaml' at commit 'HEAD' doesn't exist. "
            in caplog.text
        )

    def test_get_secret(self, repo: "Git") -> None:
        result = get_content(repo, Path("secrets.yaml"))

        assert "foo: bar" in result
        assert not (repo.path / "argops-temporal-secret.yaml").exists()

    def test_get_non_existent_secret(
        self, repo: "Git", caplog: LogCaptureFixture
    ) -> None:
        """Test getting content of a non-existent file."""
        result = get_content(repo, Path("non_existent_secrets.yaml"))

        assert result == ""
        assert (
            "The 'non_existent_secrets.yaml' at commit 'HEAD' doesn't exist. "
            in caplog.text
        )


class TestSetContent:

    def test_set_secrets_on_existent_file(self, repo: "Git") -> None:
        file_path = repo.path / "secrets.yaml"

        set_content(file_path, content="foo: bar")  # act

        assert "sops" in file_path.read_text(encoding="utf8")
        assert "foo: bar" in load_sops_file(file_path)

    def test_set_secrets_on_non_existent_file(self, repo: "Git") -> None:
        file_path = repo.path / "non-existent-secrets.yaml"

        set_content(file_path, content="foo: bar")  # act

        assert "sops" in file_path.read_text(encoding="utf8")
        assert "foo: bar" in load_sops_file(file_path)

    def test_set_secrets_idempotent_on_no_changes(self, repo: "Git") -> None:
        file_path = repo.path / "secrets.yaml"
        set_content(file_path, content="foo: bar")
        stored_content = file_path.read_text(encoding="utf8")

        set_content(
            file_path,
            content="foo: bar",
        )  # act

        assert file_path.read_text(encoding="utf8") == stored_content


class TestSaveSops:
    def test_save_sops_when_file_doesnt_exist(self, repo: "Git") -> None:
        file_path = repo.path / "new-secrets.yaml"

        save_sops_file(file_path, "foo: bar")  # act

        assert "foo: bar" in load_sops_file(file_path)


class TestCompareYamlContents:

    def test_new_property(self) -> None:
        yaml_content_1 = """
        key1: value1
        """
        yaml_content_2 = """
        key1: value1
        key2: value2
        """

        result = compare_yaml_contents(yaml_content_1, yaml_content_2)

        assert result.new == [("key2", "value2")]
        assert not result.changed
        assert not result.deleted
        assert result.unchanged == [("key1", "value1")]

    def test_new_property_from_empty(self) -> None:
        yaml_content_1 = ""
        yaml_content_2 = """
        key1: value1
        key2: value2
        """

        result = compare_yaml_contents(yaml_content_1, yaml_content_2)

        assert ("key1", "value1") in result.new
        assert ("key2", "value2") in result.new

    def test_changed_property(self) -> None:
        yaml_content_1 = """
        key1: value1
        key2: value2
        """
        yaml_content_2 = """
        key1: value1
        key2: new_value2
        """

        result = compare_yaml_contents(yaml_content_1, yaml_content_2)

        assert result.new == []
        assert result.changed == [("key2", "new_value2")]
        assert result.deleted == []
        assert result.unchanged == [("key1", "value1")]

    def test_deleted_property(self) -> None:
        yaml_content_1 = """
        key1: value1
        key2: value2
        """
        yaml_content_2 = """
        key1: value1
        """

        result = compare_yaml_contents(yaml_content_1, yaml_content_2)

        assert not result.new
        assert not result.changed
        assert result.deleted == ["key2"]
        assert result.unchanged == [("key1", "value1")]

    def test_deleted_all_properties(self) -> None:
        yaml_content_1 = """
        key1: value1
        key2: value2
        """
        yaml_content_2 = ""

        result = compare_yaml_contents(yaml_content_1, yaml_content_2)

        assert "key1" in result.deleted
        assert "key2" in result.deleted

    def test_multiple_changes(self) -> None:
        yaml_content_1 = """
        key1: value1
        key2: value2
        key3: value3
        """
        yaml_content_2 = """
        key1: new_value1
        key3: value3
        key4: value4
        """

        result = compare_yaml_contents(yaml_content_1, yaml_content_2)

        assert result.new == [("key4", "value4")]
        assert result.changed == [("key1", "new_value1")]
        assert result.deleted == ["key2"]
        assert result.unchanged == [("key3", "value3")]

    def test_no_changes(self) -> None:
        yaml_content_1 = """
        key1: value1
        key2: value2
        """
        yaml_content_2 = """
        key1: value1
        key2: value2
        """

        result = compare_yaml_contents(yaml_content_1, yaml_content_2)

        assert not result.new
        assert not result.changed
        assert not result.deleted
        # E1135: result.unchanged doesn't support membership test, but it does
        assert ("key1", "value1") in result.unchanged  # noqa: E1135
        assert ("key2", "value2") in result.unchanged  # noqa: E1135


@pytest.mark.usefixtures("set_current_dir")
class TestGetLastPromotedCommitId:
    def test_valid_commit_id_in_file(self, repo: "Git") -> None:
        file_path = repo.path / "values-staging.yaml"
        file_path.write_text("# Last promoted commit id: abc123", encoding="utf8")

        result = get_last_promoted_commit_id(repo, file_path)

        assert result == "abc123"

    def test_multiple_lines_with_commit_id(self, repo: "Git", work_dir: Path) -> None:
        file_path = work_dir / "values-staging.yaml"
        file_path.write_text(
            "some other line\n# Last promoted commit id: def456\nmore lines",
            encoding="utf8",
        )

        result = get_last_promoted_commit_id(repo, file_path)

        assert result == "def456"

    def test_no_commit_id_in_file(self, repo: "Git", work_dir: Path) -> None:
        file_path = work_dir / "values-staging.yaml"
        file_path.write_text("some other content\nwithout commit id", encoding="utf8")

        result = get_last_promoted_commit_id(repo, file_path)

        assert result is None

    def test_empty_file(self, repo: "Git", work_dir: Path) -> None:
        file_path = work_dir / "values-staging.yaml"
        file_path.write_text("", encoding="utf8")

        result = get_last_promoted_commit_id(repo, file_path)

        assert result is None

    def test_nonexistent_file(self, repo: "Git") -> None:
        file_path = Path("/path/to/nonexistent/file.yaml")

        result = get_last_promoted_commit_id(repo, file_path)

        assert result is None

    def test_sops_encrypted_file(self, repo: "Git") -> None:
        os.chdir("../sops")
        file_path = Path("secrets.yaml")

        result = get_last_promoted_commit_id(repo, file_path)

        assert result == "test_commit_id"


class TestUpdateValues:

    def test_update_values_with_empty_destination(self) -> None:
        last_promoted_source_content = dedent(
            """
        key1: value1
        key2: value2
        """
        )
        source_content = dedent(
            """
        key1: value1
        key2: updated_value2
        key3: value3
        """
        )
        destination_content = ""
        last_promoted_commit_id = "123abc"

        result = update_values(
            last_promoted_source_content,
            source_content,
            destination_content,
            last_promoted_commit_id,
        )

        expected_yaml = dedent(
            """\
        # Last promoted commit id: 123abc
        key1: value1  # New key in source
        key2: updated_value2 # New key in source
        key3: value3  # New key in source
        """
        )
        assert result.strip() == expected_yaml.strip()

    def test_update_values_with_empty_destination_and_unpromoted_source(self) -> None:
        last_promoted_source_content = ""
        source_content = dedent(
            """
        key1: value1
        key2: updated_value2
        key3: value3
        """
        )
        destination_content = ""
        last_promoted_commit_id = "123abc"

        result = update_values(
            last_promoted_source_content,
            source_content,
            destination_content,
            last_promoted_commit_id,
        )

        expected_yaml = dedent(
            """\
        # Last promoted commit id: 123abc
        key1: value1  # New key in source
        key2: updated_value2 # New key in source
        key3: value3 # New key in source
        """
        )
        assert result.strip() == expected_yaml.strip()

    def test_update_values_with_existing_destination(self) -> None:
        last_promoted_source_content = dedent(
            """
        key1: value1
        key2: value2
        """
        )
        source_content = dedent(
            """
        key1: value1
        key2: updated_value2
        key3: value3
        """
        )
        destination_content = dedent(
            """
        key1: value1
        key2: value2
        """
        )
        last_promoted_commit_id = "456def"

        result = update_values(
            last_promoted_source_content,
            source_content,
            destination_content,
            last_promoted_commit_id,
        )

        expected_yaml = dedent(
            """\
        # Last promoted commit id: 456def
        key1: value1
        key2: value2 # Key changed in source to updated_value2
        key3: value3  # New key in source
        """
        )
        assert result.strip() == expected_yaml.strip()

    def test_update_values_with_removed_content_in_source(self) -> None:
        last_promoted_source_content = dedent(
            """
        key1: value1
        key2: value2
        """
        )
        source_content = dedent(
            """
        key1: value1
        """
        )
        destination_content = dedent(
            """
        key1: value1
        key2: value2
        """
        )
        last_promoted_commit_id = "456def"

        result = update_values(
            last_promoted_source_content,
            source_content,
            destination_content,
            last_promoted_commit_id,
        )

        expected_yaml = dedent(
            """\
        # Last promoted commit id: 456def
        key1: value1
        key2: value2  # Key deleted in source
        """
        )
        assert result.strip() == expected_yaml.strip()

    def test_update_values_no_changes(self) -> None:
        last_promoted_source_content = dedent(
            """
        key1: value1
        key2: value2
        """
        )
        source_content = dedent(
            """
        key1: value1
        key2: value2
        """
        )
        destination_content = dedent(
            """
        # Last promoted commit id: 789ghi
        key1: value1
        key2: value2
        """
        )
        last_promoted_commit_id = "789ghi"

        result = update_values(
            last_promoted_source_content,
            source_content,
            destination_content,
            last_promoted_commit_id,
        )

        expected_yaml = dedent(
            """\
        # Last promoted commit id: 789ghi
        key1: value1
        key2: value2
        """
        )
        assert result.strip() == expected_yaml.strip()

    def test_update_values_no_changes_on_last_commit(self) -> None:
        """
        We don't want to change the last_promoted_commit_id if the file has not
        changed since then. Otherwise each time we do a promote all the values files
        of the repository will have a line change, which will twarten the pull request
        reviews.
        """
        last_promoted_source_content = dedent(
            """
        key1: value1
        key2: value2
        """
        )
        source_content = dedent(
            """
        key1: value1
        key2: value2
        """
        )
        destination_content = dedent(
            """
            # Last promoted commit id: a_previous_commit
        key1: value1
        key2: value2
        """
        )
        last_promoted_commit_id = "789ghi"

        result = update_values(
            last_promoted_source_content,
            source_content,
            destination_content,
            last_promoted_commit_id,
        )

        expected_yaml = dedent(
            """\
        # Last promoted commit id: a_previous_commit
        key1: value1
        key2: value2
        """
        )
        assert result.strip() == expected_yaml.strip()

    def test_update_values_with_nested_values(self) -> None:
        last_promoted_source_content = dedent(
            """
        parent:
          child1: value1
          child2: value2
        """
        )
        source_content = dedent(
            """
        parent:
          child1: value1
          child2: updated_value2
          child3: value3
        """
        )
        destination_content = dedent(
            """
        parent:
          child1: value1
          child2: value2
        """
        )
        last_promoted_commit_id = "789xyz"

        result = update_values(
            last_promoted_source_content,
            source_content,
            destination_content,
            last_promoted_commit_id,
        )

        assert re.search(
            r"child2: value2\s+# Key changed in source to updated_value2", result
        )
        assert re.search(r"child3: value3\s+# New key in source", result)

    def test_update_values_with_nested_deletions(self) -> None:
        last_promoted_source_content = dedent(
            """
        parent:
          child1: value1
          child2: value2
          child3: value3
        """
        )
        source_content = dedent(
            """
        parent:
          child1: value1
        """
        )
        destination_content = dedent(
            """
        parent:
          child1: value1
          child2: value2
          child3: value3
        """
        )
        last_promoted_commit_id = "abc456"

        result = update_values(
            last_promoted_source_content,
            source_content,
            destination_content,
            last_promoted_commit_id,
        )

        assert re.search(r"child2: value2\s+# Key deleted in source", result)
        assert re.search(r"child3: value3\s+# Key deleted in source", result)


class TestShowDiff:
    def test_no_difference(self, caplog: LogCaptureFixture) -> None:
        src = "Hello\nWorld\n"
        dest = "Hello\nWorld\n"

        show_diff(src, dest)  # act

        assert len(caplog.records) == 0

    def test_added_line(self, caplog: LogCaptureFixture) -> None:
        caplog.set_level(logging.DEBUG)
        src = "Hello\nWorld\nNew line"
        dest = "Hello\nWorld"

        show_diff(src, dest)  # act

        assert (
            "argops.services",
            logging.INFO,
            f"{GREEN}+New line{RESET}",
        ) in caplog.record_tuples

    def test_removed_line(self, caplog: LogCaptureFixture) -> None:
        caplog.set_level(logging.DEBUG)
        src = "Hello\nWorld"
        dest = "Hello\nWorld\nRemoved line"

        show_diff(src, dest)  # act

        assert (
            "argops.services",
            logging.INFO,
            f"{RED}-Removed line{RESET}",
        ) in caplog.record_tuples


@pytest.mark.usefixtures("set_current_dir")
class TestFindApplicationDirectories:
    def test_no_filters_returns_all_applications(self) -> None:
        result = find_application_directories(filters=[])

        assert len(result) == 3

    def test_single_filter_valid_result(self) -> None:
        result = find_application_directories(filters=["application-1"])

        assert len(result) == 1
        assert result[0] == Path("staging/application-set-1/application-1")

    def test_multiple_filters_valid_result(self) -> None:
        result = find_application_directories(
            filters=["application-1", "application-3"]
        )

        assert len(result) == 2
        assert Path("staging/application-set-1/application-1") in result
        assert Path("staging/application-3") in result

    def test_no_applications_found_raises_value_error(self) -> None:
        with pytest.raises(
            ValueError,
            match="No application was found with the selected filters: non-existent",
        ):
            find_application_directories(filters=["non-existent"])

    def test_application_set_filter(self) -> None:
        result = find_application_directories(filters=["application-set-1"])

        assert len(result) == 2
        assert Path("staging/application-set-1/application-1") in result
        assert Path("staging/application-set-1/application-2") in result

    def test_no_filters_returns_all_applications_under_application_set_cwd(
        self,
    ) -> None:
        result = find_application_directories(
            filters=[], start_dir=Path("staging/application-set-1")
        )

        assert len(result) == 2
        assert Path("staging/application-set-1/application-1") in result
        assert Path("staging/application-set-1/application-2") in result

    def test_no_filters_returns_all_applications_under_application_cwd(self) -> None:
        result = find_application_directories(
            filters=[], start_dir=Path("staging/application-3")
        )

        assert len(result) == 1
        assert Path("staging/application-3") in result


@pytest.mark.usefixtures("set_current_dir")
class TestPromoteChanges:
    def test_promote_changes_when_cwd_is_application_dir(
        self, repo: "Git", work_dir: Path
    ) -> None:
        production_path = Path("production/application-3")
        os.chdir("staging/application-3")
        assert not production_path.exists()

        promote_changes(repo)  # act

        assert production_path.exists()
        assert not (work_dir / "production" / "application-set-1").exists()

    def test_promote_changes_when_cwd_is_application_set_dir(
        self, repo: "Git", work_dir: Path
    ) -> None:
        production_paths = [
            Path("production/application-set-1/application-1"),
            Path("production/application-set-1/application-2"),
        ]
        os.chdir("staging/application-set-1")
        assert not production_paths[0].exists()
        assert not production_paths[1].exists()

        promote_changes(repo)  # act

        assert production_paths[0].exists()
        assert production_paths[1].exists()
        assert not (work_dir / "production" / "application-3").exists()

    def test_promote_changes_when_cwd_is_application_set_dir_and_has_filter(
        self, repo: "Git", work_dir: Path
    ) -> None:
        production_paths = [
            Path("production/application-set-1/application-1"),
            Path("production/application-set-1/application-2"),
        ]
        os.chdir("staging/application-set-1")
        assert not production_paths[0].exists()
        assert not production_paths[1].exists()

        promote_changes(repo, filters=["application-1"])  # act

        assert production_paths[0].exists()
        assert not production_paths[1].exists()
        assert not (work_dir / "production" / "application-3").exists()

    def test_promote_changes_when_cwd_is_environment_dir(
        self,
        repo: "Git",
    ) -> None:
        production_paths = [
            Path("production/application-set-1/application-1"),
            Path("production/application-set-1/application-2"),
            Path("production/application-3"),
        ]
        os.chdir("staging")
        assert not production_paths[0].exists()
        assert not production_paths[1].exists()
        assert not production_paths[2].exists()

        promote_changes(repo)  # act

        assert production_paths[0].exists()
        assert production_paths[1].exists()
        assert production_paths[2].exists()

    def test_promote_changes_when_cwd_is_root_dir(
        self,
        repo: "Git",
    ) -> None:
        production_paths = [
            Path("production/application-set-1/application-1"),
            Path("production/application-set-1/application-2"),
            Path("production/application-3"),
        ]
        assert not production_paths[0].exists()
        assert not production_paths[1].exists()
        assert not production_paths[2].exists()

        promote_changes(repo)  # act

        assert production_paths[0].exists()
        assert production_paths[1].exists()
        assert production_paths[2].exists()


class TestReplaceInNestedObject:
    def test_replace_string(self) -> None:
        input_str = "hello world"

        result = replace_in_nested_object(input_str, "hello", "hi")

        assert result == "hi world"

    def test_replace_nested_dict(self) -> None:
        input_dict = {"key1": "hello world", "key2": {"nested": "hello python"}}

        result = replace_in_nested_object(input_dict, "hello", "hi")

        assert result == {"key1": "hi world", "key2": {"nested": "hi python"}}

    def test_replace_ordered_dict(self) -> None:
        input_ordered_dict = OrderedDict(
            [
                ("key1", "hello world"),
                ("key2", OrderedDict([("nested", "hello python")])),
            ]
        )

        result = replace_in_nested_object(input_ordered_dict, "hello", "hi")

        assert result == OrderedDict(
            [("key1", "hi world"), ("key2", OrderedDict([("nested", "hi python")]))]
        )

    def test_replace_list(self) -> None:
        input_list = ["hello world", "hello python"]

        result = replace_in_nested_object(input_list, "hello", "hi")

        assert result == ["hi world", "hi python"]

    def test_replace_nested_list(self) -> None:
        input_nested_list = ["hello world", {"nested": "hello python"}, ["hello list"]]

        result = replace_in_nested_object(input_nested_list, "hello", "hi")

        assert result == ["hi world", {"nested": "hi python"}, ["hi list"]]

    def test_replace_tuple(self) -> None:
        input_tuple = ("hello world", "hello python")

        result = replace_in_nested_object(input_tuple, "hello", "hi")

        assert result == ("hi world", "hi python")

    def test_no_replacement_needed(self) -> None:
        input_dict = {"key1": "world", "key2": {"nested": "python"}}

        result = replace_in_nested_object(input_dict, "hello", "hi")

        assert result == input_dict

    def test_replace_multiple_occurrences(self) -> None:
        input_str = "hello hello world"

        result = replace_in_nested_object(input_str, "hello", "hi")

        assert result == "hi hi world"

    def test_replace_with_empty_string(self) -> None:
        input_dict = {"key1": "hello world", "key2": {"nested": "hello python"}}

        result = replace_in_nested_object(input_dict, "hello ", "")

        assert result == {"key1": "world", "key2": {"nested": "python"}}

    def test_preserves_non_string_types(self) -> None:
        input_dict = {"key1": "hello world", "key2": 42, "key3": [1, 2, 3]}

        result = replace_in_nested_object(input_dict, "hello", "hi")

        assert result == {"key1": "hi world", "key2": 42, "key3": [1, 2, 3]}
