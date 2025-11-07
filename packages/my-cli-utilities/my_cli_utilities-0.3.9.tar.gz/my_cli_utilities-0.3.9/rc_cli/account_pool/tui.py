# -*- coding: utf-8 -*-

"""Interactive TUI for Account Pool management."""

import asyncio
from typing import Optional, Dict, List, Any
from textual.app import App, ComposeResult
from textual.screen import Screen
from textual.containers import Container, Horizontal, Vertical
from textual.widgets import (
    Button,
    DataTable,
    Footer,
    Header,
    Input,
    Label,
    Select,
    TextArea,
)
from textual.binding import Binding
from textual import events
from .service import AccountService
from ..common.service_factory import ServiceFactory


# Display constants
DEFAULT_SEPARATOR_WIDTH = 60
MODAL_SEPARATOR_WIDTH = 110
MAX_DISPLAY_TEXT_LENGTH = 40
NOTIFICATION_TIMEOUT = 2
WARNING_TIMEOUT = 3


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


class BaseResultScreen(BaseScreen, ScrollableTextAreaMixin):
    """Base screen for displaying results in TextArea."""
    
    def on_mount(self) -> None:
        """Initialize with scroll settings."""
        if hasattr(self, 'query_one'):
            try:
                result_area = self.query_one("#result-area", TextArea)
                result_area.show_line_numbers = False
            except Exception:
                pass
    
    def _format_account_info(self, account: Dict, separator_width: int = DEFAULT_SEPARATOR_WIDTH, use_na_for_missing: bool = False) -> str:
        """
        Format account information for display - unified version.
        
        Args:
            account: Account dictionary
            separator_width: Width of separator line (default: DEFAULT_SEPARATOR_WIDTH)
            use_na_for_missing: If True, use 'N/A' for missing fields; otherwise skip them
        
        Returns:
            Formatted account information string
        """
        lines = []
        separator = "=" * separator_width
        lines.append(separator)
        lines.append("Account Information")
        lines.append(separator)
        
        # Helper function to format field
        def add_field(emoji: str, label: str, value: Any, show_if_none: bool = False):
            if value is not None or show_if_none:
                display_value = value if value is not None else 'N/A'
                lines.append(f"{emoji} {label}: {display_value}")
        
        # Show main fields (display phone with +, copy will remove it)
        if use_na_for_missing:
            add_field("📱", "Phone", account.get('mainNumber'), show_if_none=True)
            add_field("🆔", "Account ID", account.get('accountId'), show_if_none=True)
            add_field("🏷️ ", "Type", account.get('accountType'), show_if_none=True)
            add_field("🌐", "Environment", account.get('envName'), show_if_none=True)
            add_field("📧", "Email Domain", account.get('companyEmailDomain'), show_if_none=True)
            add_field("📅", "Created", account.get('createdAt'), show_if_none=True)
            add_field("🔗", "MongoDB ID", account.get('_id'), show_if_none=True)
        else:
            if account.get('mainNumber'):
                lines.append(f"📱 Phone: {account['mainNumber']}")
            if account.get('accountId'):
                lines.append(f"🆔 Account ID: {account['accountId']}")
            if account.get('accountType'):
                lines.append(f"🏷️  Type: {account['accountType']}")
            if account.get('envName'):
                lines.append(f"🌐 Environment: {account['envName']}")
            if account.get('companyEmailDomain'):
                lines.append(f"📧 Email Domain: {account['companyEmailDomain']}")
            if account.get('createdAt'):
                lines.append(f"📅 Created: {account['createdAt']}")
            if account.get('loginTimes') is not None:
                lines.append(f"🔢 Login Times: {account['loginTimes']}")
            if account.get('_id'):
                lines.append(f"🔗 MongoDB ID: {account['_id']}")
        
        # Status
        locked = account.get("locked", [])
        status = "🔒 Locked" if locked else "✅ Available"
        lines.append(f"🔐 Status: {status}")
        
        if locked:
            lines.append(f"🛑 Lock Details:")
            for item in locked:
                if isinstance(item, dict):
                    lines.append(f"  • Type: {item.get('accountType', 'N/A')}")
        
        lines.append(separator)
        return "\n".join(lines)

    async def _query_and_display_account(
        self,
        query_func: callable,
        title_label_id: str,
        loading_msg: str,
        success_msg: str = "✅ Account retrieved",
        validation_func: Optional[callable] = None,
        validation_error_msg: Optional[str] = None,
        *args,
        **kwargs
    ) -> None:
        """
        Generic method to query account and display result.
        
        Args:
            query_func: Synchronous function that returns account dict or (None, error_msg) tuple
            title_label_id: ID of the title label to update
            loading_msg: Message to show while loading
            success_msg: Message to show on success
            validation_func: Optional function to validate input, returns (is_valid, error_msg)
            validation_error_msg: Error message if validation fails (if validation_func not provided)
            *args, **kwargs: Arguments to pass to query_func
        """
        # Validate input if validation function provided
        if validation_func:
            is_valid, error_msg = validation_func()
            if not is_valid:
                self.query_one(f"#{title_label_id}", Label).update(
                    f"⚠️  {error_msg or validation_error_msg or 'Invalid input'}"
                )
                return
        
        result_area = self.query_one("#result-area", TextArea)
        self.query_one(f"#{title_label_id}", Label).update(loading_msg)
        result_area.text = ""
        
        try:
            account_service = ServiceFactory.get_account_service()
            
            loop = asyncio.get_event_loop()
            # Create a closure to capture the arguments
            def execute_query():
                return query_func(account_service, *args, **kwargs)
            
            result = await loop.run_in_executor(None, execute_query)
            
            if result is None or (isinstance(result, tuple) and result[0] is None):
                error_msg = result[1] if isinstance(result, tuple) else "Failed to get account"
                self.query_one(f"#{title_label_id}", Label).update(f"❌ {error_msg}")
                result_area.text = f"Error: {error_msg}"
                return
            
            account = result if not isinstance(result, tuple) else result[0]
            formatted_output = self._format_account_info(account)
            result_area.text = formatted_output
            self.query_one(f"#{title_label_id}", Label).update(success_msg)
            
        except Exception as e:
            self.query_one(f"#{title_label_id}", Label).update(f"❌ Error: {str(e)}")
            result_area.text = f"Error: {str(e)}"


