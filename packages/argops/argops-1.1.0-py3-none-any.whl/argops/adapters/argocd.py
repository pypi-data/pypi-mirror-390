"""Define the ArgoCD adapter."""

import json
import logging
import os
import shutil
import time
from contextlib import suppress
from typing import Any, Dict, Optional, Union

from argops.adapters.console import Command
from argops.exceptions import (
    ArgoCDConfigurationError,
    ArgoCDDiffError,
    ArgoCDRefreshError,
    ArgoCDSyncError,
)

log = logging.getLogger(__name__)


class ArgoCD(Command):
    """A Python adapter for interacting with the ArgoCD command line interface.

    This adapter provides methods to check ArgoCD configuration, refresh applications,
    show application diffs, and sync applications.
    """

    # W0221: Number of parameters was 3 in 'Command.check' and is now 2
    # in overriding 'Gitea.check' but this is expected
    def check(self) -> None:  # noqa: W0221
        """Check if ArgoCD is well configured.

        This method verifies:
        1. ArgoCD CLI exists

        Raises:
            ArgoCDConfigurationError if it's not well configured
        """
        log.debug("Checking ArgoCD configuration")
        argocd_path = shutil.which("argocd")
        if argocd_path:
            log.debug(f"ArgoCD CLI found at: {argocd_path}")
        else:
            raise ArgoCDConfigurationError("ArgoCD CLI not found in PATH")

    @property
    def context(self) -> str:
        """Return the name of the active Kubernetes context."""
        return_code, stdout, stderr = self._run_command(
            ["kubectl", "config", "current-context"]
        )
        if return_code == 0:
            log.debug(f"Current kubernetes context: {stdout.strip()}")
            return stdout.strip()
        raise ArgoCDConfigurationError(f"Failed to get the current context: {stderr}")

    @property
    def namespace(self) -> Optional[str]:
        """Return the name of the active Kubernetes namespace."""
        cmd = [
            "kubectl",
            "config",
            "view",
            "--minify",
            "-o",
            "jsonpath='{.contexts[*].context.namespace}'",
        ]
        return_code, stdout, stderr = self._run_command(cmd)

        if return_code == 0:
            namespace = stdout.replace("'", "").strip()
            log.debug(f"Current kubernetes namespace: {namespace}")
            return namespace
        raise ArgoCDConfigurationError(f"Failed to get the current namespace: {stderr}")

    def set_context(self, context: str, namespace: Optional[str] = None) -> None:
        """Set the Kubernetes context.

        We're assuming you're using argocd login --core and that you do the
        context switch at kubectl level. Also that the context name is equal
        to the environment name plus an optional prefix stored in the
        environment variable ARGOPS_ENVIRONMENT_PREFIX.

        Args:
            context: the ArgoCD context
            namespace: the namespace to set in the context
        """
        with suppress(KeyError):
            prefix = os.environ["ARGOPS_ENVIRONMENT_PREFIX"]
            if prefix not in context:
                context = f"{prefix}-{context}"
        log.info(f"Setting the kubernetes context: {context}")
        cmd = ["kubectl", "config", "use-context", context]

        return_code, _, stderr = self._run_command(cmd)

        if return_code == 0:
            log.debug(f"Successfully set the kubernetes context: {context}")
        else:
            raise ArgoCDConfigurationError(
                f"Failed to set the context {context}: {stderr}"
            )

        self.set_namespace(namespace)

    def set_namespace(self, namespace: Optional[str] = None) -> None:
        """Set the Kubernetes namespace.

        If namespace is None or "" it will unset the namespace

        Args:
            namespace: a kubernetes namespace
        """
        if not namespace or namespace == "":
            log.info(f"Unsetting the kubernetes namespace {self.namespace}")
            namespace = '""'
        else:
            log.info(f"Setting the kubernetes namespace: {namespace}")

        cmd = [
            "kubectl",
            "config",
            "set-context",
            "--current",
            f"--namespace={namespace}",
        ]

        return_code, _, stderr = self._run_command(cmd)

        if return_code == 0:
            log.debug("Successfully changed the kubernetes namespace")
        else:
            raise ArgoCDConfigurationError(
                f"Failed to change the namespace to {namespace}: {stderr}"
            )

    def refresh_application(self, app_name: str) -> Dict[str, Any]:
        """Refresh an application.

        Args:
            app_name: The name of the application to refresh.

        Returns:
            the result of the refresh

            status: synced or not
        """
        return self.get_application_state(app_name, refresh=True)

    def get_application_state(
        self, app_name: str, refresh: bool = False
    ) -> Dict[str, Any]:
        """Get the state of an application.

        Args:
            app_name: The name of the application to refresh.
            refresh: whether to refresh the application

        Returns:
            sync_status:
        """
        cmd = ["argocd", "app", "get", app_name, "--output", "json"]
        if refresh:
            cmd.append("--refresh")
            log.debug(f"Refreshing application: {app_name}")
        else:
            log.debug(f"Getting the state of the application: {app_name}")

        return_code, stdout, stderr = self._run_command(cmd, retries=3)

        if return_code == 0:
            try:
                if refresh:
                    log.debug(
                        f"Successfully refreshed the application state: {app_name}"
                    )
                else:
                    log.debug(f"Successfully got application state: {app_name}")
                data = json.loads(stdout)
                state = {
                    "commit": data["status"]["sync"]["revision"],
                    "health": data["status"]["health"]["status"],
                    "sync": data["status"]["sync"]["status"],
                }
                return state
            except json.JSONDecodeError as e:
                log.error(f"Failed to parse JSON response: {e}")
                raise e
        if refresh:
            raise ArgoCDRefreshError(
                f"Failed to refresh application {app_name}: {stderr}"
            )
        raise ArgoCDRefreshError(
            f"Failed to get the application {app_name} state: {stderr}"
        )

    def wait_for_application_to_be_healthy(
        self, app_name: str, wait_time: int = 1
    ) -> None:
        """Wait for the application to be ready.

        Args:
            app_name: The name of the application to refresh.
            wait_time: how much to wait between checks
        """
        while True:
            state = self.get_application_state(app_name)
            if state["health"] == "Healthy" and state["sync"] == "Synced":
                return
            if state["health"] != "Progressing":
                raise ArgoCDSyncError(
                    f"Failed to sync application {app_name} "
                    f"it's in state {state['health']}"
                )
            time.sleep(wait_time)

    def get_application_diff(
        self,
        app_name: str,
        revision: Optional[str] = None,
        server_side: Optional[bool] = True,
    ) -> str:
        """Show the diff for an application.

        Args:
            app_name: The name of the application.
            revision: The commit id to check

        Returns:
            the message of the diff
        """
        log.debug(f"Showing diff for application: {app_name}")
        cmd = ["argocd", "app", "diff", app_name]
        if revision:
            cmd += ["--revision", revision]
        if server_side:
            cmd += ["--server-side-generate"]

        return_code, stdout, stderr = self._run_command(cmd)

        if return_code == 0:
            log.debug(f"No differences found for application: {app_name}")
        elif return_code == 1:
            log.debug(f"Found differences for application: {app_name}")
        else:
            raise ArgoCDDiffError(
                f"Error getting diff for application {app_name}: {stderr}"
            )
        return stdout

    def sync_application(
        self,
        app_name: str,
        prune: bool = False,
        server_side: Optional[bool] = True,
    ) -> Dict[str, Union[bool, str]]:
        """Sync an application.

        Args:
            app_name: The name of the application to sync.
            prune: Whether to prune resources. Defaults to False.
            dry_run: Whether to perform a dry run. Defaults to False.

        Returns:
            A dictionary with the sync results.
        """
        log.debug(f"Syncing application: {app_name} (prune={prune})")
        cmd = ["argocd", "app", "sync", app_name]

        if prune:
            cmd.append("--prune")

        if server_side:
            cmd += ["--server-side"]
        return_code, stdout, stderr = self._run_command(cmd)

        if return_code != 0:
            raise ArgoCDSyncError(f"Failed to sync application {app_name}: {stderr}")

        self.wait_for_application_to_be_healthy(app_name)

        log.debug(f"Successfully synced application: {app_name}")
        return {"success": True, "output": stdout}
