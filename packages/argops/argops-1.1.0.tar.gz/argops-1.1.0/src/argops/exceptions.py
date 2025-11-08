"""Define program exceptions."""

# ArgoCD


class ArgoCDConfigurationError(Exception):
    """Custom exception for ArgoCD configuration errors."""


class ArgoCDRefreshError(Exception):
    """Custom exception for ArgoCD refresh errors."""


class ArgoCDDiffError(Exception):
    """Custom exception for ArgoCD diff errors."""


class ArgoCDSyncError(Exception):
    """Custom exception for ArgoCD sync errors."""


# Gitea


class TeaConfigurationError(Exception):
    """Custom exception for gitea tea configuration errors."""


class TeaRuntimeError(Exception):
    """Custom exception for gitea tea runtime errors."""