class GetAccountByIdScreen(BaseResultScreen):
    """Screen for getting account by ID."""
    
    def compose(self) -> ComposeResult:
        yield Header()
        with Vertical():
            with Container(id="get-by-id-container"):
                yield Label("🆔 Get Account by ID", id="get-by-id-title")
                yield Input(placeholder="Account ID", id="account-id-input")
                yield Select(
                    [
                        ("webaqaxmn", "webaqaxmn"),
                        ("xmn-up", "xmn-up"),
                        ("glpdevxmn", "glpdevxmn"),
                    ],
                    id="env-select",
                    value="webaqaxmn",
                    prompt="Select environment..."
                )
                yield TextArea(id="result-area", read_only=True)
                with Horizontal(id="get-by-id-buttons"):
                    yield Button("Get Account", id="get-btn", variant="primary")
                    yield Button("Clear", id="clear-btn")
                    yield Button("Back", id="back-btn")
        yield Footer()
    
    def on_mount(self) -> None:
        """Initialize the get by ID screen."""
        super().on_mount()
        self.query_one("#account-id-input", Input).focus()
    
    async def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button press events."""
        if event.button.id == "get-btn":
            await self._get_account_by_id()
        elif event.button.id == "clear-btn":
            self.query_one("#account-id-input", Input).value = ""
            env_select = self.query_one("#env-select", Select)
            env_select.value = "webaqaxmn"
            self.query_one("#result-area", TextArea).text = ""
        elif event.button.id == "back-btn":
            self.action_back()
    
    async def on_input_submitted(self, event: Input.Submitted) -> None:
        """Handle input submission."""
        if event.input.id == "account-id-input":
            self.query_one("#env-select", Select).focus()
    
    async def _get_account_by_id(self) -> None:
        """Get account by ID."""
        account_id = self.query_one("#account-id-input", Input).value.strip()
        env_select = self.query_one("#env-select", Select)
        env_name = env_select.value if env_select.value and isinstance(env_select.value, str) else "webaqaxmn"
        
        def validate():
            if not account_id:
                return False, "Please enter Account ID"
            return True, None
        
        await self._query_and_display_account(
            query_func=self._get_account_by_id_sync,
            title_label_id="get-by-id-title",
            loading_msg="🆔 Loading...",
            validation_func=validate,
            account_id=account_id,
            env_name=env_name
        )
    
    def _get_account_by_id_sync(self, account_service: AccountService, account_id: str, env_name: str) -> Optional[Dict]:
        """Synchronous wrapper for getting account by ID."""
        try:
            from returns.pipeline import is_successful
            
            result = account_service.data_manager.get_account_by_id(account_id, env_name)
            
            if is_successful(result):
                return result.unwrap()
            else:
                error = result.failure()
                return (None, error.message)
        except Exception as e:
            return (None, str(e))


class GetAccountByPhoneScreen(BaseResultScreen):
    """Screen for getting account by phone number."""
    
    def compose(self) -> ComposeResult:
        yield Header()
        with Vertical():
            with Container(id="get-by-phone-container"):
                yield Label("📱 Get Account by Phone", id="get-by-phone-title")
                yield Input(placeholder="Phone Number", id="phone-input")
                yield Select(
                    [
                        ("webaqaxmn", "webaqaxmn"),
                        ("xmn-up", "xmn-up"),
                        ("glpdevxmn", "glpdevxmn"),
                    ],
                    id="env-select",
                    value="webaqaxmn",
                    prompt="Select environment..."
                )
                yield TextArea(id="result-area", read_only=True)
                with Horizontal(id="get-by-phone-buttons"):
                    yield Button("Get Account", id="get-btn", variant="primary")
                    yield Button("Clear", id="clear-btn")
                    yield Button("Back", id="back-btn")
        yield Footer()
    
    def on_mount(self) -> None:
        """Initialize the get by phone screen."""
        super().on_mount()
        self.query_one("#phone-input", Input).focus()
    
    async def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button press events."""
        if event.button.id == "get-btn":
            await self._get_account_by_phone()
        elif event.button.id == "clear-btn":
            self.query_one("#phone-input", Input).value = ""
            env_select = self.query_one("#env-select", Select)
            env_select.value = "webaqaxmn"
            self.query_one("#result-area", TextArea).text = ""
        elif event.button.id == "back-btn":
            self.action_back()
    
    async def on_input_submitted(self, event: Input.Submitted) -> None:
        """Handle input submission."""
        if event.input.id == "phone-input":
            self.query_one("#env-select", Select).focus()
    
    async def _get_account_by_phone(self) -> None:
        """Get account by phone number."""
        phone = self.query_one("#phone-input", Input).value.strip()
        env_select = self.query_one("#env-select", Select)
        env_name = env_select.value if env_select.value and isinstance(env_select.value, str) else "webaqaxmn"
        
        def validate():
            if not phone:
                return False, "Please enter Phone Number"
            return True, None
        
        await self._query_and_display_account(
            query_func=self._get_account_by_phone_sync,
            title_label_id="get-by-phone-title",
            loading_msg="📱 Loading...",
            validation_func=validate,
            phone=phone,
            env_name=env_name
        )
    
    def _get_account_by_phone_sync(self, account_service: AccountService, phone: str, env_name: str) -> Optional[Dict]:
        """Synchronous wrapper for getting account by phone."""
        try:
            from returns.pipeline import is_successful
            from my_cli_utilities_common.config import ValidationUtils
            
            main_number_str = ValidationUtils.normalize_phone_number(phone)
            if not main_number_str:
                return (None, "Invalid phone number format")
            
            result = account_service.data_manager.get_all_accounts_for_env(env_name).bind(
                lambda accounts: account_service._find_account_by_phone_in_list(accounts, main_number_str)
            )
            
            if is_successful(result):
                return result.unwrap()
            else:
                error = result.failure()
                return (None, error.message)
        except Exception as e:
            return (None, str(e))
    
    def _format_account_info(self, account: Dict) -> str:
        """Format account information for display."""
        lines = []
        lines.append("=" * 60)
        lines.append("Account Information")
        lines.append("=" * 60)
        lines.append(f"📱 Phone: {account.get('mainNumber', 'N/A')}")
        lines.append(f"🆔 Account ID: {account.get('accountId', 'N/A')}")
        lines.append(f"🏷️  Type: {account.get('accountType', 'N/A')}")
        lines.append(f"🌐 Environment: {account.get('envName', 'N/A')}")
        lines.append(f"📧 Email Domain: {account.get('companyEmailDomain', 'N/A')}")
        lines.append(f"📅 Created: {account.get('createdAt', 'N/A')}")
        lines.append(f"🔗 MongoDB ID: {account.get('_id', 'N/A')}")
        
        locked = account.get("locked", [])
        status = "🔒 Locked" if locked else "✅ Available"
        lines.append(f"🔐 Status: {status}")
        
        if locked:
            lines.append(f"🛑 Lock Details:")
            for item in locked:
                if isinstance(item, dict):
                    lines.append(f"  • Type: {item.get('accountType', 'N/A')}")
        
        lines.append("=" * 60)
        return "\n".join(lines)


