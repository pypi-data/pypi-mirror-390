# -*- coding: utf-8 -*-

"""Search screen for SP parameters."""

from textual.containers import Container, Horizontal, Vertical
from textual.widgets import Button, DataTable, Footer, Header, Input, Label
from ...tui_common import BaseScreen
from ..service import sp_service


class SPSearchScreen(BaseScreen):
    """Search screen for SP parameters."""
    
    def compose(self):
        yield Header()
        with Vertical():
            with Container(id="search-container"):
                yield Label("🔍 Search Service Parameters", id="search-title")
                yield Input(
                    placeholder="Enter search query...",
                    id="search-input"
                )
                yield DataTable(id="search-results")
                with Horizontal(id="search-buttons"):
                    yield Button("Search", id="search-btn", variant="primary")
                    yield Button("Clear", id="clear-btn")
                    yield Button("Back", id="back-btn")
        yield Footer()
    
    def on_mount(self) -> None:
        """Initialize the search screen."""
        table = self.query_one("#search-results", DataTable)
        table.add_columns("SP ID", "Description")
        self.query_one("#search-input", Input).focus()
    
    async def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button press events."""
        if event.button.id == "search-btn":
            await self._perform_search()
        elif event.button.id == "clear-btn":
            self.query_one("#search-input", Input).value = ""
            table = self.query_one("#search-results", DataTable)
            table.clear()
        elif event.button.id == "back-btn":
            self.action_back()
    
    async def on_input_submitted(self, event: Input.Submitted) -> None:
        """Handle input submission."""
        if event.input.id == "search-input":
            await self._perform_search()
    
    async def _perform_search(self) -> None:
        """Perform SP search."""
        input_widget = self.query_one("#search-input", Input)
        query = input_widget.value.strip()
        
        if not query:
            return
        
        table = self.query_one("#search-results", DataTable)
        table.clear()
        
        # Show loading
        self.query_one("#search-title", Label).update("🔍 Searching...")
        
        try:
            result = await sp_service.search_service_parameters(query)
            
            if not result.success:
                self.query_one("#search-title", Label).update(
                    f"❌ Error: {result.error_message}"
                )
                return
            
            matching_sps = result.data
            
            if not matching_sps:
                self.query_one("#search-title", Label).update(
                    f"🔍 No results found for '{query}'"
                )
                return
            
            # Add results to table
            for sp_id, description in matching_sps.items():
                # Truncate description if too long
                display_desc = description
                if len(display_desc) > 60:
                    display_desc = display_desc[:57] + "..."
                table.add_row(sp_id, display_desc, key=sp_id)
            
            self.query_one("#search-title", Label).update(
                f"🔍 Found {len(matching_sps)} results for '{query}'"
            )
            
        except Exception as e:
            self.query_one("#search-title", Label).update(
                f"❌ Error: {str(e)}"
            )

