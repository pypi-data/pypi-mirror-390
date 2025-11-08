"""Define the Command interface."""

import contextlib
import logging
import os
import re
import subprocess
import tempfile
from typing import Any, Dict, List, Optional, Tuple

import questionary
from rich.console import Console as RichConsole
from rich.panel import Panel

log = logging.getLogger(__name__)


class Command:
    """A python adapter for interacting with a command line interface."""

    def _run_command(
        self, command: List[str], retries: int = 0
    ) -> Tuple[int, str, str]:
        """Run a command and return the result.

        Args:
            command: The command to run as a list of strings.
            retries: number of retries in case of failure

        Returns:
            A tuple containing (return_code, stdout, stderr).
        """
        log.debug(f"Running command: {' '.join(command)}")
        try:
            while True:
                with subprocess.Popen(
                    command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
                ) as process:
                    stdout, stderr = process.communicate()
                if process.returncode == 0 or retries <= 0:
                    log.debug(f"Command returned with exit code: {process.returncode}")
                    return process.returncode, stdout, stderr
                log.warning(
                    f"Command {' '.join(command)} returned with exit code: "
                    f"{process.returncode}\n stdout: {stdout}\n stderr: {stderr}"
                    "\nRetrying..."
                )
        except Exception as e:  # noqa: W0718
            # W0718 Catching too general exception Exception
            # (broad-exception-caught) [pylint]
            log.error(f"Error running command: {e}")
            return -1, "", str(e)

    def check(self, *args: Any, **kwargs: Any) -> None:
        """Check if <command> is well configured.

        This method verifies:
        1.

        Raises:
            <exception> if it's not well configured
        """
        raise NotImplementedError


