"""
Pagination utilities for displaying large datasets in CLI applications.
Provides flexible pagination with user interaction for better user experience.
"""

import sys
import time
from typing import List, Callable, Any, TypeVar
import typer

# Generic type for paginated items
T = TypeVar('T')

# Import OS for terminal interaction
import os


def get_single_key_input(prompt: str, continue_keys: List[str] = ['\r', '\n'], quit_keys: List[str] = ['q'], timeout: int = None) -> str:
    """
    Get single key input with immediate exit and timeout support.
    
    Args:
        prompt: Prompt message to display
        continue_keys: Keys that trigger continue action (default: Enter)
        quit_keys: Keys that trigger quit action (default: q)
        timeout: Timeout in seconds, None means no timeout
        
    Returns:
        str: 'continue', 'quit', 'timeout', or 'other'
    """
    typer.echo(prompt, nl=False)
    
    try:
        import tty
        import termios
        import select
        
        # Save original terminal settings
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        
        # Set to single character input mode
        tty.setraw(sys.stdin.fileno())
        
        try:
            if timeout is not None:
                # Use select for timeout detection
                ready, _, _ = select.select([sys.stdin], [], [], timeout)
                if not ready:
                    typer.echo("\n⏰ Timeout - automatically exiting...")
                    return 'timeout'
            
            # Read single character
            char = sys.stdin.read(1)
            
            # Process input
            if char.lower() in [k.lower() for k in quit_keys]:
                typer.echo(char)
                return 'quit'
            elif char in continue_keys:
                typer.echo("")  # New line
                return 'continue'
            else:
                typer.echo("")  # New line
                return 'other'
        finally:
            # Restore terminal settings
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
            
    except Exception:
        # If single character input fails, fallback to regular input
        typer.echo("")
        if timeout is not None:
            # Simple timeout implementation (less precise, but works as fallback)
            import signal
            def timeout_handler(signum, frame):
                raise TimeoutError("Input timeout")
            
            signal.signal(signal.SIGALRM, timeout_handler)
            signal.alarm(timeout)
            
            try:
                user_input = input().strip().lower()
                signal.alarm(0)  # Cancel timeout
                if user_input in [k.lower() for k in quit_keys]:
                    return 'quit'
                else:
                    return 'continue'
            except TimeoutError:
                signal.alarm(0)  # Cancel timeout
                typer.echo("\n⏰ Timeout - automatically exiting...")
                return 'timeout'
        else:
            user_input = input().strip().lower()
            if user_input in [k.lower() for k in quit_keys]:
                return 'quit'
            else:
                return 'continue'


def paginated_display(
    items: List[T], 
    display_func: Callable[[T, int], None], 
    title: str, 
    page_size: int = 5, 
    display_width: int = 50,
    start_index: int = 1
) -> bool:
    """
    Display items with pagination support.
    
    Args:
        items: List of items to display
        display_func: Function to display individual items, receives (item, index)
        title: Title to display before items
        page_size: Number of items per page
        display_width: Width for separator lines
        start_index: Starting index for item numbering
        
    Returns:
        bool: True if user completed viewing all items, False if user quit early
    """
    if not items:
        typer.echo(f"\n{title}")
        typer.echo("=" * display_width)
        typer.echo("   No items to display")
        typer.echo("=" * display_width)
        return True
    
    total_items = len(items)
    total_pages = (total_items + page_size - 1) // page_size
    current_page = 1
    
    # Display title
    typer.echo(f"\n{title}")
    typer.echo("=" * display_width)
    
    # Smart pagination: if items <= page_size, show all directly
    if total_items <= page_size:
        for i, item in enumerate(items):
            display_func(item, start_index + i)
        return True
    
    # Pagination for larger lists
    while current_page <= total_pages:
        start_idx = (current_page - 1) * page_size
        end_idx = min(start_idx + page_size, total_items)
        
        # Display items for current page
        for i in range(start_idx, end_idx):
            display_func(items[i], start_index + i)
        
        # Show pagination info
        remaining = total_items - end_idx
        if remaining > 0:
            # Get user input with single-key support
            result = get_single_key_input(f"\n({remaining} more) Press Enter or 'q': ")
            if result in ['quit', 'timeout']:
                return False  # User quit early or timed out
        else:
            # Last page
            break
        
        current_page += 1
    
    return True  # User completed viewing all items


def simple_pagination(items: List[Any], items_per_page: int = 10) -> None:
    """
    Simple pagination for displaying lists without custom formatting.
    
    Args:
        items: List of items to paginate
        items_per_page: Number of items to show per page
    """
    if not items:
        typer.echo("No items to display.")
        return
    
    total_items = len(items)
    total_pages = (total_items + items_per_page - 1) // items_per_page
    
    for page in range(total_pages):
        start_idx = page * items_per_page
        end_idx = min(start_idx + items_per_page, total_items)
        
        typer.echo(f"\n--- Page {page + 1}/{total_pages} ---")
        for i in range(start_idx, end_idx):
            typer.echo(f"{i + 1}. {items[i]}")
        
        if page < total_pages - 1:  # Not the last page
            typer.echo("\nPress Enter to continue to next page...")
            input()


def get_user_choice(prompt: str, valid_choices: List[str]) -> str:
    """
    Get user input with validation.
    
    Args:
        prompt: Prompt to display to user
        valid_choices: List of valid input choices
        
    Returns:
        User's valid choice
    """
    while True:
        choice = input(f"{prompt} ({'/'.join(valid_choices)}): ").strip().lower()
        if choice in [c.lower() for c in valid_choices]:
            return choice
        typer.echo(f"Invalid choice. Please choose from: {', '.join(valid_choices)}")


def confirm_action(message: str, default: bool = False) -> bool:
    """
    Ask user for yes/no confirmation.
    
    Args:
        message: Confirmation message
        default: Default choice if user just presses Enter
        
    Returns:
        User's boolean choice
    """
    default_text = "Y/n" if default else "y/N"
    choice = input(f"{message} [{default_text}]: ").strip().lower()
    
    if not choice:  # User just pressed Enter
        return default
    
    return choice in ['y', 'yes', 'true', '1'] 