# -*- coding: utf-8 -*-

"""List screen for all SP parameters."""

from textual.containers import Container, Horizontal, Vertical
from textual.widgets import Button, DataTable, Footer, Header, Label
from ...tui_common import BaseScreen
from ..service import sp_service


class SPListScreen(BaseScreen):
    """List screen for all SP parameters."""
    
    def compose(self):
        yield Header()
        with Vertical():
            with Container(id="list-container"):
                yield Label("📋 All Service Parameters", id="list-title")
                yield DataTable(id="sp-list")
                with Horizontal(id="list-buttons"):
                    yield Button("Refresh", id="refresh-btn", variant="primary")
                    yield Button("Search", id="search-btn")
                    yield Button("Back", id="back-btn")
        yield Footer()
    
    def on_mount(self) -> None:
        """Initialize the list screen."""
        table = self.query_one("#sp-list", DataTable)
        table.add_columns("SP ID", "Description")
        self.app.call_later(self._load_sp_list)
    
    async def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button press events."""
        if event.button.id == "refresh-btn":
            await self._load_sp_list()
        elif event.button.id == "search-btn":
            self.app.push_screen("search")
        elif event.button.id == "back-btn":
            self.action_back()
    
    async def _load_sp_list(self) -> None:
        """Load all SP parameters."""
        table = self.query_one("#sp-list", DataTable)
        table.clear()
        
        self.query_one("#list-title", Label).update("📋 Loading...")
        
        try:
            result = await sp_service.get_all_service_parameters()
            
            if not result.success:
                self.query_one("#list-title", Label).update(
                    f"❌ Error: {result.error_message}"
                )
                return
            
            service_parameters = result.data
            
            # Add results to table
            for sp_id, description in service_parameters.items():
                # Truncate description if too long
                display_desc = description
                if len(display_desc) > 60:
                    display_desc = display_desc[:57] + "..."
                table.add_row(sp_id, display_desc, key=sp_id)
            
            self.query_one("#list-title", Label).update(
                f"📋 {len(service_parameters)} Service Parameters"
            )
            
        except Exception as e:
            self.query_one("#list-title", Label).update(
                f"❌ Error: {str(e)}"
            )

