# -*- coding: utf-8 -*-

"""Common TUI components and base classes for RC CLI."""

from textual.screen import Screen
from textual.widgets import TextArea
from textual.binding import Binding
from textual import events


class BaseScreen(Screen):
    """Base screen with common functionality."""
    
    BINDINGS = [
        Binding("escape", "back", "Back", priority=True),
    ]
    
    def action_back(self) -> None:
        """Go back to previous screen."""
        self.app.pop_screen()


class ScrollableTextAreaMixin:
    """Mixin for screens with scrollable TextArea."""
    
    async def on_mouse_scroll_up(self, event: events.MouseScrollUp) -> None:
        """Handle scroll with reduced step for better UX."""
        control = event.control
        if isinstance(control, TextArea):
            control.action_scroll_up()
            event.stop()
    
    async def on_mouse_scroll_down(self, event: events.MouseScrollDown) -> None:
        """Handle scroll with reduced step for better UX."""
        control = event.control
        if isinstance(control, TextArea):
            control.action_scroll_down()
            event.stop()


class BaseInfoScreen(BaseScreen, ScrollableTextAreaMixin):
    """Base info screen with TextArea scrolling support."""
    
    def on_mount(self) -> None:
        """Initialize with scroll settings."""
        if hasattr(self, 'query_one'):
            try:
                text_area = self.query_one("#info-area", TextArea)
                text_area.show_line_numbers = False
            except Exception:
                # Fallback if info-area doesn't exist
                pass


class BaseResultScreen(BaseScreen, ScrollableTextAreaMixin):
    """Base screen for displaying results in TextArea."""
    
    def on_mount(self) -> None:
        """Initialize with scroll settings."""
        if hasattr(self, 'query_one'):
            try:
                result_area = self.query_one("#result-area", TextArea)
                result_area.show_line_numbers = False
            except Exception:
                # Fallback if result-area doesn't exist
                pass

