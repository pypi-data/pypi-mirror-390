"""Test the model."""

from argops.model import YamlDiff


class TestYamlDiffHasChanged:
    def test_has_changed_new_items(self) -> None:
        """Check has_changed returns True when new items are present."""
        result = YamlDiff(new=[("path.to.new", "new_value")]).has_changed

        assert result is True

    def test_has_changed_changed_items(self) -> None:
        """Check has_changed returns True when changed items are present."""
        result = YamlDiff(changed=[("path.to.changed", 123)]).has_changed

        assert result is True

    def test_has_changed_deleted_items(self) -> None:
        """Check has_changed returns True when deleted items are present."""
        result = YamlDiff(deleted=["path.to.deleted"]).has_changed

        assert result is True

    def test_has_changed_no_changes(self) -> None:
        """Check has_changed returns False when no changes are present."""
        result = YamlDiff(
            unchanged=[("path.to.unchanged", "unchanged_value")]
        ).has_changed

        assert result is False
