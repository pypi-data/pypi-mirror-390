"""Define all the orchestration functionality required by the program to work.

Classes and functions that connect the different domain model objects with the adapters
and handlers to achieve the program's purpose.
"""  # noqa: C0302

# C0302 Too many lines in module (1127/1000)
# The function apply is complex, I know, it needs some refactoring,
# will do on a great day

import difflib
import filecmp
import logging
import os
import re
import shutil
import subprocess
import sys
from collections import OrderedDict
from io import StringIO
from pathlib import Path
from typing import TYPE_CHECKING, Any, Dict, List, Optional, Tuple, TypeVar, Union, cast

from ruyaml import YAML
from ruyaml.comments import CommentedMap

from argops.adapters.git import NoRemoteTrackingBranchError
from argops.model import YamlDiff

if TYPE_CHECKING:
    from argops.adapters.argocd import ArgoCD
    from argops.adapters.console import Console
    from argops.adapters.git import Git
    from argops.adapters.gitea import Gitea


log = logging.getLogger(__name__)


GREEN = "\033[32m"
RED = "\033[31m"
YELLOW = "\033[33m"
RESET = "\033[0m"


def promote_changes(
    repo: "Git",
    src_dir: Optional[Path] = None,
    dest_dir: Optional[Path] = None,
    filters: Optional[List[str]] = None,
    dry_run: bool = False,
) -> List[Path]:
    """Promote changes from the source directory to the destination directory.

    Args:
        src_dir (str): The name of the source directory.
        dest_dir (str): The name of the destination directory.
        filters (List[str]): List of filters the applications must match.
        repo (Git): The git repository adapter.
        dry_run (bool): If True, perform a dry run showing changes without
            copying files.

    Returns:
        the paths where the promotion is going to be made
    """
    src_dir = src_dir or Path("staging")
    dest_dir = dest_dir or Path("production")
    promote_dirs: List[Path] = []
    filters = filters or []

    repository_root, initial_path = find_repository_root_path(src_dir=src_dir)
    os.chdir(repository_root)
    if initial_path == Path("."):
        initial_path = src_dir

    # Ensure the destination directory exists
    if not dest_dir.exists():
        dest_dir.mkdir(parents=True, exist_ok=True)
        log.info(f"Created destination directory: {dest_dir}")

    application_directories = find_application_directories(filters, initial_path)

    # Sync each directory
    for directory in application_directories:
        log.info(f"Promoting application {directory}")
        print_application_name(directory)
        sync_src = directory.resolve().relative_to(repository_root)
        sync_dest = dest_dir / directory.relative_to(src_dir)

        if not sync_dest.exists():
            sync_dest.mkdir(parents=True, exist_ok=True)
            log.info(f"Created destination directory: {sync_dest}")

        comparison = filecmp.dircmp(sync_src, sync_dest)
        sync_directory(
            comparison,
            sync_src,
            sync_dest,
            repo,
            dry_run,
        )
        promote_dirs.append(sync_dest)
    return promote_dirs


def find_application_directories(
    filters: Optional[List[str]] = None, start_dir: Optional[Path] = None
) -> List[Path]:
    """Find directories containing a Chart.yaml file that match the filters.

    The filters can be either environments, application sets or applications.

    Args:
        filters (List[str]): List of filters that the directories need to match.
        start_dir (Path): The path of the directory to start form.

    Returns:
        List[Path]: List of application directory absolute paths to sync.

    Raises:
        ValueError: If no applications are found
    """
    filters = filters or []
    start_dir = start_dir or Path("staging")
    directories = []

    # If cwd is an application directory
    if (start_dir / "Chart.yaml").exists() and (
        len(filters) == 0
        or any(directory in filters for directory in str(start_dir).split("/"))
    ):
        return [start_dir]

    # If cwd is the root, an environment or an application set directory
    for element in start_dir.rglob("**/*"):
        if (
            element.is_dir()
            and (element / "Chart.yaml").exists()
            and (
                len(filters) == 0
                or any(directory in filters for directory in str(element).split("/"))
            )
        ):
            directories.append(element)

    if len(directories) == 0:
        if len(filters) == 0:
            filters = ["None"]
        raise ValueError(
            f"No application was found with the selected filters: {','.join(filters)}"
        )

    return directories


