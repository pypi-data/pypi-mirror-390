"""Define the Git adapter."""

import logging
from contextlib import suppress
from pathlib import Path
from typing import Any, Dict, List, Optional

import git
from git.exc import GitCommandError, InvalidGitRepositoryError, NoSuchPathError

log = logging.getLogger(__name__)


class GitRepositoryError(Exception):
    """Custom exception for Git repository errors."""


class NoRemoteTrackingBranchError(Exception):
    """Custom exception for branches that are no present on the remote."""


class Git:
    """A Python adapter for interacting with the Git repository."""

    def __init__(self, repo_path: Optional[Path] = None, init: bool = False) -> None:
        """Initialize the object."""
        if not repo_path:
            repo_path = Path(".")
        self.path = repo_path
        if init:
            self.repo = git.Repo.init(repo_path)
        else:
            try:
                self.repo = git.Repo(self.find_repo_root(repo_path))
            except InvalidGitRepositoryError as e:
                raise GitRepositoryError(
                    f"Invalid Git repository at path: {repo_path}"
                ) from e
            except NoSuchPathError as e:
                raise GitRepositoryError(f"Path does not exist: {repo_path}") from e

    def add(self, elements: List[str]) -> None:
        """Stage the changes."""
        self.repo.index.add(elements)

    def create_branch(self, name: str) -> None:
        """Create a new branch and check it out."""
        new_branch = self.repo.create_head(name)
        self.repo.git.checkout(new_branch)

    def change_branch(self, name: str) -> None:
        """Change the active git branch.

        Raises:
            GitRepositoryError: If there is an issue accessing the repository
                or retrieving the commit information.
        """
        try:
            if self.current_branch == name:
                return

            # Get the current branch
            self.repo.git.checkout(name)
        except Exception as e:
            raise GitRepositoryError(
                f"Error changing to the git branch {name}: {e}"
            ) from e

    def commit(self, message: str) -> None:
        """Make a commit with the staged changes."""
        self.repo.index.commit(message)

    def fetch(self) -> None:
        """Fetch the new commits from the origin remote."""
        self.repo.remotes.origin.fetch()

    def push(self) -> None:
        """Push current branch to remote, setting upstream if needed.

        Attempts to push to origin if the remote branch is not tracked.
        """
        push_info = self.repo.remotes.origin.push(self.current_branch)
        push_info.raise_if_error()
        log.debug(f"Successfully pushed to {self.repo.active_branch.name}")

    def merge_branch(self, branch_name: str) -> None:
        """Merge the specified branch into the current branch.

        Args:
            branch_name: Name of the branch to merge from

        Raises:
            GitRepositoryError: If the merge operation fails
        """
        try:
            self.repo.git.merge(branch_name)
        except git.GitCommandError as e:
            raise GitRepositoryError(
                f"Failed to merge branch '{branch_name}': {str(e)}"
            ) from e

    def delete_branch(self, branch_name: str, remote: bool = True) -> None:
        """Delete the specified branch locally and optionally from the remote.

        Args:
            branch_name: Name of the branch to delete
            remote: Whether to also delete the branch from the remote 'origin'

        Raises:
            GitRepositoryError: If the branch deletion fails
        """
        try:
            # Delete local branch
            with suppress(GitCommandError):
                self.repo.git.branch("-D", branch_name)

            # Delete remote branch if requested
            if remote:
                self.repo.git.push("origin", "--delete", branch_name)
        except git.GitCommandError as e:
            raise GitRepositoryError(
                f"Failed to delete branch '{branch_name}': {str(e)}"
            ) from e

    def update_main(self) -> None:
        """Pull changes from remote main branch and merge them if needed.

        Will first fetch all remote changes and then merge only if necessary.
        Stashes any uncommitted changes before merging and restores them afterward.
        """
        # Fetch the latest changes from remote
        self.fetch()

        # Get references to local and remote main branches
        local_main = self.repo.heads.main
        remote_main = self.repo.remotes.origin.refs.main

        # Check if there are uncommitted changes
        has_uncommitted_changes = (
            self.repo.is_dirty() or len(self.repo.untracked_files) > 0
        )

        # Stash changes if needed
        if has_uncommitted_changes:
            log.debug("Stashing uncommitted changes")
            stash_result = self.repo.git.stash(
                "push", "-u", "-m", "Auto-stash before updating main"
            )
            log.debug(f"Stash result: {stash_result}")

        # Check if we need to merge (if local is behind remote)
        if local_main.commit != remote_main.commit:
            # Check if we're on main branch
            current_branch = self.repo.active_branch
            previous_branch = current_branch

            if current_branch.name != "main":
                # Checkout main branch
                local_main.checkout()

            # Perform the merge
            merge_result = self.repo.git.merge(remote_main.name)

            # Log the result
            log.debug(f"Merged remote main: {merge_result}")

            # Return to previous branch if we switched
            if previous_branch.name != "main":
                # Checkout main branch
                previous_branch.checkout()
        else:
            log.debug("Local main is already up to date")

        # Pop stash if we stashed changes
        if has_uncommitted_changes:
            log.debug("Restoring stashed changes")
            stash_pop_result = self.repo.git.stash("pop")
            log.debug(f"Stash pop result: {stash_pop_result}")

    @property
    def branch_status(self) -> tuple[list[git.Commit], list[git.Commit]]:
        """Check if the current branch is up-to-date with its remote tracking branch.

        Returns:
            tuple[list[git.Commit], list[git.Commit]]: A tuple containing two lists:
                - The first list contains commits that the local branch is behind
                - The second list contains commits that the local branch is ahead

        Raises:
            NoRemoteTrackingBranchError: If the current branch has no remote
                tracking branch
        """
        current_branch = self.repo.active_branch
        tracking_branch = self.repo.active_branch.tracking_branch()

        if tracking_branch is None:
            raise NoRemoteTrackingBranchError(
                f"The current branch {current_branch.name} has no remote "
                "tracking branch"
            )

        # Fetch the latest changes from remote
        log.debug(
            f"Fetching latest changes from origin for branch {current_branch.name}"
        )
        self.fetch()

        # Compare commits between local and remote
        log.debug(
            f"Comparing commits between {current_branch.name} and "
            f"{tracking_branch.name}"
        )
        commits_behind = list(
            self.repo.iter_commits(f"{current_branch.name}..{tracking_branch.name}")
        )
        commits_ahead = list(
            self.repo.iter_commits(f"{tracking_branch.name}..{current_branch.name}")
        )

        if not commits_behind:
            log.debug(
                f"Branch '{current_branch.name}' is up-to-date with "
                f"'{tracking_branch.name}'"
            )
        else:
            log.debug(
                f"Branch '{current_branch.name}' is behind by "
                f"{len(commits_behind)} commits"
            )

        if commits_ahead:
            log.debug(
                f"Branch '{current_branch.name}' is ahead by "
                f"{len(commits_ahead)} commits"
            )

        return commits_behind, commits_ahead

    @property
    def branch_is_behind_origin(self) -> bool:
        """Check if the current branch is behind its remote tracking branch.

        Returns:
            bool: True if the branch is behind its remote tracking branch,
                False otherwise

        Raises:
            GitRepositoryError: If the current branch has no remote tracking
                branch
        """
        commits_behind, _ = self.branch_status

        is_behind = len(commits_behind) > 0
        return is_behind

    @property
    def branch_is_ahead_origin(self) -> bool:
        """Check if the current branch is ahead of its remote tracking branch.

        Returns:
            bool: True if the branch is ahead of its remote tracking branch,
                False otherwise

        Raises:
            GitRepositoryError: If the current branch has no remote tracking
                branch
        """
        _, commits_ahead = self.branch_status

        is_ahead = len(commits_ahead) > 0
        return is_ahead

    @property
    def current_commit_id(self) -> str:
        """Get the current commit ID. The one at HEAD.

        Returns:
            str: The current commit ID.

        Raises:
            GitRepositoryError: If there is an issue accessing the repository
                or retrieving the commit ID.
        """
        try:
            current_commit = self.repo.head.commit
            return current_commit.hexsha
        except Exception as e:
            raise GitRepositoryError(
                f"Error retrieving the current commit ID: {e}"
            ) from e

    @property
    def current_branch(self) -> str:
        """Get the active branch.

        Returns:
            str: The current branch name.

        Raises:
            GitRepositoryError: If there is an issue accessing the repository
                or retrieving the branch.
        """
        try:
            return self.repo.active_branch.name
        except Exception as e:
            raise GitRepositoryError(f"Error retrieving the active branch: {e}") from e

    @property
    def branch_id(self) -> str:
        """Get the branch ID.

        If the current branch is 'main', returns the current commit ID.
        Otherwise, returns the commit ID where the current branch was
        created from (usually main).

        Returns:
            str: The branch ID.

        Raises:
            GitRepositoryError: If there is an issue accessing the repository
                or retrieving the commit information.
        """
        try:
            # If current branch is 'main', return current commit id
            if self.current_branch == "main":
                return self.current_commit_id

            # Get the current branch
            branch = self.repo.heads[self.current_branch]

            # Get the commit where the branch was created from
            # This finds the merge-base (common ancestor) between the current branch
            # and main
            main_branch = self.repo.heads["main"]
            merge_base = self.repo.git.merge_base(branch.commit, main_branch.commit)

            return merge_base
        except Exception as e:
            raise GitRepositoryError(f"Error retrieving the branch ID: {e}") from e

    def find_repo_root(self, start_path: Path) -> Path:
        """Traverse the directory tree upwards until finding the .git directory.

        Args:
            start_path: Path to start the search from

        Returns:
            Path to the repository root or None if not found
        """
        current = start_path.absolute()

        # Traverse up until we find .git directory or reach the filesystem root
        while current != current.parent:
            git_dir = current / ".git"
            if git_dir.exists() and git_dir.is_dir():
                return current
            current = current.parent

        raise GitRepositoryError(
            f"Could not find a git repository from the directory {start_path}"
        )

    def get_content(self, file_path: Path, commit_id: str = "HEAD") -> str:
        """Get the content of a file on a defined commit.

        If the file doesn't belong to a git repository it will return the
        content of the file.
        """
        try:
            commit = self.repo.commit(commit_id)
            blob = commit.tree / str(file_path)
            commit_content = blob.data_stream.read().decode("utf-8")
        except KeyError as e:
            log.warning(
                f"The '{file_path}' at commit '{commit_id}' doesn't exist. "
                f"Returning the content of the file directly: {e}"
            )
            commit_content = file_path.read_text(encoding="utf8")
        return commit_content

    def get_merge_commits(
        self, source_branch: str, destination_branch: str = "main"
    ) -> str:
        """Retrieve and format commits that would be merged from source to destination branch.

        Args:
            source_branch (str): The name of the source branch to merge from
            destination_branch (str): The name of the destination branch to merge into

        Returns:
            str: A formatted string containing commit titles and bodies
        """
        try:
            # Get the merge base to find common ancestor
            merge_base = self.repo.git.merge_base(source_branch, destination_branch)

            # Get commits between merge base and source branch
            commits = self.repo.git.rev_list(
                f"{merge_base}..{source_branch}", no_merges=True
            ).splitlines()

            # Collect commit details
            commit_details = []
            for commit_hash in commits:
                commit = self.repo.commit(commit_hash)

                # Format commit title and body
                if isinstance(commit.summary, bytes):
                    summary = commit.summary.decode("utf-8").strip()
                else:
                    summary = commit.summary.strip()
                if isinstance(commit.message, bytes):
                    message = commit.message.decode("utf-8").strip()
                else:
                    message = commit.message.strip()
                commit_info = f"{summary} ({commit.hexsha[:7]})\n"

                # Only add body if it exists and is different from summary
                if message != summary:
                    commit_info += f"\n{message}\n"

                commit_details.append(commit_info)

            # Join commits with separators
            return (
                "\n---\n".join(commit_details)
                if commit_details
                else "No commits to merge."
            )

        except (GitCommandError, KeyError) as e:
            log.error(f"Error retrieving commits: {str(e)}")
            raise e

    def check_clean_state(self) -> Dict[str, Any]:
        """Check if the repository is in a clean state.

        Determines if the repository has any staged, unstaged, or untracked changes.

        Returns:
            Dict[str, Any]: Repository state containing:
                - is_clean (bool): True if repository is clean, False otherwise
                - staged_changes (List): List of staged changes
                - unstaged_changes (List): List of unstaged changes
                - untracked_files (List): List of untracked files
        """
        log.debug("Checking repository clean state")

        # Prepare return data structure
        state = {
            "is_clean": True,
            "staged_changes": [],
            "unstaged_changes": [],
            "untracked_files": [],
        }

        # Check staged changes
        staged_changes = self.repo.index.diff("HEAD")
        if staged_changes:
            log.debug(f"Found {len(staged_changes)} staged changes")
            state["is_clean"] = False
            for item in staged_changes:
                change_type = self._get_change_type(item)
                if isinstance(state["unstaged_changes"], list):
                    # ignore: error: "object" has no attribute "append"
                    # but I made sure it's a list
                    state["staged_changes"].append(  # type: ignore
                        {"type": change_type, "path": item.a_path}
                    )
                else:
                    raise ValueError(
                        f"The state['unstaged_changes'] is not a list "
                        f"but {type(state['unstaged_changes'])}"
                    )

        # Check unstaged changes
        unstaged_changes = self.repo.index.diff(None)
        if unstaged_changes:
            log.debug(f"Found {len(unstaged_changes)} unstaged changes")
            state["is_clean"] = False
            for item in unstaged_changes:
                change_type = self._get_change_type(item)
                if isinstance(state["unstaged_changes"], list):
                    state["unstaged_changes"].append(
                        {"type": change_type, "path": item.a_path}
                    )
                else:
                    raise ValueError(
                        f"The state['unstaged_changes'] is not a list "
                        f"but {type(state['unstaged_changes'])}"
                    )

        # Check untracked files
        untracked_files = self.repo.untracked_files
        if untracked_files:
            log.debug(f"Found {len(untracked_files)} untracked files")
            state["is_clean"] = False
            state["untracked_files"] = untracked_files

        log.info(f"Repository clean state check result: {state['is_clean']}")
        return state

    @property
    def origin_url(self) -> str:
        """Get the origin_url."""
        try:
            return list(self.repo.remotes.origin.urls)[0]
        except Exception as e:
            raise GitRepositoryError(f"Error retrieving the url of origin: {e}") from e

    def _get_change_type(self, diff_item: Any) -> str:
        """Helper method to determine the type of change for a diff item.

        Args:
            diff_item: A GitPython diff item object.

        Returns:
            str: String description of the change type.
        """
        log.debug(f"Determining change type for {diff_item.a_path}")
        if diff_item.new_file:
            return "new file"
        if diff_item.deleted_file:
            return "deleted"
        if diff_item.renamed:
            return "renamed"
        return "modified"
