"""Error handling utilities for production and development modes."""

import os
import sys
from typing import TYPE_CHECKING, NoReturn

from rich.console import Console

if TYPE_CHECKING:
    pass  # pyright: ignore[reportMissingImports]

console = Console()


def is_debug_mode() -> bool:
    """Check if debug mode is enabled via ANYT_DEBUG environment variable."""
    debug_value = os.getenv("ANYT_DEBUG", "false").lower()
    return debug_value in ("1", "true", "yes", "on")


def install_traceback_handler() -> None:
    """Install rich traceback handler if in debug mode."""
    if is_debug_mode():
        from rich.traceback import install

        install(show_locals=True, width=120, word_wrap=True)


def handle_api_error(error: Exception, context: str = "") -> NoReturn:
    """Handle API errors with user-friendly messages in production mode.

    Args:
        error: The exception that occurred
        context: Optional context about what operation failed (e.g., "adding comment")

    Raises:
        SystemExit: Always exits with code 1 after displaying error
    """
    # Import at runtime to avoid circular imports and missing module errors
    try:
        from sdk.generated.exceptions import HTTPException  # pyright: ignore[reportMissingImports]
    except ImportError:
        HTTPException = None

    # In debug mode, let the exception propagate for full stack trace
    if is_debug_mode():
        raise error

    # Production mode - show user-friendly error messages
    prefix = f"[red]Error{f' {context}' if context else ''}:[/red]"

    if HTTPException and isinstance(error, HTTPException):
        status_code = error.status_code  # pyright: ignore[reportAttributeAccessIssue]

        # Common HTTP error codes with helpful messages
        if status_code == 401:
            console.print(f"{prefix} Authentication failed")
            console.print("\nPlease check your API key:")
            console.print("  1. Ensure ANYT_API_KEY environment variable is set")
            console.print("  2. Verify the API key is valid and not expired")
            console.print(
                "  3. Check the API URL is correct (ANYT_API_URL or workspace config)"
            )
            console.print("\nExample:")
            console.print("  [cyan]export ANYT_API_KEY=anyt_agent_...[/cyan]")

        elif status_code == 403:
            console.print(f"{prefix} Permission denied")
            console.print(
                "\nYou don't have permission to perform this operation. Please check:"
            )
            console.print("  - You are using the correct workspace")
            console.print("  - Your API key has the required permissions")

        elif status_code == 404:
            console.print(f"{prefix} Resource not found")
            console.print("\nThe requested resource could not be found. Please check:")
            console.print("  - Task/workspace identifiers are correct")
            console.print("  - You have access to the workspace")

        elif status_code == 409:
            console.print(f"{prefix} Conflict")
            console.print(
                "\nThe operation conflicts with existing data (e.g., circular dependency)"
            )

        elif status_code == 422:
            console.print(f"{prefix} Validation error")
            console.print("\nThe data provided is invalid. Please check your input.")

        elif status_code >= 500:
            console.print(f"{prefix} Server error (HTTP {status_code})")
            console.print("\nThe AnyTask API server encountered an error.")
            console.print(
                "Please try again later or contact support if the issue persists."
            )

        else:
            console.print(f"{prefix} API request failed (HTTP {status_code})")
            console.print(f"\n{str(error)}")

    else:
        # Generic error handling
        console.print(f"{prefix} {str(error)}")

    # Debug mode hint
    console.print(
        "\n[dim]For detailed error information, run with: export ANYT_DEBUG=true[/dim]"
    )

    sys.exit(1)


def format_validation_error(error: Exception) -> str:
    """Format validation errors in a user-friendly way.

    Args:
        error: Validation exception

    Returns:
        Formatted error message
    """
    # Extract useful information from Pydantic validation errors
    error_str = str(error)

    # If it's a Pydantic error, try to extract field-specific messages
    if "validation error" in error_str.lower():
        return f"Invalid data: {error_str}"

    return error_str