def find_repository_root_path(src_dir: Optional[Path] = None) -> Tuple[Path, Path]:
    """Finds the path at the top of the argocd repository.

    Walk upwards the directory tree starting from the current working directory until
    it finds the src_dir directory to promote.

    Args:
        src_dir (str): The name of the source directory to promote.

    Returns:
        str: The full path of the found repository root directory.
        str: The relative path of the found repository root directory.

    Raises:
        FileNotFoundError: If the repository with the given name is not found.
    """
    if not src_dir:
        src_dir = Path(".")
    initial_path = Path.cwd()
    current_path = initial_path

    while current_path != current_path.parent:  # Stop at the filesystem root
        target_path = current_path / src_dir
        if target_path.is_dir():
            log.debug(f"Found '{src_dir}' at {target_path.resolve()}")
            return current_path.resolve(), initial_path.relative_to(current_path)

        current_path = current_path.parent

    raise FileNotFoundError(
        f"No repository named '{src_dir}' found in the directory tree."
    )


def sync_new_file(
    file_name: str, src_dir: Path, dest_dir: Path, repo: "Git", dry_run: bool
) -> None:
    """Handle new files and directories.

    By copying them from the source to the destination directory.

    Args:
        file_name (str): The name of the file or directory.
        src_dir (Path): The path to the source directory.
        dest_dir (Path): The path to the destination directory.
        repo (Git): The git repository adapter.
        dry_run (bool): If True, only log the changes without performing any
                        operations.
    """
    src_path = src_dir / file_name
    dest_path = dest_dir / file_name.replace("-staging", "-production")

    if file_name in ("values-staging.yaml", "secrets.yaml"):
        promote_environment_specific_files(file_name, src_dir, dest_dir, repo, dry_run)
    else:
        log.info(f"{GREEN}New{RESET}: {src_path} -> {dest_path}")
        if not dry_run:
            if src_path.is_dir():
                shutil.copytree(src_path, dest_path)
            else:
                shutil.copy2(src_path, dest_path)


def sync_deleted_file(file_name: str, dest_dir: Path, dry_run: bool) -> None:
    """Handle files and directories that have been deleted from the source.

    By removing them from the destination directory.

    Args:
        file_name (str): The name of the file or directory.
        dest_dir (str): The path to the destination directory.
        dry_run (bool): If True, only log the changes without performing any
                        operations.
    """
    dest_path = dest_dir / file_name

    if file_name in ["values-production.yaml"]:
        return

    log.info(f"{RED}Deleting{RESET}: {dest_path}")
    if not dry_run:
        if dest_path.is_dir():
            shutil.rmtree(dest_path)
        else:
            os.remove(dest_path)


def sync_updated_file(
    file_name: str, src_dir: Path, dest_dir: Path, repo: "Git", dry_run: bool
) -> None:
    """Handle updated files.

    By copying them from the source to the destination directory
    and logging differences.

    Args:
        file_name (str): The name of the file.
        src_dir (str): The path to the source directory.
        dest_dir (str): The path to the destination directory.
        repo (Git): The git repository adapter.
        dry_run (bool): If True, only log the changes without performing any
                        operations.
    """
    src_path = src_dir / file_name
    dest_path = dest_dir / file_name

    log.info(f"{YELLOW}Updating file{RESET}: {src_path} -> {dest_path}\n")

    if file_name in ("values-staging.yaml", "secrets.yaml"):
        promote_environment_specific_files(file_name, src_dir, dest_dir, repo, dry_run)
    else:
        show_file_diff(src_path, dest_path)
        if not dry_run:
            shutil.copy2(src_path, dest_path)


# ignore: Missing type parameters for generic type dircmp
# The standard filecmp.dircmp class from Python's standard library
# does not require or support type parameters.
def sync_directory(
    comparison: filecmp.dircmp,  # type: ignore
    src_dir: Path,
    dest_dir: Path,
    repo: "Git",
    dry_run: bool,
) -> None:
    """Synchronize the changes between two directories.

    It performs the following operations:
    - Copy new and updated files from the source directory to the destination
      directory.
    - Delete files and directories that are not in the source directory.

    Args:
        comparison (filecmp.dircmp): The directory comparison object.
        src_dir (Path): The path to the source directory.
        dest_dir (Path): The path to the destination directory.
        repo (Git): The git repository adapter.
        dry_run (bool): If True, only log the changes without performing any
                        operations.
    """
    for file_name in comparison.left_only:
        sync_new_file(file_name, src_dir, dest_dir, repo, dry_run)

    for file_name in comparison.right_only:
        sync_deleted_file(file_name, dest_dir, dry_run)

    for file_name in comparison.diff_files:
        sync_updated_file(file_name, src_dir, dest_dir, repo, dry_run)

    for subdir_name in comparison.common_dirs:
        subdir_comparison = comparison.subdirs[subdir_name]
        sync_directory(
            subdir_comparison,
            src_dir / subdir_name,
            dest_dir / subdir_name,
            repo,
            dry_run,
        )