class GetAccountByAliasScreen(BaseResultScreen):
    """Screen for getting account by alias with fuzzy matching."""
    
    BINDINGS = [
        Binding("escape", "back", "Back", priority=True),
        Binding("down", "focus_table", "Focus Table", show=False),
        Binding("up", "focus_input", "Focus Input", show=False),
        Binding("enter", "select_alias", "Select Alias", show=False),
        Binding("c", "copy_selected", "Copy Selected", show=True),
    ]
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._all_mappings = []  # Store all mappings for filtering
    
    def compose(self) -> ComposeResult:
        yield Header()
        with Vertical():
            with Container(id="get-by-alias-container"):
                yield Label("🏷️  Get Account by Alias", id="get-by-alias-title")
                yield Select([], id="alias-select", prompt="Select alias...")
                yield Input(placeholder="Alias (e.g., webAqaXmn) - Type to search...", id="alias-input")
                yield Select(
                    [
                        ("webaqaxmn", "webaqaxmn"),
                        ("xmn-up", "xmn-up"),
                        ("glpdevxmn", "glpdevxmn"),
                    ],
                    id="env-select",
                    value="webaqaxmn",
                    prompt="Select environment..."
                )
                yield TextArea(id="result-area", read_only=True)
                with Horizontal(id="get-by-alias-buttons"):
                    yield Button("Get Account", id="get-btn", variant="primary")
                    yield Button("Copy Selected", id="copy-btn", variant="success")
                    yield Button("Clear", id="clear-btn")
                    yield Button("Back", id="back-btn")
        yield Footer()
    
    def on_mount(self) -> None:
        """Initialize the get by alias screen."""
        super().on_mount()
        alias_select = self.query_one("#alias-select", Select)
        alias_select.styles.display = "none"  # Hide initially
        self.query_one("#alias-input", Input).focus()
        
        # Show immediate feedback
        title_label = self.query_one("#get-by-alias-title", Label)
        title_label.update("🏷️  Get Account by Alias (Initializing...)")
        
        # Load aliases asynchronously
        self.call_after_refresh(self._load_aliases)
        asyncio.create_task(self._load_aliases())
    
    async def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button press events."""
        if event.button.id == "get-btn":
            await self._get_account_by_alias()
        elif event.button.id == "copy-btn":
            self.action_copy_selected()
        elif event.button.id == "clear-btn":
            self.query_one("#alias-input", Input).value = ""
            env_select = self.query_one("#env-select", Select)
            env_select.value = "webaqaxmn"
            self.query_one("#result-area", TextArea).text = ""
            self._hide_suggestions()
        elif event.button.id == "back-btn":
            self.action_back()
    
    def on_input_changed(self, event: Input.Changed) -> None:
        """Handle input changes for fuzzy matching."""
        if event.input.id == "alias-input":
            # Trigger filtering when input changes
            self._filter_aliases(event.value)
    
    async def on_input_submitted(self, event: Input.Submitted) -> None:
        """Handle input submission."""
        if event.input.id == "alias-input":
            # If select is visible, focus on it to allow selection
            alias_select = self.query_one("#alias-select", Select)
            if alias_select.styles.display != "none":
                alias_select.focus()
            else:
                self.query_one("#env-select", Select).focus()
        # Environment select doesn't trigger query, user needs to click button
    
    def action_focus_input(self) -> None:
        """Focus the alias input."""
        self.query_one("#alias-input", Input).focus()
    
    def action_copy_selected(self) -> None:
        """Copy selected text from result area to clipboard."""
        try:
            import pyperclip
            
            result_area = self.query_one("#result-area", TextArea)
            text = result_area.text
            if not text or not text.strip():
                self.app.notify("No content to copy", severity="warning", timeout=2)
                return
            
            lines = text.split('\n') if text else []
            
            # Try to get selected text
            selected_text = None
            try:
                selection = result_area.selection
                if selection:
                    if hasattr(selection, 'selected_text') and selection.selected_text:
                        selected_text = selection.selected_text
                    elif hasattr(selection, 'start') and hasattr(selection, 'end'):
                        start, end = selection.start, selection.end
                        if start < end and text:
                            selected_text = text[start:end]
            except Exception:
                pass
            
            # If no selection, try to extract value from line at cursor position
            if not selected_text or not selected_text.strip():
                cursor_line = None
                try:
                    selection = result_area.selection
                    if selection and hasattr(selection, 'start'):
                        start = selection.start
                        if isinstance(start, tuple) and len(start) >= 1:
                            cursor_line = start[0]
                        elif isinstance(start, int):
                            # Calculate line number from character position
                            char_count = 0
                            for i, line in enumerate(lines):
                                line_len = len(line) + 1
                                if char_count + line_len > start:
                                    cursor_line = i
                                    break
                                char_count += line_len
                except Exception:
                    pass
                
                if cursor_line is not None and 0 <= cursor_line < len(lines):
                    line = lines[cursor_line].strip()
                    # Extract value after colon (e.g., "📱 Phone: 13476901535" -> "13476901535")
                    if ':' in line:
                        parts = line.split(':', 1)
                        if len(parts) > 1:
                            selected_text = parts[1].strip()
                        else:
                            selected_text = line
                    else:
                        selected_text = line
                else:
                    # No cursor position, copy all text
                    selected_text = text
            
            # Remove + from phone numbers if copying phone field
            if selected_text:
                # Check if it's a phone number line
                for line in lines:
                    if ('📱' in line or 'phone' in line.lower()) and selected_text in line:
                        # Remove + if present
                        if selected_text.startswith('+'):
                            selected_text = selected_text[1:]
                        break
                
                pyperclip.copy(selected_text)
                self.app.notify(f"Copied: {selected_text[:30]}{'...' if len(selected_text) > 30 else ''}", timeout=2)
            else:
                self.app.notify("Nothing selected to copy", severity="warning", timeout=2)
                
        except ImportError:
            self.app.notify("pyperclip not installed. Install with: pip install pyperclip", severity="error", timeout=5)
        except Exception as e:
            self.app.notify(f"Failed to copy: {str(e)}", severity="error", timeout=3)
    
    async def on_select_changed(self, event: Select.Changed) -> None:
        """Handle selection from Select dropdown."""
        if event.select.id == "alias-select":
            selected_alias = event.value
            # Check if it's a valid string (not Select.BLANK)
            if selected_alias and isinstance(selected_alias, str):
                self.query_one("#alias-input", Input).value = selected_alias
                event.select.styles.display = "none"
                self.query_one("#env-select", Select).focus()
    
    def _hide_suggestions(self) -> None:
        """Hide the suggestions select."""
        try:
            alias_select = self.query_one("#alias-select", Select)
            alias_select.styles.display = "none"
            title_label = self.query_one("#get-by-alias-title", Label)
            title_label.update("🏷️  Get Account by Alias")
        except Exception:
            pass
    
    async def _load_aliases(self) -> None:
        """Load aliases from GitLab."""
        try:
            title_label = self.query_one("#get-by-alias-title", Label)
            title_label.update("🏷️  Get Account by Alias (Loading...)")
            
            account_service = ServiceFactory.get_account_service()
            
            loop = asyncio.get_event_loop()
            mappings = await loop.run_in_executor(
                None,
                lambda: self._load_aliases_sync(account_service)
            )
            
            if mappings is None or (isinstance(mappings, tuple) and mappings[0] is None):
                # Silently fail - user can still type manually
                self._all_mappings = []
                title_label.update("🏷️  Get Account by Alias (No aliases loaded)")
                self.app.notify("Failed to load aliases", severity="warning", timeout=3)
                return
            
            # Store all mappings for filtering
            self._all_mappings = mappings
            title_label.update(f"🏷️  Get Account by Alias (Loaded {len(mappings)} aliases)")
            self.app.notify(f"Loaded {len(mappings)} aliases", timeout=2)
            
            # If there's text in the input, trigger filtering
            try:
                alias_input = self.query_one("#alias-input", Input)
                current_value = alias_input.value
                if current_value:
                    # Filter with current value
                    self._filter_aliases(current_value)
            except Exception:
                pass
            
        except Exception as e:
            # Silently fail - user can still type manually
            self._all_mappings = []
            title_label = self.query_one("#get-by-alias-title", Label)
            title_label.update(f"🏷️  Get Account by Alias (Load error)")
            self.app.notify(f"Error: {str(e)[:50]}", severity="error", timeout=5)
    
    def _load_aliases_sync(self, account_service: AccountService) -> Optional[List]:
        """Synchronous wrapper for loading aliases."""
        try:
            mappings = account_service.alias_service.get_mappings(False)
            result = list(mappings.values())
            return result
        except Exception:
            return None
    
    def _filter_aliases(self, search_term: str) -> None:
        """Filter aliases based on search term (fuzzy match)."""
        try:
            alias_select = self.query_one("#alias-select", Select)
            title_label = self.query_one("#get-by-alias-title", Label)
            
            if not self._all_mappings:
                # Try to load if not loaded yet
                title_label.update("🏷️  Get Account by Alias (Waiting for aliases...)")
                alias_select.styles.display = "none"
                return
            
            search_term = search_term.strip()
            
            # If no search term, hide suggestions
            if not search_term:
                title_label.update("🏷️  Get Account by Alias")
                alias_select.styles.display = "none"
                return
            
            search_term_lower = search_term.lower()
            
            # Fuzzy match: search in alias, brand, and kamino_key
            filtered = []
            for mapping in self._all_mappings:
                # Check if search term appears in any field (case-insensitive)
                if (search_term_lower in mapping.alias.lower() or
                    search_term_lower in mapping.brand.lower() or
                    search_term_lower in mapping.kamino_key.lower()):
                    filtered.append(mapping)
            
            # Limit to 10 results for better UX
            filtered = filtered[:10]
            
            # Update Select with filtered options
            if filtered:
                title_label.update(f"🏷️  Get Account by Alias (Found {len(filtered)} matches)")
                # Create options list: (display_text, alias_value)
                options = [(f"{mapping.alias} ({mapping.brand})", mapping.alias) for mapping in filtered]
                alias_select.set_options(options)
                alias_select.styles.display = "block"
            else:
                title_label.update(f"🏷️  Get Account by Alias (No matches for '{search_term}')")
                alias_select.styles.display = "none"
            
        except Exception as e:
            title_label.update(f"🏷️  Get Account by Alias (Error: {str(e)[:30]})")
    
    async def _get_account_by_alias(self) -> None:
        """Get account by alias."""
        alias = self.query_one("#alias-input", Input).value.strip()
        env_select = self.query_one("#env-select", Select)
        env_name = env_select.value if env_select.value and isinstance(env_select.value, str) else "webaqaxmn"
        account_type = None  # Account type is rarely used, alias already uniquely identifies account
        
        # Hide suggestions when querying
        self._hide_suggestions()
        
        def validate():
            if not alias:
                return False, "Please enter Alias"
            return True, None
        
        await self._query_and_display_account(
            query_func=self._get_account_by_alias_sync,
            title_label_id="get-by-alias-title",
            loading_msg="🏷️  Loading...",
            validation_func=validate,
            alias=alias,
            env_name=env_name,
            account_type=account_type
        )
    
    def _get_account_by_alias_sync(
        self,
        account_service: AccountService,
        alias: str,
        env_name: str,
        account_type: Optional[str]
    ) -> Optional[Dict]:
        """Synchronous wrapper for getting account by alias."""
        try:
            from returns.pipeline import is_successful
            
            # Get kaminoKey from alias
            mapping = account_service.alias_service.get_mapping_by_alias(alias)
            
            if not mapping:
                return (None, f"Alias '{alias}' not found in GitLab configuration")
            
            kamino_key = mapping.kamino_key
            result = account_service.data_manager.get_account_by_kamino_key(
                kamino_key,
                env_name,
                account_type
            )
            
            if is_successful(result):
                return result.unwrap()
            else:
                error = result.failure()
                return (None, error.message)
        except ValueError as e:
            return (None, str(e))
        except Exception as e:
            return (None, str(e))


class AccountQueryResultScreen(Screen):
    """Modal screen to display account query results with copy support."""
    
    BINDINGS = [
        Binding("escape", "back", "Back", priority=True),
        Binding("c", "copy_selected", "Copy Selected", show=True),
        Binding("a", "copy_all", "Copy All", show=True),
    ]
    
    def action_back(self) -> None:
        """Go back to previous screen."""
        self.app.pop_screen()
    
    def __init__(self, account: Dict, query_info: str, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.account = account
        self.query_info = query_info
    
    def _format_account_info(self, account: Dict) -> str:
        """Format account information for display with modal width."""
        # Use modal separator width and don't show N/A for missing fields
        return BaseResultScreen._format_account_info(self, account, separator_width=MODAL_SEPARATOR_WIDTH, use_na_for_missing=False)
    
    def compose(self) -> ComposeResult:
        yield Header()
        with Vertical():
            with Container(id="account-result-modal-container"):
                yield Label(f"✅ Account Found: {self.query_info}", id="modal-title")
                yield TextArea(
                    "",
                    read_only=True,
                    show_line_numbers=False,
                    id="modal-result-area"
                )
            with Horizontal(id="modal-buttons"):
                yield Button("Copy Selected", id="copy-selected-btn", variant="success")
                yield Button("Copy All", id="copy-all-btn")
                yield Button("Back", id="back-btn", variant="primary")
        yield Footer()
    
    def on_mount(self) -> None:
        """Initialize the screen with account data."""
        result_area = self.query_one("#modal-result-area", TextArea)
        formatted_output = self._format_account_info(self.account)
        result_area.text = formatted_output
        result_area.show_line_numbers = False
    
    async def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button presses."""
        if event.button.id == "copy-selected-btn":
            self.action_copy_selected()
        elif event.button.id == "copy-all-btn":
            self.action_copy_all()
        elif event.button.id == "back-btn":
            self.app.pop_screen()
    
    def _extract_field_value(self, field_name: str) -> str:
        """Extract a specific field value from account dict."""
        field_mapping = {
            'phone': ('mainNumber', 'phone'),
            'account_id': ('accountId', '_id'),
            'type': ('accountType',),
            'env': ('envName',),
            'email': ('companyEmailDomain',),
            'created': ('createdAt',),
            'login_times': ('loginTimes',),
        }
        
        field_name_lower = field_name.lower().replace(' ', '_')
        keys = field_mapping.get(field_name_lower, [])
        
        for key in keys:
            value = self.account.get(key)
            if value is not None:
                result = str(value)
                # Remove leading + for phone numbers
                if field_name_lower == 'phone' and result.startswith('+'):
                    result = result[1:]
                return result
        
        return ""
    
    def action_copy_selected(self) -> None:
        """Copy selected text or smart field extraction from TextArea to clipboard."""
        try:
            import pyperclip
            
            result_area = self.query_one("#modal-result-area", TextArea)
            text = result_area.text
            lines = text.split('\n') if text else []  # Initialize lines early for reuse
            
            # Try to get selected text using different methods
            selected_text = None
            
            # Method 1: Try selection.selected_text if available
            try:
                selection = result_area.selection
                if selection:
                    if hasattr(selection, 'selected_text') and selection.selected_text:
                        selected_text = selection.selected_text
                    elif hasattr(selection, 'start') and hasattr(selection, 'end'):
                        start, end = selection.start, selection.end
                        if start < end and text:
                            selected_text = text[start:end]
            except Exception:
                pass
            
            # Method 2: If no selection, try to extract value from line at cursor position
            if not selected_text or not selected_text.strip():
                # Try to get cursor position from selection start
                cursor_pos = None
                try:
                    selection = result_area.selection
                    if selection and hasattr(selection, 'start'):
                        start = selection.start
                        # Handle both int and tuple (line, column) formats
                        if isinstance(start, tuple) and len(start) >= 1:
                            # If it's a tuple, use the line number directly
                            cursor_line = start[0]
                            if 0 <= cursor_line < len(lines):
                                line = lines[cursor_line].strip()
                                # Try to extract just the value (after colon or emoji)
                                if ':' in line:
                                    parts = line.split(':')
                                    if len(parts) > 1:
                                        value = ':'.join(parts[1:]).strip()
                                        if value:
                                            selected_text = value
                                        else:
                                            selected_text = line
                                    else:
                                        selected_text = line
                                else:
                                    selected_text = line
                        elif isinstance(start, int):
                            cursor_pos = start
                except Exception:
                    pass
                
                # If we have a cursor position (int), calculate which line it's on
                if cursor_pos is not None and isinstance(cursor_pos, int) and cursor_pos >= 0:
                    # Count characters up to cursor position to find the line
                    char_count = 0
                    cursor_line = 0
                    for i, line in enumerate(lines):
                        line_len = len(line) + 1  # +1 for newline
                        if char_count + line_len > cursor_pos:
                            cursor_line = i
                            break
                        char_count += line_len
                    
                    if 0 <= cursor_line < len(lines):
                        line = lines[cursor_line].strip()
                        
                        # Try to extract just the value (after colon or emoji)
                        # Example: "📱 Phone: +13476901535" -> "+13476901535"
                        if ':' in line:
                            # Extract value after the last colon
                            parts = line.split(':')
                            if len(parts) > 1:
                                value = ':'.join(parts[1:]).strip()
                                if value:
                                    selected_text = value
                                else:
                                    selected_text = line
                            else:
                                selected_text = line
                        else:
                            selected_text = line
                
                # Method 3: If still no text, try smart field extraction based on line content
                if not selected_text or not selected_text.strip():
                    # Parse the displayed text to extract field values
                    for line in lines:
                        line_lower = line.lower()
                        if 'phone' in line_lower and ':' in line:
                            selected_text = self._extract_field_value('phone')
                            break
                        elif 'account id' in line_lower and ':' in line:
                            selected_text = self._extract_field_value('account_id')
                            break
                        elif 'type' in line_lower and ':' in line and 'account' not in line_lower:
                            selected_text = self._extract_field_value('type')
                            break
                
                # If still no text, ask user to select text manually
                if not selected_text or not selected_text.strip():
                    self.app.notify("⚠️  Please select text or use 'Copy All' (a)", severity="warning", timeout=WARNING_TIMEOUT)
                    return
            
            if not selected_text or not selected_text.strip():
                self.app.notify("⚠️  No text to copy. Select text or use 'Copy All' (a)", severity="warning", timeout=WARNING_TIMEOUT)
                return
            
            # Copy to clipboard
            text_to_copy = selected_text.strip()
            # Remove leading + for phone numbers
            if text_to_copy.startswith('+'):
                # Check if the copied text is from a Phone line
                # Reuse the lines variable that was already retrieved earlier
                for line in lines:
                    if ('phone' in line.lower() or '📱' in line) and text_to_copy in line:
                        text_to_copy = text_to_copy.lstrip('+')
                        break
            
            pyperclip.copy(text_to_copy)
            
            # Show notification with truncated value
            display_text = text_to_copy[:MAX_DISPLAY_TEXT_LENGTH] + "..." if len(text_to_copy) > MAX_DISPLAY_TEXT_LENGTH else text_to_copy
            self.app.notify(f"✅ Copied: {display_text}", timeout=NOTIFICATION_TIMEOUT)
                
        except ImportError:
            self.app.notify("❌ pyperclip not installed. Please install it: pip install pyperclip", severity="error", timeout=5)
        except Exception as e:
            import traceback
            error_msg = f"❌ Failed to copy: {str(e)}"
            self.app.notify(error_msg, severity="error", timeout=5)
            print(f"Copy error details: {traceback.format_exc()}")
    
    def action_copy_all(self) -> None:
        """Copy all account information to clipboard."""
        try:
            import pyperclip
            
            # Get the text from the TextArea
            result_area = self.query_one("#modal-result-area", TextArea)
            text_to_copy = result_area.text
            
            if not text_to_copy:
                # Fallback: format the account info again
                text_to_copy = self._format_account_info(self.account)
            
            # Remove + from phone numbers in the text
            lines = text_to_copy.split('\n')
            processed_lines = []
            for line in lines:
                if ('phone' in line.lower() or '📱' in line) and ':' in line:
                    # Extract and process phone number
                    parts = line.split(':', 1)
                    if len(parts) == 2:
                        label = parts[0]
                        value = parts[1].strip()
                        if value.startswith('+'):
                            value = value[1:]
                        processed_lines.append(f"{label}: {value}")
                    else:
                        processed_lines.append(line)
                else:
                    processed_lines.append(line)
            text_to_copy = '\n'.join(processed_lines)
            
            # Copy to clipboard
            pyperclip.copy(text_to_copy)
            
            # Verify it was copied (optional check)
            copied_text = pyperclip.paste()
            if copied_text == text_to_copy:
                self.app.notify("✅ Account info copied to clipboard!", timeout=2)
            else:
                self.app.notify("⚠️  Copy may have failed - please try again", severity="warning", timeout=3)
                
        except ImportError:
            self.app.notify("❌ pyperclip not installed. Please install it: pip install pyperclip", severity="error", timeout=5)
        except Exception as e:
            import traceback
            error_msg = f"❌ Failed to copy: {str(e)}"
            self.app.notify(error_msg, severity="error", timeout=5)
            print(f"Copy error details: {traceback.format_exc()}")


