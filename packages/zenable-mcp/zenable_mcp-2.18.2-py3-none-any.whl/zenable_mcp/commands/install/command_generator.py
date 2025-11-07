"""Dynamic command generator for unified install commands."""

import click

from zenable_mcp.exit_codes import ExitCode
from zenable_mcp.ide_config import IDERegistry
from zenable_mcp.logging.command_logger import log_command
from zenable_mcp.logging.logged_echo import echo
from zenable_mcp.utils.cli_validators import (
    handle_exit_code,
    validate_mutual_exclusivity,
)
from zenable_mcp.utils.context_helpers import (
    get_dry_run_from_context,
    get_recursive_from_context,
)
from zenable_mcp.utils.install_status import (
    InstallResult,
    InstallStatus,
    show_installation_summary,
)


def _create_unified_command_function(
    tool_name: str, ide_class, mcp_group, hook_group, features: list[str]
):
    """Create a unified command function for a specific tool.

    This function generates a Click command that installs all supported
    features (mcp, hook, etc.) for the given tool.

    Args:
        tool_name: Canonical name of the tool
        ide_class: IDE configuration class for this tool
        mcp_group: MCP command group
        hook_group: Hook command group
        features: List of supported features for this tool

    Returns:
        Click command function
    """
    display_name = ide_class.display_name

    def unified_command(
        ctx,
        dry_run,
        recursive,
        is_global,
        include,
        exclude,
        overwrite=None,
        no_instructions=None,
    ):
        f"""Install all {display_name} integrations.

        This command installs all supported features for {display_name}:
        {", ".join(features)}.
        """
        # Invoke MCP installation if supported
        if "mcp" in features:
            # Find the command for this tool in the mcp group
            ide_command = mcp_group.commands.get(tool_name)
            if ide_command:
                try:
                    ctx.invoke(
                        ide_command,
                        overwrite=overwrite or False,
                        no_instructions=no_instructions or False,
                        dry_run=dry_run,
                        is_global=is_global,
                        recursive=recursive,
                        include=include,
                        exclude=exclude,
                    )
                except Exception as e:
                    echo(
                        f"Error installing MCP for {display_name}: {e}",
                        err=True,
                    )
                    return handle_exit_code(ctx, ExitCode.INSTALLATION_ERROR)

        # Invoke hook installation if supported
        if "hook" in features:
            # Find the command for this tool in the hook group
            hook_command = hook_group.commands.get(tool_name)
            if hook_command:
                try:
                    ctx.invoke(
                        hook_command,
                        is_global=is_global,
                        dry_run=dry_run,
                        recursive=recursive,
                        include=include,
                        exclude=exclude,
                    )
                except Exception as e:
                    echo(
                        f"Error installing hook for {display_name}: {e}",
                        err=True,
                    )
                    return handle_exit_code(ctx, ExitCode.INSTALLATION_ERROR)

        return ExitCode.SUCCESS

    # Set function metadata for Click
    unified_command.__name__ = tool_name.replace("-", "_")
    return unified_command


def add_unified_options(func):
    """Add standard options to unified install commands."""
    # MCP-specific options (only if tool supports MCP)
    func = click.option(
        "--no-instructions",
        is_flag=True,
        default=False,
        help="Skip post-installation instructions",
    )(func)
    func = click.option(
        "--overwrite",
        is_flag=True,
        default=False,
        help="Overwrite existing configuration",
    )(func)

    # Common options for all commands
    func = click.option(
        "--exclude",
        multiple=True,
        help="Exclude dirs matching glob patterns",
    )(func)
    func = click.option(
        "--include",
        multiple=True,
        help="Include only dirs matching glob patterns",
    )(func)
    func = click.option(
        "--global",
        "-g",
        "is_global",
        is_flag=True,
        default=False,
        help="Install globally",
    )(func)
    func = click.option(
        "--recursive",
        is_flag=True,
        default=False,
        help="Install in all git repos below current directory",
    )(func)
    func = click.option(
        "--dry-run",
        is_flag=True,
        default=False,
        help="Preview without installing",
    )(func)

    return func