def promote_environment_specific_files(
    file_name: str,
    src_dir: Path,
    dest_dir: Path,
    repo: "Git",
    dry_run: bool = False,
) -> None:
    """Promote changes of environment specific files (values and secrets).

    This function compares the YAML contents of the source and destination files.
    If `dry_run` is True, it only shows the diff without making any changes.

    It also substitutes the environment in the content of the files. For
    example if it contains a key `domain: staging.example.com` it will be promoted
    in production as `domain: production.example.com`.

    Args:
        file_name (str): The name of the YAML file (e.g., "values-staging.yaml").
        src_dir (str): The source directory containing the staging file.
        dest_dir (str): The destination directory containing the production file.
        repo (Git): The git repository adapter.
        dry_run (bool, optional): If True, only show the diff without making any
            changes. Defaults to False.
    """
    src_environment = src_dir.parts[0]
    dest_environment = dest_dir.parts[0]
    staging_file_path = src_dir / file_name
    # Replace values-staging to values-production
    production_file_path = dest_dir / file_name.replace(
        src_environment, dest_environment
    )
    log.info(
        f"Promoting the changes from {staging_file_path} to {production_file_path}"
    )

    last_promoted_commit = get_last_promoted_commit_id(repo, production_file_path)
    current_commit = repo.current_commit_id
    log.debug(f"Last promoted commit of {staging_file_path} is {last_promoted_commit}")
    log.debug(f"Last commit is {current_commit}")

    # Get the different contents
    if not last_promoted_commit:
        last_promoted_content = ""
    else:
        last_promoted_content = get_content(
            repo, staging_file_path, last_promoted_commit
        )

    log.debug(
        f"Creating the updated values of {production_file_path} "
        f"from the latest version of {staging_file_path}"
    )
    old_production_content = get_content(repo, production_file_path)
    new_content = update_values(
        last_promoted_content,
        get_content(repo, staging_file_path),
        old_production_content,
        current_commit,
    )
    if not dry_run:
        set_content(production_file_path, new_content)
        log.debug(f"Promotion completed. Changes applied to {production_file_path}")