class ListAliasesScreen(BaseScreen):
    """Screen for listing aliases."""
    
    BINDINGS = [
        Binding("escape", "back", "Back", priority=True),
        Binding("c", "copy_selected", "Copy", show=True),
        Binding("/", "focus_search", "Search", show=True),
        Binding("enter", "query_account", "Query", show=True),
        Binding("r", "query_account", "Query", show=True),
    ]
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._all_mappings = []  # Store all mappings for filtering
    
    def compose(self) -> ComposeResult:
        yield Header()
        with Vertical():
            with Container(id="list-aliases-container"):
                yield Label("🏷️  List Aliases", id="list-aliases-title")
                yield Input(placeholder="🔍 Search aliases (fuzzy match)...", id="search-input")
                yield DataTable(id="aliases-table", cursor_type="cell")
                with Horizontal(id="list-aliases-buttons"):
                    yield Button("Load Aliases", id="load-btn", variant="primary")
                    yield Button("Refresh", id="refresh-btn")
                    yield Button("Copy Cell", id="copy-btn")
                    yield Button("Query Account", id="query-account-btn", variant="success")
                    yield Button("Clear Search", id="clear-search-btn")
                    yield Button("Back", id="back-btn")
        yield Footer()
    
    def on_mount(self) -> None:
        """Initialize the list aliases screen."""
        table = self.query_one("#aliases-table", DataTable)
        table.add_column("#", width=5)
        table.add_column("Alias", width=32)
        table.add_column("Brand", width=10)
        table.add_column("Kamino Key")  # No width specified - takes remaining space
        self.app.call_later(self._load_aliases, False)
    
    def action_focus_search(self) -> None:
        """Focus the search input."""
        search_input = self.query_one("#search-input", Input)
        search_input.focus()
    
    async def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button press events."""
        if event.button.id == "load-btn":
            await self._load_aliases(False)
        elif event.button.id == "refresh-btn":
            await self._load_aliases(True)
        elif event.button.id == "copy-btn":
            self.action_copy_selected()
        elif event.button.id == "query-account-btn":
            await self.action_query_account()
        elif event.button.id == "clear-search-btn":
            search_input = self.query_one("#search-input", Input)
            search_input.value = ""
            self._filter_aliases("")
        elif event.button.id == "back-btn":
            self.action_back()
    
    def on_input_changed(self, event: Input.Changed) -> None:
        """Handle search input changes."""
        if event.input.id == "search-input":
            self._filter_aliases(event.value)
    
    def action_copy_selected(self) -> None:
        """Copy selected cell to clipboard."""
        table = self.query_one("#aliases-table", DataTable)
        
        if table.row_count == 0:
            self.app.notify("No data to copy", severity="warning", timeout=2)
            return
        
        try:
            # Get cursor position (row, column)
            cursor_row = table.cursor_row
            cursor_col = table.cursor_column
            
            if cursor_row is None or cursor_col is None:
                self.app.notify("No cell selected", severity="warning", timeout=2)
                return
            
            # Get cell value
            cell_value = table.get_cell_at((cursor_row, cursor_col))
            copy_text = str(cell_value)
            
            # Copy to clipboard
            import pyperclip
            pyperclip.copy(copy_text)
            
            # Get column name for better notification
            columns = ["#", "Alias", "Brand", "Kamino Key"]
            col_name = columns[cursor_col] if cursor_col < len(columns) else "Cell"
            
            # Show notification with truncated preview
            preview = copy_text[:40] + "..." if len(copy_text) > 40 else copy_text
            self.app.notify(f"✅ Copied {col_name}: {preview}", timeout=2)
            
        except ImportError:
            self.app.notify("⚠️  pyperclip not installed. Install with: pip install pyperclip", 
                          severity="error", timeout=5)
        except Exception as e:
            self.app.notify(f"❌ Copy failed: {str(e)}", severity="error", timeout=3)
    
    async def action_query_account(self) -> None:
        """Query account using the selected row's alias or kamino key."""
        table = self.query_one("#aliases-table", DataTable)
        
        if table.row_count == 0:
            self.app.notify("No data available", severity="warning", timeout=2)
            return
        
        try:
            # Get cursor position
            cursor_row = table.cursor_row
            cursor_col = table.cursor_column
            
            if cursor_row is None or cursor_row < 0:
                self.app.notify("Please select a row first", severity="warning", timeout=2)
                return
            
            # Get the row data (columns: #, Alias, Brand, Kamino Key)
            alias = str(table.get_cell_at((cursor_row, 1)))
            kamino_key = str(table.get_cell_at((cursor_row, 3)))
            
            # Determine query method based on selected column
            # Column 1 = Alias, Column 3 = Kamino Key
            use_alias = (cursor_col == 1)
            
            if use_alias and alias:
                # Query by alias
                self.app.notify(f"🔍 Querying account by Alias: {alias}", timeout=2)
                query_param = ('alias', alias)
            elif kamino_key:
                # Query by kamino key (default)
                self.app.notify(f"🔍 Querying account by Kamino Key from: {alias}", timeout=2)
                query_param = ('kamino_key', kamino_key)
            else:
                self.app.notify("No valid query parameter found", severity="warning", timeout=2)
                return
            
            # Query account
            account_service = ServiceFactory.get_account_service()
            loop = asyncio.get_event_loop()
            
            result = await loop.run_in_executor(
                None,
                lambda: self._query_account_sync(account_service, query_param, alias)
            )
            
            if result is None or (isinstance(result, tuple) and result[0] is None):
                error_msg = result[1] if isinstance(result, tuple) else "Failed to query account"
                self.app.notify(f"❌ {error_msg}", severity="error", timeout=5)
                return
            
            # Create a result screen to display the account info
            account = result if not isinstance(result, tuple) else result[0]
            self._show_account_result_popup(account, alias, query_param[1])
            
        except Exception as e:
            self.app.notify(f"❌ Query failed: {str(e)}", severity="error", timeout=3)
    
    def _query_account_sync(self, account_service: AccountService, query_param: tuple, display_name: str):
        """Synchronous wrapper for querying account by alias or kamino key.
        
        Args:
            account_service: Service instance
            query_param: Tuple of (query_type, query_value) where query_type is 'alias' or 'kamino_key'
            display_name: Name to display in messages
        """
        try:
            from returns.pipeline import is_successful
            
            query_type, query_value = query_param
            
            if query_type == 'alias':
                # Query by alias - use the alias service to get kamino key first
                mapping = account_service.alias_service.get_mapping_by_alias(query_value)
                if not mapping:
                    return (None, f"Alias '{query_value}' not found")
                
                # Use the kamino key from the mapping
                result = account_service.data_manager.get_account_by_kamino_key(
                    kamino_key=mapping.kamino_key,
                    env_name=AccountService.DEFAULT_ENV_NAME
                )
            else:
                # Query by kamino key directly
                result = account_service.data_manager.get_account_by_kamino_key(
                    kamino_key=query_value,
                    env_name=AccountService.DEFAULT_ENV_NAME
                )
            
            # Don't use handler in TUI - it calls typer.Exit() which crashes the TUI!
            # Instead, manually unwrap the Result
            if is_successful(result):
                account = result.unwrap()
                return account
            else:
                # Get error from Failure
                error = result.failure()
                return (None, str(error))
            
        except Exception as e:
            return (None, str(e))
    
    def _show_account_result_popup(self, account: Dict, alias: str, kamino_key: str) -> None:
        """Show account result in a modal screen."""
        if not account:
            self.app.notify("❌ No account found", severity="warning", timeout=3)
            return
        
        try:
            # Create the result screen
            result_screen = AccountQueryResultScreen(account, alias)
            
            # Push the screen - AccountPoolTUIApp.push_screen now supports Screen instances
            self.app.push_screen(result_screen)
            
        except Exception as e:
            import traceback
            error_details = traceback.format_exc()
            self.app.notify(f"❌ Failed to show result: {str(e)}", severity="error", timeout=5)
            print(f"Error details: {error_details}")
    
    async def _load_aliases(self, force_refresh: bool = False) -> None:
        """Load aliases from GitLab."""
        table = self.query_one("#aliases-table", DataTable)
        table.clear()
        
        title = "🏷️  Refreshing..." if force_refresh else "🏷️  Loading..."
        self.query_one("#list-aliases-title", Label).update(title)
        
        try:
            account_service = ServiceFactory.get_account_service()
            
            loop = asyncio.get_event_loop()
            mappings = await loop.run_in_executor(
                None,
                lambda: self._load_aliases_sync(account_service, force_refresh)
            )
            
            if mappings is None or (isinstance(mappings, tuple) and mappings[0] is None):
                error_msg = mappings[1] if isinstance(mappings, tuple) else "Failed to load aliases"
                self.query_one("#list-aliases-title", Label).update(f"❌ {error_msg}")
                return
            
            # Store all mappings for filtering
            self._all_mappings = mappings
            
            # Add results to table
            for i, mapping in enumerate(mappings, 1):
                table.add_row(
                    str(i),
                    mapping.alias,
                    mapping.brand,
                    mapping.kamino_key,
                    key=str(i)
                )
            
            title_text = f"🏷️  {len(mappings)} Alias(es) Found"
            if force_refresh:
                title_text += " (Refreshed)"
            self.query_one("#list-aliases-title", Label).update(title_text)
            
        except Exception as e:
            self.query_one("#list-aliases-title", Label).update(f"❌ Error: {str(e)}")
    
    def _filter_aliases(self, search_term: str) -> None:
        """Filter aliases based on search term (fuzzy match)."""
        table = self.query_one("#aliases-table", DataTable)
        table.clear()
        
        if not self._all_mappings:
            return
        
        search_term = search_term.lower().strip()
        
        # If no search term, show all
        if not search_term:
            filtered = self._all_mappings
        else:
            # Fuzzy match: search in alias, brand, and kamino_key
            filtered = []
            for mapping in self._all_mappings:
                # Check if search term appears in any field (case-insensitive)
                if (search_term in mapping.alias.lower() or
                    search_term in mapping.brand.lower() or
                    search_term in mapping.kamino_key.lower()):
                    filtered.append(mapping)
        
        # Add filtered results to table
        for i, mapping in enumerate(filtered, 1):
            table.add_row(
                str(i),
                mapping.alias,
                mapping.brand,
                mapping.kamino_key,
                key=str(i)
            )
        
        # Update title
        if search_term:
            title_text = f"🔍 {len(filtered)} / {len(self._all_mappings)} Alias(es) (filtered)"
        else:
            title_text = f"🏷️  {len(filtered)} Alias(es) Found"
        self.query_one("#list-aliases-title", Label).update(title_text)
    
    def _load_aliases_sync(self, account_service: AccountService, force_refresh: bool) -> Optional[List]:
        """Synchronous wrapper for loading aliases."""
        try:
            mappings = account_service.alias_service.get_mappings(force_refresh)
            return list(mappings.values())
        except ValueError as e:
            return (None, str(e))
        except Exception as e:
            return (None, str(e))