def attach_mcp_commands(mcp_group, install_single_ide, common_options):
    """Attach MCP commands for all tools that support MCP.

    Args:
        mcp_group: Click Group (mcp subgroup) to attach commands to
        install_single_ide: Function to install IDE configuration
        common_options: Decorator for common MCP options
    """
    registry = IDERegistry()

    for tool_name, ide_class in registry.ide_configs.items():
        # Check if IDE supports MCP using class method
        try:
            capabilities = ide_class.get_capabilities()
            if not (
                capabilities.get("supports_mcp_global_config")
                or capabilities.get("supports_mcp_project_config")
            ):
                continue
        except Exception:
            # If we can't get capabilities, skip this IDE
            continue

        # Create command function for this tool
        def make_mcp_command(tool_name=tool_name, ide_class=ide_class):
            @common_options
            @click.pass_context
            @log_command
            def mcp_command(
                ctx,
                overwrite,
                no_instructions,
                dry_run,
                is_global,
                recursive,
                include,
                exclude,
            ):
                f"""Install MCP for {ide_class.display_name}."""
                return install_single_ide(
                    ctx,
                    tool_name,
                    overwrite,
                    no_instructions,
                    dry_run,
                    is_global,
                    recursive,
                    include,
                    exclude,
                )

            mcp_command.__name__ = tool_name.replace("-", "_")
            return mcp_command

        # Get aliases for this tool
        aliases = registry.get_aliases(tool_name)
        help_text = f"Install MCP for {ide_class.display_name}"

        # If aliases exist, show all aliases as visible and hide canonical
        if aliases:
            # Register all aliases as visible
            for alias in aliases:
                alias_cmd = make_mcp_command()
                mcp_group.add_command(
                    click.command(
                        name=alias,
                        help=help_text,
                        hidden=False,
                    )(alias_cmd)
                )

            # Register canonical name as hidden
            canonical_cmd = make_mcp_command()
            mcp_group.add_command(
                click.command(
                    name=tool_name,
                    help=help_text,
                    hidden=True,
                )(canonical_cmd)
            )
        else:
            # No aliases, register canonical name as visible
            cmd = make_mcp_command()
            mcp_group.add_command(
                click.command(
                    name=tool_name,
                    help=help_text,
                    hidden=False,
                )(cmd)
            )


def attach_hook_commands(hook_group, claude_impl, common_hook_options, all_hooks):
    """Attach hook commands for all tools that support hooks.

    Args:
        hook_group: Click Group (hook subgroup) to attach commands to
        claude_impl: Claude hook implementation function
        common_hook_options: Decorator for common hook options
        all_hooks: all_hooks command for recursive installation
    """
    registry = IDERegistry()

    for tool_name, ide_class in registry.ide_configs.items():
        # Check if IDE supports hooks using class method
        try:
            capabilities = ide_class.get_capabilities()
            if not capabilities.get("supports_hooks"):
                continue
        except Exception:
            # If we can't get capabilities, skip this IDE
            continue

        # For now, only claude-code has hook support
        # In the future, this can be extended to other tools
        if tool_name != "claude-code":
            continue

        # Create command function for this tool
        def make_hook_command(tool_name=tool_name, ide_class=ide_class):
            @common_hook_options
            @click.pass_context
            @log_command
            def hook_command(ctx, is_global, dry_run, recursive, include, exclude):
                f"""Install {ide_class.display_name} hooks."""
                # Check for mutual exclusivity of --global and --recursive
                validate_mutual_exclusivity(
                    is_global, recursive, "--global", "--recursive"
                )

                # Get flags from context hierarchy if not explicitly set
                if not dry_run:
                    dry_run = get_dry_run_from_context(ctx)
                if not recursive:
                    recursive = get_recursive_from_context(ctx)

                if recursive:
                    # Delegate to all_hooks for recursive installation
                    return ctx.invoke(
                        all_hooks,
                        is_global=False,
                        dry_run=dry_run,
                        recursive=True,
                        include=include,
                        exclude=exclude,
                    )

                results = []

                try:
                    result = claude_impl(is_global, dry_run)
                    results.append(result)
                except SystemExit as e:
                    echo(
                        f"Error installing {ide_class.display_name} hook: {e}", err=True
                    )
                    results.append(
                        InstallResult(
                            InstallStatus.FAILED,
                            f"{ide_class.display_name} hook",
                            "Failed",
                        )
                    )

                # Show installation summary
                show_installation_summary(results, dry_run, "Hooks Installation")

                # In dry-run mode, show preview message
                if dry_run and any(r.is_success for r in results):
                    echo(
                        "\nTo actually perform the installation, run the command without --dry-run"
                    )

                # Return appropriate exit code
                if results and any(r.is_error for r in results):
                    return handle_exit_code(ctx, ExitCode.INSTALLATION_ERROR)
                else:
                    return ExitCode.SUCCESS

            hook_command.__name__ = tool_name.replace("-", "_") + "_hook"
            return hook_command

        # Get aliases for this tool
        aliases = registry.get_aliases(tool_name)
        help_text = f"Install {ide_class.display_name} hooks"

        # If aliases exist, show all aliases as visible and hide canonical
        if aliases:
            # Register all aliases as visible
            for alias in aliases:
                alias_cmd = make_hook_command()
                hook_group.add_command(
                    click.command(
                        name=alias,
                        help=help_text,
                        hidden=False,
                    )(alias_cmd)
                )

            # Register canonical name as hidden
            canonical_cmd = make_hook_command()
            hook_group.add_command(
                click.command(
                    name=tool_name,
                    help=help_text,
                    hidden=True,
                )(canonical_cmd)
            )
        else:
            # No aliases, register canonical name as visible
            cmd = make_hook_command()
            hook_group.add_command(
                click.command(
                    name=tool_name,
                    help=help_text,
                    hidden=False,
                )(cmd)
            )