def update_values(
    last_promoted_source_content: str,
    source_content: str,
    destination_content: str,
    last_promoted_commit_id: str = "HEAD",
) -> str:
    """Updates the destination YAML content.

    By applying changes from the source content, including new, changed,
    and deleted properties. Updates the last promoted commit ID in the destination
    content.

    Args:
        last_promoted_source_content (str): The previous source YAML content.
        source_content (str): The current source YAML content.
        destination_content (str): The current destination YAML content.
        last_promoted_commit_id (str): The last promoted git commit id.

    Returns:
        str: The updated YAML content with comments.
    """
    log.debug("Comparing source contents.")
    diff = compare_yaml_contents(last_promoted_source_content, source_content)

    if not diff.has_changed:
        log.debug("The source has not changed since the last promoted commit")
        return destination_content

    # Read the current production file
    if destination_content == "":
        log.debug("Destination content is empty, initializing from the source content.")
        new_content = YAML().load(
            replace_in_nested_object(source_content, "staging", "production")
        )
        diff.new = diff.new + diff.unchanged + diff.changed
        diff.changed = []
        diff.deleted = []
    else:
        log.debug("Loading existing destination content.")
        new_content = YAML().load(destination_content)

    def apply_diff(
        new_content: CommentedMap, diff: YamlDiff, parent_key: Optional[str] = ""
    ) -> None:
        """Recursively applies differences to the content, handling nested structures.

        Args:
            new_content (Dict[str, Any]): The content to be updated.
            diff (Any): The difference object containing new, changed, and
                deleted items.
            parent_key (Optional[str]): The parent key path for nested structures.
                Defaults to "".
        """
        log.debug(f"Applying differences to parent key: {parent_key}")

        for key, value in diff.new:
            new_content[key] = replace_in_nested_object(value, "staging", "production")

            comment = "New key in source"
            new_content.yaml_add_eol_comment(
                key=key,
                comment=comment,
            )
            log.debug(
                f"Added new key '{key}' with value '{value}' at path '{parent_key}'"
            )

        for key, value in diff.changed:
            if isinstance(value, dict):
                log.debug(f"Recursively applying changes to nested key: {key}")
                string_stream = StringIO()
                YAML().dump(new_content[key], string_stream)
                source_yaml = string_stream.getvalue()
                string_stream.close()
                string_stream = StringIO()
                YAML().dump(value, string_stream)
                destination_yaml = string_stream.getvalue()
                string_stream.close()

                apply_diff(
                    new_content[key],
                    compare_yaml_contents(
                        source_yaml,
                        destination_yaml,
                    ),
                    key,
                )
            else:
                comment = f"Key changed in source to {value}"
                new_content.yaml_add_eol_comment(key=key, comment=comment)
                log.info(f"Updated key '{key}' to '{value}' at path '{parent_key}'")

        for key in diff.deleted:
            if key in new_content:
                comment = "Key deleted in source"
                new_content.yaml_add_eol_comment(key=key, comment=comment)
                log.info(f"Marked key '{key}' as deleted at path '{parent_key}'")

    apply_diff(new_content, diff)

    log.debug("Updating the last promoted commit ID.")
    new_content.yaml_set_start_comment(
        f"Last promoted commit id: {last_promoted_commit_id}"
    )

    log.debug("Finished updating values.")

    string_stream = StringIO()
    YAML().dump(new_content, string_stream)
    new_content_text = string_stream.getvalue()
    string_stream.close()

    show_diff(new_content_text, destination_content)

    return new_content_text


def get_last_promoted_commit_id(repo: "Git", file_path: Path) -> Optional[str]:
    """Extract the last promoted commit ID from a values-staging.yaml file.

    Args:
        repo (Git): The git repository adapter.
        file_path (Path): The path to the file to check.

    Returns:
        str: The last promoted commit ID or None if the line doesn't exist.
    """
    commit_id_pattern = re.compile(r"# Last promoted commit id: (\w+)")
    try:
        content = get_content(repo, file_path)
    except FileNotFoundError:
        log.warning(
            f"The file {file_path} doesn't exist, returning None as the content"
        )
        return None

    for line in content.splitlines():
        match = commit_id_pattern.match(line)
        if match:
            return match.group(1)

    return None


def get_content(repo: "Git", file_path: Path, commit_id: str = "HEAD") -> str:
    """Get YAML content of the file at a specific commit.

    If the file name matches ".*secrets.*", it will decrypt the content
    using `load_sops_file`.

    Args:
        repo (Git): The git repository adapter.
        file_path (str): The path to the file within the repository.
        commit_id (str): The commit ID to retrieve the file from. Defaults to "HEAD".

    Returns:
        str: The content of the file at the specified commit, or an empty string if
        the file doesn't exist.
    """
    try:
        commit_content = repo.get_content(file_path, commit_id)
    except FileNotFoundError:
        return ""

    except Exception as e:  # noqa: W0718
        # W0718: Catching too general exception Exception. But it's what we want
        log.error(
            f"Error retrieving content for '{file_path}' at commit '{commit_id}': {e}"
        )
        return ""

    if re.search(r".*secrets.*", file_path.name, re.IGNORECASE):
        log.debug(f"File '{file_path}' matches secrets pattern, decrypting with sops.")
        temp_file = Path(f"{repo.path}/argops-temporal-secret.yaml")
        temp_file.write_text(commit_content, encoding="utf8")
        try:
            content = load_sops_file(temp_file)
        except RuntimeError as e:
            log.warning(f"The '{file_path}' at commit '{commit_id}' doesn't exist: {e}")
            content = ""
        temp_file.unlink()  # Clean up the temporary file
    else:
        content = commit_content

    return content