class MainMenuScreen(BaseScreen):
    """Main menu screen."""
    
    BINDINGS = [
        Binding("q", "quit", "Quit", priority=True),
        Binding("escape", "quit", "Quit", priority=True),
        Binding("up", "move_up", "Move Up", priority=True),
        Binding("down", "move_down", "Move Down", priority=True),
        Binding("enter", "select", "Select", priority=True),
    ]
    
    button_ids = [
        "get-by-phone-btn",
        "get-by-alias-btn",
        "list-aliases-btn",
        "exit-btn",
    ]
    selected_index = 0
    
    def compose(self) -> ComposeResult:
        yield Header()
        with Vertical():
            with Container(id="menu-container"):
                yield Label("🏦 Account Pool Management", id="menu-title")
                with Vertical(id="menu-buttons"):
                    yield Button("📱 Get Account by Phone", id="get-by-phone-btn", variant="primary")
                    yield Button("🏷️  Get Account by Alias", id="get-by-alias-btn")
                    yield Button("📋 List Aliases", id="list-aliases-btn")
                    yield Button("❌ Exit", id="exit-btn")
        yield Footer()
    
    def on_mount(self) -> None:
        """Initialize menu with first button focused."""
        self._update_selection()
    
    def action_quit(self) -> None:
        """Quit the application."""
        self.app.exit()
    
    def on_key(self, event: events.Key) -> None:
        """Handle key events explicitly."""
        if event.key == "escape":
            self.app.exit()
            event.prevent_default()
        # Let other keys be handled by default processing
    
    def action_move_up(self) -> None:
        """Move selection up."""
        if self.selected_index > 0:
            self.selected_index -= 1
            self._update_selection()
    
    def action_move_down(self) -> None:
        """Move selection down."""
        if self.selected_index < len(self.button_ids) - 1:
            self.selected_index += 1
            self._update_selection()
    
    def action_select(self) -> None:
        """Select the current menu item."""
        button_id = self.button_ids[self.selected_index]
        button = self.query_one(f"#{button_id}", Button)
        button.press()
    
    def _update_selection(self) -> None:
        """Update button selection state."""
        for i, button_id in enumerate(self.button_ids):
            button = self.query_one(f"#{button_id}", Button)
            if i == self.selected_index:
                button.variant = "primary"
                button.focus()
            else:
                button.variant = "default"
    
    async def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button press events."""
        if event.button.id == "get-by-phone-btn":
            self.app.push_screen("get_by_phone")
        elif event.button.id == "get-by-alias-btn":
            self.app.push_screen("get_by_alias")
        elif event.button.id == "list-aliases-btn":
            self.app.push_screen("list_aliases")
        elif event.button.id == "exit-btn":
            self.app.exit()


class AccountPoolTUIApp(App):
    """Main TUI application for Account Pool management."""
    
    CSS = """
    Screen {
        align: center middle;
        layout: vertical;
    }
    
    #menu-container {
        width: auto;
        min-width: 50;
        max-width: 80;
        height: auto;
        border: solid $primary;
        padding: 1;
    }
    
    #menu-title {
        text-align: center;
        width: 100%;
        margin: 1;
    }
    
    #menu-buttons {
        width: 100%;
        height: auto;
    }
    
    #menu-buttons > Button {
        width: 100%;
        margin: 1;
    }
    
    #get-by-phone-container, #get-by-alias-container, #list-aliases-container {
        width: auto;
        min-width: 70;
        max-width: 90%;
        height: auto;
        max-height: 85vh;
        border: solid $primary;
        padding: 1;
        layout: vertical;
    }
    
    #get-by-alias-container {
        height: auto;
    }
    
    #account-result-modal-container {
        width: auto;
        min-width: 80;
        max-width: 95%;
        height: auto;
        border: solid $primary;
        padding: 1;
    }
    
    #get-by-phone-title, #get-by-alias-title, #list-aliases-title, #modal-title {
        text-align: center;
        width: 100%;
        margin: 1;
    }
    
    #types-table, #aliases-table {
        height: 1fr;
        min-height: 15;
        max-height: 30;
        width: 100%;
    }
    
    #alias-select, #env-select {
        width: 100%;
        margin-bottom: 1;
    }
    
    #result-area {
        height: auto;
        min-height: 8;
        max-height: 20;
        width: 100%;
    }
    
    #get-by-alias-container > #result-area,
    #get-by-phone-container > #result-area,
    #get-by-id-container > #result-area {
        height: auto;
        min-height: 10;
        max-height: 30vh;
    }
    
    #get-by-alias-container,
    #get-by-phone-container,
    #get-by-id-container {
        height: auto;
        max-height: 85vh;
        overflow-y: auto;
    }
    
    #modal-result-area {
        height: auto;
        min-height: 15;
        max-height: 40vh;
        width: 100%;
    }
    
    #phone-input, #alias-input, #account-id-input {
        width: 100%;
        margin: 1;
    }
    
    #get-by-phone-buttons, #get-by-alias-buttons, #list-aliases-buttons, #modal-buttons {
        width: 100%;
        height: auto;
        margin-top: 1;
        layout: horizontal;
    }
    
    #get-by-phone-buttons > Button, #get-by-alias-buttons > Button,
    #list-aliases-buttons > Button, #modal-buttons > Button {
        margin: 1;
        min-width: 10;
        width: 1fr;
    }
    """
    
    TITLE = "Account Pool Management TUI"
    BINDINGS = [
        Binding("q", "quit", "Quit", priority=True),
    ]
    
    def on_mount(self) -> None:
        """Set up the initial screen."""
        self.push_screen("main")
    
    def action_quit(self) -> None:
        """Quit the application."""
        self.exit()
    
    def action_back(self) -> None:
        """Go back to previous screen."""
        if len(self.screen_stack) > 1:
            self.pop_screen()
    
    def push_screen(self, screen_name_or_instance) -> None:
        """Push a screen by name or Screen instance."""
        # If it's already a Screen instance, push it directly
        from textual.screen import Screen as TextualScreen
        if isinstance(screen_name_or_instance, TextualScreen):
            super().push_screen(screen_name_or_instance)
            return
        
        # Otherwise, treat it as a string name and look it up
        screens = {
            "main": MainMenuScreen(),
            "get_by_phone": GetAccountByPhoneScreen(),
            "get_by_alias": GetAccountByAliasScreen(),
            "list_aliases": ListAliasesScreen(),
        }
        
        if screen_name_or_instance in screens:
            super().push_screen(screens[screen_name_or_instance])


def run_tui():
    """Run the TUI application."""
    try:
        app = AccountPoolTUIApp()
        app.run()
    except Exception as e:
        import sys
        print(f"Error running TUI: {e}", file=sys.stderr)
        raise


if __name__ == "__main__":
    run_tui()