def attach_unified_commands(install_group):
    """Attach all unified commands to the install group.

    This function generates and attaches unified commands for all tools.
    For tools with multiple features (e.g., both mcp and hook), it installs all features.
    For tools with a single feature (e.g., only mcp), it installs that feature.

    Args:
        install_group: Click Group to attach commands to
    """
    # Get the mcp and hook groups from the install group
    mcp_group = install_group.commands.get("mcp")
    hook_group = install_group.commands.get("hook")

    registry = IDERegistry()

    for tool_name, ide_class in registry.ide_configs.items():
        # Check features using class method
        try:
            capabilities = ide_class.get_capabilities()
            supports_mcp = capabilities.get(
                "supports_mcp_global_config"
            ) or capabilities.get("supports_mcp_project_config")
            supports_hooks = capabilities.get("supports_hooks")

            # Skip tools that don't support any features
            if not supports_mcp and not supports_hooks:
                continue

            # Build features list
            features = []
            if supports_mcp:
                features.append("mcp")
            if supports_hooks:
                features.append("hook")

        except Exception:
            # If we can't get capabilities, skip this IDE
            continue

        # Create a factory function to generate fresh decorated functions
        def make_unified_command(
            tool_name=tool_name, ide_class=ide_class, features=features
        ):
            # Generate command function
            cmd_func = _create_unified_command_function(
                tool_name, ide_class, mcp_group, hook_group, features
            )

            # Add Click decorators in the correct order
            # Options must be applied BEFORE pass_context (innermost first)
            cmd_func = add_unified_options(cmd_func)
            cmd_func = log_command(cmd_func)
            cmd_func = click.pass_context(cmd_func)

            return cmd_func

        # Customize help text
        help_text = f"Install Zenable for {ide_class.display_name}"

        # Get aliases for this tool
        aliases = registry.get_aliases(tool_name)

        # If aliases exist, show all aliases as visible and hide canonical
        if aliases:
            # Register all aliases as visible
            for alias in aliases:
                alias_cmd = click.command(
                    name=alias,
                    help=help_text,
                    hidden=False,
                )(make_unified_command())
                install_group.add_command(alias_cmd)

            # Register canonical name as hidden
            canonical_cmd = click.command(
                name=tool_name,
                help=help_text,
                hidden=True,
            )(make_unified_command())
            install_group.add_command(canonical_cmd)
        else:
            # No aliases, register canonical name as visible
            cmd = click.command(
                name=tool_name,
                help=help_text,
                hidden=False,
            )(make_unified_command())
            install_group.add_command(cmd)