def set_content(file_path: Path, content: str) -> None:
    """Set YAML content of the file.

    If the file name matches ".*secrets.*", it will encrypt the content
    using `save_sops_file`. Otherwise, it will write the content directly to the file.

    Args:
        file_path (Path): The path to the file on the filesystem.
        content (str): The new content to be written into the file.
    """
    file_exists = file_path.exists()
    if re.search(r".*secrets.*", file_path.name, re.IGNORECASE):
        if file_exists:
            old_content = load_sops_file(file_path)
        else:
            old_content = ""
        if content.strip() != old_content.strip():
            log.info(
                f"File '{file_path}' matches secrets pattern, encrypting with sops."
            )
            log.info(f"Writing content to '{file_path}'")
            save_sops_file(file_path, content)
        else:
            log.debug(f"Not overwriting {file_path} as the contents are equal")
    else:
        Path(file_path).write_text(content, encoding="utf-8")


def compare_yaml_contents(yaml_content_1: str, yaml_content_2: str) -> YamlDiff:
    """Compare the YAML contents from two plain text YAML strings.

    Args:
        yaml_content_1 (str): The plain text content of the first YAML.
        yaml_content_2 (str): The plain text content of the second YAML.

    Returns:
        YamlDiff: The differences between the two YAML contents.
    """
    content_1 = YAML().load(yaml_content_1)
    content_2 = YAML().load(yaml_content_2)

    # Initialize the YamlDiff object
    diff = YamlDiff()

    if not content_1:
        diff.new = [(key, content_2[key]) for key in content_2.keys()]
    elif not content_2:
        diff.deleted = content_1.keys()
    else:
        # Compare the contents
        all_keys = set(content_1.keys()).union(set(content_2.keys()))
        for key in all_keys:
            if key not in content_1:
                diff.new.append((key, content_2[key]))
            elif key not in content_2:
                diff.deleted.append(key)
            else:
                if content_1[key] != content_2[key]:
                    diff.changed.append((key, content_2[key]))
                else:
                    # E1101: Instance of FiledInfo has no append member, but it does
                    # https://github.com/pylint-dev/pylint/issues/4899
                    diff.unchanged.append((key, content_1[key]))  # noqa: E1101

    return diff


def show_diff(src: str, dest: str) -> None:
    """Show the differences between two strings.

    Args:
        src (str): The source text.
        dest (str): The destination text.
    """
    diff = difflib.unified_diff(dest.splitlines(), src.splitlines())
    for line in diff:
        printeable_line = line.rstrip("\n")
        if line.startswith("+++"):
            printeable_line = "+++ New"
        elif line.startswith("---"):
            printeable_line = "--- Old"
        if line.startswith("+"):
            log.info(f"{GREEN}{printeable_line}{RESET}")
        elif line.startswith("-"):
            log.info(f"{RED}{printeable_line}{RESET}")
        else:
            log.info(printeable_line)


def show_file_diff(src_file: Path, dest_file: Path) -> None:
    """Show the differences between two files.

    Args:
        src_file (Path): The path to the first file.
        dest_file (Path): The path to the second file.
    """
    show_diff(
        src_file.read_text(encoding="utf8"),
        dest_file.read_text(encoding="utf8"),
    )


