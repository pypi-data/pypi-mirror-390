"""Context panel widget for displaying parameter information."""
from typing import Any, Dict, Optional
from textual.app import ComposeResult
from textual.widgets import Static, Label
from textual.containers import Vertical
from rich.panel import Panel
from rich.text import Text
from rich.table import Table
from rich.console import Group


class ContextPanel(Static):
    """Widget for displaying contextual help and information."""

    def __init__(self, **kwargs):
        """Initialize the context panel."""
        super().__init__(**kwargs)
        self.current_field: Optional[Dict] = None
        self.current_value: Any = None

    def compose(self) -> ComposeResult:
        """Compose the context panel."""
        with Vertical(id="context-container"):
            yield Static(
                Panel(
                    "Select a parameter to see details",
                    title="📋 Context",
                    border_style="dim",
                ),
                id="context-content"
            )

    def show_field_info(self, field: Dict, current_value: Any = None) -> None:
        """Display information about a field."""
        self.current_field = field
        self.current_value = current_value

        # Build info panel
        field_name = field["arg"].lstrip("-").replace("-", "_")
        field_type = field.get("type", str).__name__
        field_help = field.get("help", "No description available")
        field_default = field.get("default")
        field_scope = field.get("scope", ["all"])
        field_group = field.get("group", "Other")

        # Create a table for field info
        table = Table(show_header=False, box=None, padding=0)
        table.add_column("Key", style="cyan", no_wrap=True)
        table.add_column("Value")

        table.add_row("Field", field_name)
        table.add_row("Type", field_type)
        table.add_row("Group", field_group)

        # Scope
        if "all" in field_scope:
            scope_str = "All trainers"
        else:
            scope_str = ", ".join(field_scope)
        table.add_row("Scope", scope_str)

        # Default value
        if field_default is not None:
            table.add_row("Default", str(field_default))

        # Current value
        if current_value is not None and current_value != field_default:
            table.add_row("Current", f"[yellow]{current_value}[/yellow]")

        # Help text
        help_panel = Panel(
            field_help,
            title="Description",
            border_style="dim",
            padding=(0, 1),
        )

        # Validation info
        validation_text = self._get_validation_info(field, current_value)
        if validation_text:
            validation_panel = Panel(
                validation_text,
                title="Validation",
                border_style="green" if "✓" in validation_text else "yellow",
                padding=(0, 1),
            )
        else:
            validation_panel = None

        # Combine all elements as a single renderable group (avoid mounting unattached widgets)
        elements = [table, help_panel]
        if validation_panel:
            elements.append(validation_panel)
        content_group = Group(*elements)

        # Update the display
        context_content = self.query_one("#context-content", Static)
        context_content.update(Panel(content_group, title=f"📋 {field_name}", border_style="blue"))

    def _get_validation_info(self, field: Dict, value: Any) -> str:
        """Get validation information for a field."""
        field_name = field["arg"].lstrip("-").replace("-", "_")
        field_type = field.get("type", str)

        validation_messages = []

        # Type validation
        if value is not None and value != "":
            if field_type == int:
                try:
                    int(value)
                    validation_messages.append("[OK] Valid integer")
                except (ValueError, TypeError):
                    validation_messages.append("[!] Must be an integer")
            elif field_type == float:
                try:
                    float(value)
                    validation_messages.append("[OK] Valid number")
                except (ValueError, TypeError):
                    validation_messages.append("[!] Must be a number")

        # JSON validation for JSON fields
        if field_name in ["sweep_params", "token_weights", "custom_loss_weights",
                         "custom_metrics", "rl_reward_weights", "rl_env_config"]:
            if value and isinstance(value, str):
                import json
                try:
                    json.loads(value)
                    validation_messages.append("[OK] Valid JSON")
                except json.JSONDecodeError as e:
                    validation_messages.append(f"[!] Invalid JSON: {str(e)}")

        # Special validations
        if field_name == "lr" and value:
            try:
                lr = float(value)
                if lr <= 0:
                    validation_messages.append("[!] Learning rate must be positive")
                elif lr > 1:
                    validation_messages.append("[!] Learning rate unusually high (>1)")
            except (ValueError, TypeError):
                pass

        if field_name == "batch_size" and value:
            try:
                bs = int(value)
                if bs <= 0:
                    validation_messages.append("[!] Batch size must be positive")
            except (ValueError, TypeError):
                pass

        if field_name == "epochs" and value:
            try:
                epochs = int(value)
                if epochs <= 0:
                    validation_messages.append("[!] Epochs must be positive")
            except (ValueError, TypeError):
                pass

        return "\n".join(validation_messages) if validation_messages else ""

    def clear(self) -> None:
        """Clear the context panel."""
        self.current_field = None
        self.current_value = None
        context_content = self.query_one("#context-content", Static)
        context_content.update(
            Panel(
                "Select a parameter to see details",
                title="📋 Context",
                border_style="dim",
            )
        )