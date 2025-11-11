import logging
from abc import ABC, abstractmethod
from typing import Optional

from pydantic import ValidationError
from tomllib import TOMLDecodeError
from yaml import YAMLError

from zenable_mcp.logging.logged_echo import echo
from zenable_mcp.logging.persona import Persona
from zenable_mcp.user_config.config_parser import (
    ConfigParser,
    UserDBConfigParser,
)
from zenable_mcp.user_config.data_models import DEFAULT_CONFIG, UserConfig
from zenable_mcp.user_config.file_provider import (
    File,
    FileProvider,
    ProviderFileNotFoundError,
    ProviderMultipleFilesFoundError,
)

LOG = logging.getLogger(__name__)


class ConfigHandler(ABC):
    """
    Abstract class for config handlers.
    """

    @abstractmethod
    def load_config(self) -> tuple[UserConfig, Optional[str]]:
        """
        Load the user config.

        Returns:
            Tuple of (config, error_message)
        """


class FileConfigHandler(ConfigHandler):
    """
    Config handler for file based user config.
    """

    _config_logged = False  # Class variable to track if we've already logged

    def __init__(
        self,
        file_provider: FileProvider,
        config_parsers: list[ConfigParser],
        config_file_name: str = "zenable_config",
    ):
        self.file_provider = file_provider
        self.config_parsers = config_parsers
        self.config_file_name = config_file_name

    def load_config(self) -> tuple[UserConfig, Optional[str]]:
        """
        Load the user config.

        Returns:
            Tuple of (config, error_message)
            - config: The loaded config or default config if loading failed
            - error_message: Error message if config loading failed, None otherwise
        """
        # Let's try to load the config file. If we can't find it, we return a default config.
        error_message = None
        try:
            file = self._read_file()
            loaded_config, extra_fields_warning = self._parse_config(file)

            if extra_fields_warning:
                error_message = extra_fields_warning
                echo(
                    f"User config loaded, found extra fields. Generated the error message: {error_message}. Loaded config: {loaded_config}",
                    persona=Persona.POWER_USER,
                )
            else:
                error_message = None
                # Only log at info level the first time, debug thereafter
                if not FileConfigHandler._config_logged:
                    echo(
                        f"User config loaded successfully. Config: {loaded_config}",
                        persona=Persona.POWER_USER,
                    )
                    FileConfigHandler._config_logged = True
                else:
                    echo(
                        f"User config loaded successfully. Config: {loaded_config}",
                        persona=Persona.DEVELOPER,
                    )

        except ProviderFileNotFoundError:
            # If the file is not found, we return a default config, no error message
            error_message = None  # No error message, this is not an error.
            echo(
                "User config not found, using the Zenable defaults...",
                persona=Persona.DEVELOPER,
            )
            loaded_config = DEFAULT_CONFIG

        except ProviderMultipleFilesFoundError as error:
            # If multiple files are found, we return a default config, setting a specific error message
            found_files = error.found_files
            error_message = f"Multiple config files found, using the Zenable defaults. Files found: {found_files}"
            echo(error_message, persona=Persona.POWER_USER, err=True)
            loaded_config = DEFAULT_CONFIG

        except (ValidationError, TOMLDecodeError, YAMLError):
            # If the file is not valid, we return a default config, setting a specific error message
            error_message = "We couldn't parse the provided config file, using the Zenable defaults..."
            echo(error_message, persona=Persona.POWER_USER, err=True)
            loaded_config = DEFAULT_CONFIG

        except Exception:
            # Other errors (internal errors, etc)
            error_message = (
                "Failed to load the provided config, using the Zenable defaults..."
            )
            echo(error_message, persona=Persona.DEVELOPER, err=True)
            loaded_config = DEFAULT_CONFIG

        return loaded_config, error_message

    def _read_file(self) -> File:
        """
        Fetch the file content.
        """
        # We have the file name without extension and a list of parsers with compatible extensions.
        # Create a list with all the possible file names to fetch.
        file_names = [
            self.config_file_name + ext
            for parser in self.config_parsers
            for ext in parser.compatible_file_extensions
        ]
        return self.file_provider.find_and_get_one_file(file_names)

    def _parse_config(self, file: File) -> tuple[UserConfig, Optional[str]]:
        """
        Parse the config file and return a UserConfig instance with optional warning.
        """
        # We have a file loaded, we need to find the parser that can parse it.
        file_extension = "." + file.path.split(".")[-1]
        compatible_parser = next(
            (
                parser
                for parser in self.config_parsers
                if file_extension in parser.compatible_file_extensions
            ),
            None,
        )
        if not compatible_parser:
            # This should never happen, as we should have found the file with a compatible extension.
            raise ValueError("No compatible parser found for the file.")
        return compatible_parser.parse_config(file.content)


class DBConfigHandler(ConfigHandler):
    """
    Config handler for database-stored user config (stores only deltas from DEFAULT_CONFIG).
    """

    def __init__(self, tenant_config_delta: Optional[dict]):
        """
        Initialize with tenant config delta from database.

        Args:
            tenant_config_delta: Dictionary containing only overrides from DEFAULT_CONFIG.
                               None means no overrides (use defaults).
        """
        self.tenant_config_delta = tenant_config_delta

    def load_config(self) -> tuple[UserConfig, Optional[str]]:
        """
        Load config by merging tenant delta with DEFAULT_CONFIG.

        Returns:
            Tuple of (config, error_message)
            - config: The merged config or default config if loading failed
            - error_message: Error message if config loading/validation failed, None otherwise
        """
        # If no delta, return default config
        if not self.tenant_config_delta:
            LOG.debug(
                "No tenant config delta in DB, using the Zenable defaults...",
            )
            return DEFAULT_CONFIG, None

        try:
            # Use the DB config parser to validate and merge delta with defaults
            # It's not a parser, but we keep the same interface for consistency
            parser = UserDBConfigParser()

            # Get the merged config from the DB config delta
            merged_config, warning = parser.get_config_from_dict(
                self.tenant_config_delta
            )

            if warning:
                LOG.exception(
                    f"Tenant DB config loaded, found extra fields. {warning}. This shouldn't "
                    "happen, it probably means that there's a data inconsistency in the DB."
                )
            else:
                LOG.info(
                    "Tenant DB config loaded successfully.",
                )

            return merged_config, warning
        except Exception:
            error_message = (
                "Internal error: Failed to load tenant configuration. Using defaults."
            )
            LOG.exception(error_message)
            return DEFAULT_CONFIG, error_message