class Console:
    """Console adapter for Git operations with rich output."""

    def __init__(self) -> None:
        """Initialize a GitConsole object."""
        log.debug("Initializing the Console")
        self.console = RichConsole()

    def bell(self) -> None:
        """Trigger the terminal bell."""
        print("\a", end="")

    def print(self, objects: Any, pad: bool = True) -> None:
        """Print a message."""
        if isinstance(objects, str) and pad:
            objects = f"  {objects}"
        self.console.print(objects)

    def print_check(self, message: str) -> None:
        """Print a success message."""
        self.print(f"[green]✓[/green] {message}", pad=False)

    def print_fail(self, message: str) -> None:
        """Print a failed message."""
        self.print(f"[red]✗[/red] {message}", pad=False)

    @contextlib.contextmanager
    def print_process(
        self,
        initial_message: str,
        success_message: Optional[str] = None,
        failure_message: Optional[str] = None,
    ) -> Any:
        """Display a process with a spinner, success, or failure status.

        This context manager shows a spinner while the process is running,
        then displays either a success or failure message based on whether
        an exception was raised.

        Args:
            initial_message: Message to display when starting the process
            success_message: Message to display when process completes successfully
            failure_message: Message to display when process fails

        Yields:
            None: This context manager doesn't yield a value

        Example:
            ```python
            console = Console()
            try:
                with console.print_process(
                    "Cloning repository...",
                    "Repository cloned successfully",
                    "Failed to clone repository"
                ):
                    # Some code that might raise an exception
                    git.clone("https://github.com/example/repo.git")
            except Exception as e:
                log.error(f"Error during git operation: {e}")
            ```
        """
        log.debug(f"Starting process: {initial_message}")
        success_message = success_message or initial_message
        failure_message = failure_message or initial_message
        try:
            with self.console.status(initial_message):
                yield
            log.debug(f"Process completed successfully: {success_message}")
            self.print_check(success_message)
        except Exception as e:
            log.error(f"Process failed: {failure_message}. Error: {str(e)}")
            self.print_fail(f"{failure_message}: {str(e)}")
            self.bell()
            raise e

    def print_application_diff(self, diff_output: str) -> None:
        """Prints an ArgoCD application diff with colored output.

        Takes the output of 'argocd app diff <app-name>' and formats it with colors
        and styling to make it more readable.

        Args:
            diff_output: String containing the output of argocd app diff command

        Example:
            ```python
            console = Console()
            diff_output = subprocess.check_output(
                ["argocd", "app", "diff", "my-app"]
            ).decode("utf-8")
            console.print_application_diff(diff_output)
            ```
        """
        log.debug("Parsing application diff output")

        # Split the diff by resource sections
        sections = re.split(r"===== (.+?) ======", diff_output)

        if len(sections) <= 1:
            log.debug("No resources found in diff output")
            self.print("[yellow]No differences found in the application[/yellow]")
            return

        # First element is empty if diff starts with a section header
        if not sections[0].strip():
            sections.pop(0)

        for i in range(0, len(sections), 2):
            if i + 1 >= len(sections):
                break

            resource_path = sections[i]
            diff_content = sections[i + 1]

            # Extract resource type and name from the path
            path_parts = resource_path.strip().split("/")
            if len(path_parts) >= 3:
                resource_type = path_parts[-3] if len(path_parts) >= 3 else "Unknown"
                namespace = path_parts[-2] if len(path_parts) >= 2 else "default"
                name = path_parts[-1] if len(path_parts) >= 1 else "Unknown"
            else:
                resource_type = "Unknown"
                namespace = "default"
                name = resource_path

            # Print resource header
            self.print(
                f"\n[bold magenta]{'=' * 5}[/bold magenta] "
                f"[bold white]{resource_type} {namespace} {name} [/bold white] "
                f"[bold magenta]{'=' * 5}[/bold magenta]"
            )

            # Process diff content
            for line in diff_content.splitlines():
                if line.startswith("<"):
                    # Lines that are removed (exist in the cluster but not in git)
                    self.print(f"[red]{line}[/red]")
                elif line.startswith(">"):
                    self.print(f"[green]{line}[/green]")
                else:
                    # Context lines
                    self.print(f"{line}")

        log.debug("Application diff printed successfully")

    def ask_yes_no(
        self, question: str, default: bool = True, bell: bool = True
    ) -> bool:
        """Ask user a yes/no question using questionary.

        Args:
            question: The question to ask.
            default: The default answer (True for Yes, False for No). Defaults to True.
            bell: Ring the terminal bell. Defaults to True

        Returns:
            bool: True if user answered Yes, False if No.
        """
        log.debug(f"Asking yes/no question: {question}, default: {default}")

        if bell:
            self.bell()
        result = questionary.confirm(question, default=default).ask()

        log.debug(f"User answered: {result}")
        return result

    def display_repo_state(self, state: Dict[str, Any]) -> None:
        """Display repository state with rich formatting.

        Args:
            state: Repository state dictionary from Git.check_clean_state()
        """
        log.debug("Displaying repository state")

        if state["is_clean"]:
            self.print_check(
                "[bold green]Repository is clean.[/bold green] "
                "Working tree has no changes.",
            )
            return

        self.print(Panel("[bold red]Changes in repository[/bold red]", expand=False))

        # Show staged changes
        if state["staged_changes"]:
            self.print("\n[bold green]Changes staged for commit:[/bold green]")
            for change in state["staged_changes"]:
                change_color = self._get_change_color(change["type"])
                self.print(
                    f"  [{change_color}]{change['type']}:[/{change_color}]"
                    f" {change['path']}"
                )

        # Show unstaged changes
        if state["unstaged_changes"]:
            self.print("\n[bold yellow]Changes not staged for commit:[/bold yellow]")
            for change in state["unstaged_changes"]:
                change_color = self._get_change_color(change["type"])
                self.print(
                    f"  [{change_color}]{change['type']}:[/{change_color}]"
                    f" {change['path']}"
                )

        # Show untracked files
        if state["untracked_files"]:
            self.print("\n[bold red]Untracked files:[/bold red]")
            for file_path in state["untracked_files"]:
                self.print(f"  [red]•[/red] {file_path}")

    def step(self, message: str, bell: bool = False) -> None:
        """Show the user a message and then expect it to press enter.

        Args:
            message: The message to show.
            bell: Ring the terminal bell. Defaults to False
        """
        if bell:
            self.bell()

        questionary.text(f"{message} then press Enter.").ask()

    def create_commit_message(
        self,
        change_type: Optional[str] = None,
        scope: Optional[str] = None,
        title: Optional[str] = None,
        body: Optional[str] = None,
    ) -> str:
        """Create a commit message using interactive prompts and editor.

        Creates a conventional commit message with type, scope, title and body.
        If arguments are not provided, prompts the user for input.

        Args:
            change_type: Optional type of change (feat, fix, improve, refactor)
            scope: Optional scope of the change
            title: Optional title/summary of the change
            body: Optional detailed description of the change

        Returns:
            str: Formatted commit message
        """
        log.debug("Creating commit message")

        # Get change type if not provided
        log.debug("Prompting for change type")
        self.bell()
        change_type = questionary.select(
            "Select the type of change:",
            choices=["feat", "fix", "improve", "refactor"],
            default=change_type,
        ).ask()

        # Get scope if not provided
        log.debug("Prompting for scope")
        scope = scope or ""
        scope = questionary.text("Enter the scope of change:", default=scope).ask()

        # Get title if not provided
        log.debug("Prompting for title")
        title = title or ""
        title = questionary.text("Enter a title for the change:", default=title).ask()
        while title == "":
            title = questionary.text(
                "Enter a title for the change:", default=title
            ).ask()

        # Get body if not provided
        log.debug("Opening editor for body")
        body = self._get_body_from_editor()

        # Format the commit message
        scope_part = f"({scope})" if scope else ""
        header = f"{change_type}{scope_part}: {title}"

        if body:
            commit_message = f"{header}\n\n{body}"
        else:
            commit_message = header

        log.debug(f"Created commit message: {commit_message}")
        return commit_message

    def _get_body_from_editor(self) -> str:
        """Launch system editor to get commit message body.

        Returns:
            str: Text entered in the editor
        """
        log.debug("Launching editor for commit body")
        editor = os.environ.get("EDITOR", "vim")

        with tempfile.NamedTemporaryFile(
            suffix=".tmp", mode="w+", encoding="utf-8"
        ) as temp:
            temp.write(
                "# Enter commit message body. Lines starting with '#' "
                "will be ignored.\n"
            )
            temp.write("# Leave file empty to skip the body.\n")
            temp.flush()

            subprocess.call([editor, temp.name])

            temp.seek(0)
            lines = temp.readlines()

        # Filter out comment lines
        body_lines = [line for line in lines if not line.startswith("#")]
        body = "".join(body_lines).strip()

        log.debug(f"Got body from editor ({len(body)} chars)")
        return body

    def _get_change_color(self, change_type: str) -> str:
        """Helper method to determine the color for a change type.

        Args:
            change_type: The type of change as a string.

        Returns:
            str: Rich compatible color name for the change type.
        """
        log.debug(f"Determining color for change type: {change_type}")
        color_map = {
            "new file": "bright_green",
            "deleted": "bright_red",
            "renamed": "bright_blue",
            "modified": "bright_yellow",
        }
        return color_map.get(change_type, "white")
