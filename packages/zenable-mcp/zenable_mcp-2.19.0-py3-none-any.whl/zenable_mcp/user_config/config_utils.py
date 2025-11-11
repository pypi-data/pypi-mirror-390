import logging
from typing import Optional

from zenable_mcp.user_config.data_models import DEFAULT_CONFIG, UserConfig

LOG = logging.getLogger(__name__)


def reconcile_deprecated_file_config(
    db_config: UserConfig,
    file_config: UserConfig,
    tenant_name: str,
    db_error: Optional[str],
    file_error: Optional[str],
) -> tuple[UserConfig, Optional[str], Optional[str]]:
    """
    Reconcile deprecated file config with DB config.

    This will be deprecated, and this will be removed in a future release.

    Returns:
        Tuple of (config, error_message, warning_message)
    """
    # There are more sophisticated ways to detect if a config was loaded, but this is simple and
    # works.
    has_db_config = db_config != DEFAULT_CONFIG
    has_file_config = file_config != DEFAULT_CONFIG

    warning_message = None
    error_message = None

    if has_file_config and not has_db_config:
        # DB config doesn't exist, but file config does: use file config
        user_config = file_config
        warning_message = (
            "Deprecation warning: Configuration will no longer be loaded from file. "
            "The file configuration is being loaded because no config was set in the UI. "
            "Please manage settings via the Zenable UI and remove 'zenable_config.{toml,yaml,yml}' "
            "from your repository."
        )
        # Let's log a warning so we can check who's still using files and make a migration ourselves and contact the tenant to let them know.
        LOG.warning(
            "File config loaded for tenant %s and the UI config is default. Using file config. The config in the file is %s",
            tenant_name,
            file_config,
        )
        error_message = file_error
    elif has_file_config and has_db_config:
        # Both exist: use DB config and warn about file
        user_config = db_config
        warning_message = (
            "Deprecation warning: Configuration will no longer be loaded from file. "
            "The file configuration is being ignored because a config was set in the UI. "
            "Please remove 'zenable_config.{toml,yaml,yml}' from your repository "
            "and keep managing settings via the Zenable UI."
        )
        # Let's log a warning so we can check who's still using files and make a migration ourselves and contact the tenant to let them know.
        LOG.warning(
            "File config found for tenant %s, but UI config was also found. Using DB config. The config in the file is %s",
            tenant_name,
            file_config,
        )
        # This error concatenation is not the best, but this method will be deleted.
        if db_error:
            error_message = "UI config error: " + db_error
        if file_error:
            if error_message:
                error_message += ". File config error: " + file_error
            else:
                error_message = "File config error: " + file_error
    else:
        # Only DB config or no custom config: use db_config
        user_config = db_config

    return user_config, error_message, warning_message