def load_sops_file(file_path: Path) -> str:
    """Decrypt and load content from a sops-encrypted file.

    Args:
        file_path (Path): The path to the sops-encrypted file.

    Returns:
        str: The decrypted content of the file as a string.

    Raises:
        RuntimeError: If decryption fails due to a subprocess error.
    """
    try:
        log.debug(f"Decrypting file: {file_path}")
        result = subprocess.run(
            ["sops", "--decrypt", file_path],
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        log.debug(f"File {file_path} decrypted successfully")
        return result.stdout.decode("utf-8")
    except subprocess.CalledProcessError as e:
        error_message = e.stderr.decode().strip()
        log.error(f"Error decrypting the file: {error_message}")
        raise RuntimeError(
            f"Failed to decrypt file {file_path}: {error_message}"
        ) from e


def save_sops_file(file_path: Path, content: str) -> None:
    """Encrypt and save content to a file using sops.

    The function saves the content to a decrypted file with '{file_path}-decrypted',
    encrypts it with `sops`, and then renames it to the desired encrypted filename.

    Args:
        file_path (Path): The path where the encrypted file will be saved, including
            the '.yaml' extension.
        content (str): The content to be encrypted and saved.

    Example:
        content = 'secret_key: super_secret_value'
        save_sops_file('secrets.yaml', content)
    """
    log.debug(f"Encrypting and saving content to {file_path}")

    # Remove the '.yaml' extension from file_path for decrypted_file_path
    decrypted_file_path = file_path.parent / f"{file_path.stem}-decrypted.yaml"
    decrypted_file_path.write_text(content)
    log.debug(f"Decrypted content saved at {decrypted_file_path}")

    # Get the current working directory
    if decrypted_file_path.parent.is_absolute():
        cwd = decrypted_file_path.parent
    else:
        cwd = decrypted_file_path.cwd()

    try:
        # Encrypt the decrypted file using sops
        subprocess.run(
            ["sops", "--encrypt", "--in-place", str(decrypted_file_path)],
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            cwd=cwd,
        )
        log.debug("File successfully encrypted with sops")

        # Rename the decrypted file to have the '.yaml'
        # extension and match the desired filename
        decrypted_file_path.rename(file_path)
        log.debug(f"Encrypted file saved as {file_path}")
    except subprocess.CalledProcessError as e:
        log.error(f"Error encrypting the file: {e.stderr.decode().strip()}")
        raise
    except Exception as e:
        log.error(f"Unexpected error: {str(e)}")
        raise


def print_application_name(application_path: Path) -> None:
    """Print application name from given path.

    Args:
        application_path (Path): The application directory.

    Example:
        >>> print_application_name(Path("/path/to/app"))
        ###########
        ##  app  ##
        ###########
    """
    name = application_path.name
    box_size = len(name) + 8
    log.info(
        f"\n\n{'#' * box_size}\n" f"##  {name.title()}  ##\n" f"{'#' * box_size}\n"
    )


T = TypeVar(
    "T",
    str,
    Dict[str, Any],
    OrderedDict[str, Any],
    CommentedMap,
    List[Any],
    Tuple[Any],
    Any,
)


def replace_in_nested_object(
    obj: T,
    old_string: str,
    new_string: str,
) -> T:
    """Recursively replace strings in nested dictionary structures.

    Replaces all occurrences of old_string with new_string in nested
    dictionaries, lists, tuples, and other supported data structures.

    Args:
        obj: Input object to process for string replacements.
        old_string: The string to be replaced.
        new_string: The string to replace with.

    Returns:
        Modified object with string replacements applied.

    Raises:
        TypeError: If input cannot be processed.
    """
    try:
        # If it's a string, perform direct replacement
        if isinstance(obj, str):
            log.debug(f"Replacing in string: {obj}")
            replaced_str = obj.replace(old_string, new_string)
            if not isinstance(replaced_str, type(obj)):
                raise TypeError(
                    f"Unexpected type after replacement: {type(replaced_str)}"
                )
            return replaced_str

        # If it's an OrderedDict or dict
        if isinstance(obj, (OrderedDict, dict)):
            log.debug(f"Processing dictionary with {len(obj)} keys")
            # Use the same type as the input
            new_dict: Union[Dict[str, Any], OrderedDict[str, Any]] = type(obj)()

            for key, value in obj.items():
                # Recursively replace in nested structures
                new_dict[key] = replace_in_nested_object(value, old_string, new_string)

            return cast(T, new_dict)

        # If it's a list or tuple, recursively replace in each element
        if isinstance(obj, (list, tuple)):
            log.debug(f"Processing collection with {len(obj)} items")
            # ignore error: Cannot instantiate type "Type[tuple[Any]]"  [misc]
            # I don't have the time to deal with it right now
            return type(obj)(  # type: ignore
                replace_in_nested_object(item, old_string, new_string) for item in obj
            )

        # For any other type, return as is
        log.debug(f"Skipping non-replaceable type: {type(obj)}")
        return obj

    except Exception as e:
        log.error(f"Error replacing the values of: {e}")
        raise


def get_application_name_from_current_directory(environment: str) -> str:
    """Get application name from current directory.

    Also check if the environment is coherent with the current directory.
    """
    current_directory = Path.cwd()
    try:
        application_directories = find_application_directories(
            start_dir=current_directory
        )
    except ValueError as e:
        raise ValueError(
            "Could not find any ArgoCD application in your current directory"
        ) from e
    if application_directories != [current_directory]:
        raise ValueError(
            "Could not find any ArgoCD application in your current directory"
        )
    if environment not in str(current_directory):
        raise ValueError(
            f"Your current path is not part of the desired environment {environment}"
        )
    return current_directory.name


# R0912 Too many branches (30/12)
# R0914 Too many local variables (22/15)
# R0915 Too many statements (125/50)
# The function is complex, I know, it needs some refactoring, will do on a great day
def apply(  # noqa: R0912, R0914, R0915
    environment: str,
    argocd: "ArgoCD",
    repo: "Git",
    git_server: "Gitea",
    console: "Console",
) -> None:
    """Push, diff and sync the changes of an argocd application."""
    log.debug("Configure the apply")
    argocd.check()
    old_namespace = argocd.namespace
    old_context = argocd.context
    argocd.set_context(context=environment, namespace="argocd")
    if environment != "staging":
        git_server.check(repo.origin_url)
    application_name = get_application_name_from_current_directory(
        environment=environment
    )
    console.print(
        f"[white]Applying the changes of the application {application_name} "
        f"version {repo.current_commit_id} to {environment}[/white]",
        pad=False,
    )

    log.debug("Update the main branch")
    with console.print_process(
        "Updating the main branch with the remote",
        "Updated the main branch with the remote",
        "Error updating the main branch with the remote",
    ):
        repo.update_main()

    log.debug("Create the commit if needed")
    repo_state = repo.check_clean_state()
    if not repo_state["is_clean"]:
        log.debug("Create the branch if needed")
        if environment != "staging":
            branch_name = f"promote/{application_name}-{repo.branch_id}"
        else:
            branch_name = f"staging/{application_name}-{repo.branch_id}"

        if repo.current_branch != branch_name:
            repo.create_branch(branch_name)

        console.step('"git add" all the changes you want to deploy', bell=True)
        repo_state = repo.check_clean_state()
        if len(repo_state["staged_changes"]) > 0:
            commit_message = console.create_commit_message(
                scope=f"{environment}:{application_name}"
            )
            repo.commit(commit_message)

        log.debug("Check that the git state is clean")
        repo_state = repo.check_clean_state()
        console.display_repo_state(repo_state)
        if not repo_state["is_clean"]:
            continue_deploy = console.ask_yes_no(
                "Do you want to continue even if the state is not clean?",
                default=False,
            )
            if not continue_deploy:
                argocd.set_context(context=old_context, namespace=old_namespace)
                sys.exit(1)

    log.debug("Push the changes if necessary")
    with console.print_process(
        "Checking if the local changes have been pushed",
        "Checked if the local changes have been pushed",
        "Error checking if the local changes have been pushed",
    ):
        try:
            branch_is_ahead_origin = repo.branch_is_ahead_origin
        except NoRemoteTrackingBranchError:
            branch_is_ahead_origin = True

    if branch_is_ahead_origin:
        with console.print_process(
            "Pushing the local changes to the git repo",
            "Pushed the local changes to the git repo",
            "Error pushing the local changes to the git repo",
        ):
            repo.push()
    else:
        console.print_check(
            f"The current branch {repo.current_branch} is up to date with origin"
        )

    log.debug("Refreshing the argocd application")
    with console.print_process(
        f"Refreshing the application {application_name}",
        f"Refreshed the application {application_name}",
        f"Error refreshing the application {application_name}",
    ):
        app_state = argocd.refresh_application(application_name)
    if app_state["commit"] == repo.current_commit_id and app_state["sync"] == "Synced":
        console.print_check(
            f"The application {application_name} is already in sync with the latest "
            f"commit {repo.current_commit_id}"
        )
        console.bell()
        argocd.set_context(context=old_context, namespace=old_namespace)
        sys.exit(0)
    else:
        with console.print_process(
            (
                f"Fetching the application diff {application_name} for "
                f"commit {repo.current_commit_id}"
            ),
            (
                f"Fetched the application diff {application_name} for "
                f"commit {repo.current_commit_id}"
            ),
            (
                f"Error fetching the application diff {application_name} for "
                f"commit {repo.current_commit_id}"
            ),
        ):
            application_diff = argocd.get_application_diff(
                app_name=application_name, revision=repo.current_commit_id
            )
        if not application_diff:
            console.print(
                f"The changes introduced by {repo.current_commit_id} are not creating "
                f"any change in the application {application_name}"
            )
        else:
            console.print_application_diff(application_diff)

    log.debug("Create the merge request if needed")
    if branch_is_ahead_origin:
        push = console.ask_yes_no(
            "Do you want to push the changes to the git repository?"
        )
        if not push:
            console.print("Aborting the apply")
            argocd.set_context(context=old_context, namespace=old_namespace)
            sys.exit(0)
    if environment != "staging":
        with console.print_process(
            "Checking if there is an open merge request",
            "Checked if there is an open merge request",
            "Error checking if there is an open merge request",
        ):
            merge_request_url = git_server.get_merge_request_url(
                repo.origin_url, repo.current_branch
            )
        if merge_request_url:
            console.print_check(
                f"Merge request for branch {repo.current_branch} already exists: "
                f"{merge_request_url}"
            )
        else:
            with console.print_process(
                "Creating the merge request",
                "Created the merge request",
                "Error creating the merge request",
            ):
                description = [
                    repo.get_merge_commits(source_branch=repo.current_branch),
                    "\n",
                    "```diff",
                    application_diff,
                    "```",
                ]

                merge_request_url = git_server.create_merge_request(
                    origin_url=repo.origin_url,
                    branch_name=repo.current_branch,
                    title=f"Promote {application_name} changes to {environment}",
                    description="\n".join(description),
                )
            console.print(merge_request_url)
        merge = console.ask_yes_no("Do you want to merge the changes into main?")
        if merge:
            with console.print_process(
                f"Merging the request {merge_request_url}",
                f"Merged the request {merge_request_url}",
                f"Error merging the request {merge_request_url}",
            ):
                git_server.merge_merge_request(merge_request_url)
            with console.print_process(
                f"Refreshing the application {application_name} after the merge",
                f"Refreshed the application {application_name} after the merge",
                f"Error refreshing the application {application_name} after the merge",
            ):
                argocd.refresh_application(application_name)
        else:
            console.print("Aborting the merge and the sync")
            argocd.set_context(context=old_context, namespace=old_namespace)
            sys.exit(0)
    else:
        branch_name = repo.current_branch
        if branch_name != "main":
            with console.print_process(
                "Merging the changes into main locally",
                "Merged the changes into main locally",
                "Error merging the changes into main locally",
            ):
                repo.change_branch("main")
                repo.update_main()
                repo.merge_branch(branch_name)
                repo.delete_branch(branch_name)

        with console.print_process(
            "Pushing the local changes to the git repo",
            "Pushed the local changes to the git repo",
            "Error pushing the local changes to the git repo",
        ):
            repo.push()
    sync = console.ask_yes_no("Do you want to sync the changes?")
    if not sync:
        console.print("Aborting the sync")
        argocd.set_context(context=old_context, namespace=old_namespace)
        sys.exit(0)
    with console.print_process(
        f"Syncing the application {application_name} to {repo.current_commit_id}",
        f"Synced the application {application_name} to {repo.current_commit_id}",
        f"Error syncing the application {application_name} to {repo.current_commit_id}",
    ):
        argocd.sync_application(application_name)

    if environment == "staging":
        log.debug("Promoting the changes to the next environment")
        promote = console.ask_yes_no(
            "Do you want to promote the changes to production?",
            default=True,
        )
        if not promote:
            argocd.set_context(context=old_context, namespace=old_namespace)
            sys.exit(0)
        promote_dirs = promote_changes(repo=repo, filters=[application_name])
        if len(promote_dirs) > 1:
            raise ValueError(
                f"The promotion of the application {application_name} led to more than "
                "one directory, which is not yet supported by argops apply"
            )
        if len(promote_dirs) == 0:
            raise ValueError(
                f"The promotion of the application {application_name} returned no "
                "directory, please check the logs to debug the issue"
            )
        os.chdir(promote_dirs[0])
        console.print(f"Changed the current directory to {promote_dirs[0]}")
        apply(
            environment="production",
            argocd=argocd,
            repo=repo,
            console=console,
            git_server=git_server,
        )
    else:
        with console.print_process(
            "Updating local main branch with merged changes",
            "Updated local main branch with merged changes",
            "Error updating local main branch with merged changes",
        ):
            repo.change_branch("main")
            repo.update_main()
    console.bell()
