"""Define the Gitea adapter."""

import logging
import re
import shutil
import time
from contextlib import suppress
from typing import List, Optional, Tuple

from argops.adapters.console import Command
from argops.exceptions import TeaConfigurationError, TeaRuntimeError

log = logging.getLogger(__name__)


class Gitea(Command):
    """A Python adapter for interacting with the Gitea command line interface."""

    # W0221: Number of parameters was 3 in 'Command.check' and is now 2
    # in overriding 'Gitea.check' but this is expected
    def check(self, origin_url: str) -> None:  # noqa: W0221
        """Check if tea is well configured.

        This method verifies:
        1. tea is in the path
        2. the profile name is part of the origin_url. Which means that the
            correct profile is set

        Raises:
           TeaConfigurationError  if it's not well configured
        """
        log.debug("Checking that tea binary is present")
        tea_path = shutil.which("tea")
        if tea_path:
            log.debug(f"tea CLI found at: {tea_path}")
        else:
            raise TeaConfigurationError("tea CLI not found in PATH")

        log.debug(f"Checking that the tea profile matches the origin_url: {origin_url}")
        if self.default_profile not in origin_url:
            log.debug("Setting a tea profile that matches the origin_url")
            matching_profiles = [
                profile for profile in self.profiles if profile in origin_url
            ]
            if len(matching_profiles) > 1:
                raise TeaConfigurationError(
                    f"More than one tea login profile matched the origin_url "
                    f"{origin_url}: {', '.join(matching_profiles)}. "
                    "Please change your profile names so that only one is selected."
                )
            if len(matching_profiles) == 0:
                raise TeaConfigurationError(
                    f"No tea login profile matched the origin_url {origin_url}. "
                    "Please use tea login to add such a profile"
                )
            self.set_default_profile(matching_profiles[0])

    def get_repo_id(self, origin_url: str) -> str:
        """Get the gitea repo id from the origin_url.

        Args:
            origin_url (str): The URL of the git repository (SSH or HTTPS format)

        Returns:
            str: The repository ID in the format 'username/repository'
        """
        # Regex for SSH format (git@domain:username/repo.git)
        ssh_pattern = r"^git@[^:]+:([^/]+/[^/.]+)(?:\.git)?$"

        # Regex for HTTPS format (https://domain/username/repo)
        https_pattern = r"^https://[^/]+/([^/]+/[^/]+)/?$"

        # Try SSH pattern first
        ssh_match = re.match(ssh_pattern, origin_url)
        if ssh_match:
            return ssh_match.group(1)

        # Then try HTTPS pattern
        https_match = re.match(https_pattern, origin_url)
        if https_match:
            return https_match.group(1)

        raise ValueError(f"Unable to extract repository ID from URL: {origin_url}")

    def create_merge_request(
        self, origin_url: str, branch_name: str, title: str, description: str
    ) -> str:
        """Open a merge request.

        Args:
            origin_url (str): The URL of the git repository (SSH or HTTPS format)

        Returns:
            the merge request url

        """
        command = [
            "tea",
            "pr",
            "create",
            "--repo",
            self.get_repo_id(origin_url),
            "--title",
            title,
            "--description",
            description,
            "--head",
            branch_name,
        ]
        _, stdout, _ = self._run_command(command)
        return stdout.splitlines()[-1]

    def merge_requests(self, origin_url: str) -> List[List[str]]:
        """Return the open merge requests.

        Args:
            origin_url (str): The URL of the git repository (SSH or HTTPS format)

        Returns:
            List of title, source branch, and url

        """
        command = [
            "tea",
            "pr",
            "list",
            "--fields",
            "title,head,url",
            "--repo",
            self.get_repo_id(origin_url),
            "--output",
            "csv",
        ]
        _, stdout, _ = self._run_command(command)
        merge_requests = []
        for merge in stdout.splitlines()[1:]:
            merge_request = []
            for element in merge.split(","):
                merge_request.append(element.replace('"', ""))
            merge_requests.append(merge_request)
        return merge_requests

    def get_merge_request_url(self, origin_url: str, branch: str) -> Optional[str]:
        """Return the merge request url if it exists."""
        for merge_request in self.merge_requests(origin_url):
            if merge_request[1] == branch:
                return merge_request[2]
        return None

    def merge_request_exists(self, origin_url: str, branch: str) -> bool:
        """Check if the merge request already exists."""
        return self.get_merge_request_url(origin_url, branch) is not None

    def merge_merge_request(self, merge_request_url: str) -> None:
        """Merge a merge request waiting until it's closed.

        Args:
            merge_request_url (str): The URL of the gitea merge request
        """
        pattern = r"(https?://[^/]+)/([^/]+/[^/]+)/pulls/(\d+)"

        # Match the pattern
        match = re.match(pattern, merge_request_url)

        if match:
            domain_url = match.group(1)
            repo = match.group(2)
            merge_request_number = int(match.group(3))
        else:
            raise ValueError(
                "Could not extract the repo and merge request number from url "
                f"{merge_request_url}"
            )
        command = [
            "tea",
            "pr",
            "merge",
            "--repo",
            repo,
            str(merge_request_number),
        ]
        while True:
            with suppress(TeaConfigurationError):
                # Try to merge the merge request. If it has some CI jobs that need
                # to pass before it's mergable, then it will return an exit code 1
                self._run_command(command)
            time.sleep(1)
            open_requests = self.merge_requests(origin_url=f"{domain_url}/{repo}")
            # Exit when the pull request is no longer open
            if not any(
                str(merge_request_number) in request[2] for request in open_requests
            ):
                break

    @property
    def profiles(self) -> List[str]:
        """Return the profile names."""
        command = ["tea", "login", "list", "--output", "simple"]
        _, stdout, _ = self._run_command(command)
        profiles = [line.split()[0] for line in stdout.splitlines()]
        return profiles

    @property
    def default_profile(self) -> str:
        """Return the default profile name."""
        command = ["tea", "login", "default"]
        _, stdout, _ = self._run_command(command)
        default_profile = stdout.split(":")[1]
        return default_profile

    def set_default_profile(self, name: str) -> None:
        """Set the tea default profile."""
        command = ["tea", "login", "default", name]
        self._run_command(command)

    def _run_command(
        self, command: List[str], retries: int = 0
    ) -> Tuple[int, str, str]:
        """Run a command and return the result.

        Args:
            command: The command to run as a list of strings.

        Returns:
            A tuple containing (return_code, stdout, stderr).
        """
        return_code, stdout, stderr = super()._run_command(command, retries)
        if return_code != 0:
            raise TeaRuntimeError(
                f"Error {return_code} running command {' '.join(command)}: {stderr}"
            )
        return return_code, stdout, stderr
