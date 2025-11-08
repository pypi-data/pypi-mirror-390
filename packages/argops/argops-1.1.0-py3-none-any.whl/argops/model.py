"""Define the data models of the program."""

import logging
from typing import Any, List, Tuple

from pydantic import BaseModel, Field

log = logging.getLogger(__name__)


class YamlDiff(BaseModel):
    """Model of a difference between two yaml source files.

    Attributes:
        unchanged (List[Tuple[str, Any]]): A list of tuples containing the path
            and value of unchanged items.
        new (List[Tuple[str, Any]]): A list of tuples containing the path
            and value of new items.
        changed (List[Tuple[str, Any]]): A list of tuples containing the path
            and value of changed items.
        deleted (List[str]): A list of strings containing the paths of deleted items.
    """

    unchanged: List[Tuple[str, Any]] = Field(default_factory=list)
    new: List[Tuple[str, Any]] = Field(default_factory=list)
    changed: List[Tuple[str, Any]] = Field(default_factory=list)
    deleted: List[str] = Field(default_factory=list)

    @property
    def has_changed(self) -> bool:
        """Check if there are any changes in the YamlDiff model.

        Returns:
            bool: True if new, changed, or deleted lists have items; False otherwise.
        """
        return len(self.new) > 0 or len(self.changed) > 0 or len(self.deleted) > 0
