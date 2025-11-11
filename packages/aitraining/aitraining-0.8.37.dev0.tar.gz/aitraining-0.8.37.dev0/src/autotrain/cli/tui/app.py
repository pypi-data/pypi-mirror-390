"""Main TUI Application for AITraining."""
import asyncio
import json
import os
import sys
from pathlib import Path
from typing import Dict, List, Optional, Any
import subprocess

from textual import on, work
from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.containers import Container, Horizontal, Vertical, VerticalScroll
from textual.screen import ModalScreen
from textual.widgets import (
    Header,
    Footer,
    Button,
    Label,
    Static,
    Input,
    TextArea,
    ListView,
    ListItem,
    Checkbox,
    Select,
    TabbedContent,
    TabPane,
    LoadingIndicator,
    RichLog,
)
from textual.reactive import reactive
from rich.console import RenderableType
from rich.panel import Panel
from rich.text import Text
from rich.table import Table
from rich.syntax import Syntax

from autotrain import logger
from autotrain.cli.utils import get_field_info
from autotrain.trainers.clm.params import LLMTrainingParams
from autotrain.cli.run_llm import FIELD_GROUPS, FIELD_SCOPES

# Import our custom widgets and components
from .widgets.parameter_form import ParameterForm
from .widgets.trainer_selector import TrainerSelector
from .widgets.group_list import GroupList
from .widgets.context_panel import ContextPanel
from .state.app_state import AppState
from .runner import CommandRunner


class AITrainingTUI(App):
    """AITraining Terminal User Interface Application."""

    CSS_PATH = "styles.tcss"

    BINDINGS = [
        Binding("ctrl+s", "save_config", "Save Config", priority=True),
        Binding("ctrl+l", "load_config", "Load Config", priority=True),
        Binding("ctrl+r", "run_training", "Run", priority=True, show=True),
        Binding("ctrl+c", "quit", "Quit", priority=True),
        Binding("q", "quit", "Quit", show=False),
        Binding("f1", "toggle_help", "Help", priority=True),
        Binding("f5", "refresh", "Refresh", show=False),
        Binding("ctrl+p", "show_command", "Preview Command"),
        Binding("ctrl+d", "toggle_dry_run", "Toggle Dry Run"),
        Binding("ctrl+t", "toggle_theme", "Toggle Theme"),
        Binding("/", "search", "Search Parameters"),
        Binding("escape", "clear_search", "Clear Search", show=False),
    ]

    TITLE = "AITraining TUI"

    def __init__(
        self,
        theme: str = "dark",
        dry_run: bool = False,
        config_file: Optional[str] = None,
    ):
        """Initialize the TUI application."""
        super().__init__()
        self.theme_name = theme
        self.dry_run = dry_run
        self.initial_config = config_file
        self.state = AppState()
        self.runner = CommandRunner(dry_run=dry_run)

    def compose(self) -> ComposeResult:
        """Compose the TUI layout."""
        # Header with branding
        yield Header(show_clock=True)

        # Main container with three-panel layout
        with Container(id="main-container"):
            # Left panel: Trainer selector and groups
            with Vertical(id="left-panel", classes="panel"):
                yield Label("═══ AITraining ═══", id="branding")
                yield TrainerSelector(id="trainer-selector")
                yield GroupList(id="group-list")

            # Center panel: Parameter form
            with VerticalScroll(id="center-panel", classes="panel"):
                yield Label("Parameters", id="param-header")
                yield ParameterForm(id="param-form")

            # Right panel: Context and help
            with Vertical(id="right-panel", classes="panel"):
                with TabbedContent(id="right-tabs"):
                    with TabPane("Context", id="context-tab"):
                        yield ContextPanel(id="context-panel")
                    with TabPane("Command", id="command-tab"):
                        yield TextArea(
                            id="command-preview",
                            read_only=True,
                            language="bash",
                            theme="monokai",
                        )
                    with TabPane("Logs", id="logs-tab"):
                        yield RichLog(id="log-viewer", highlight=True, markup=True)

        # Footer with status and keybindings
        yield Footer()

    async def on_mount(self) -> None:
        """Initialize the app when mounted."""
        self.title = "AITraining TUI - Interactive Parameter Configuration"
        self.sub_title = f"Theme: {self.theme_name} | Dry Run: {'ON' if self.dry_run else 'OFF'}"

        # Theme selection is currently cosmetic; Textual themes must be registered first.
        # We avoid setting App.theme directly to prevent InvalidThemeError in environments
        # where custom themes aren't registered. Styling is handled via CSS.

        # Load initial state
        await self._initialize_state()

        # Load config if provided
        if self.initial_config:
            await self._load_config_file(self.initial_config)

        # Initialize UI with state
        await self._refresh_ui()

    async def _initialize_state(self) -> None:
        """Initialize the application state."""
        # Get field info from LLMTrainingParams
        field_info = get_field_info(LLMTrainingParams, FIELD_GROUPS, FIELD_SCOPES)

        # Initialize state with field info
        self.state.initialize_fields(field_info)

        # Set default trainer
        self.state.set_trainer("default")

        # Group fields by their groups
        groups = {}
        for field in field_info:
            group = field.get("group", "Other")
            if group not in groups:
                groups[group] = []
            groups[group].append(field)

        self.state.groups = groups
        self.state.current_group = "Basic"

    async def _refresh_ui(self) -> None:
        """Refresh the UI based on current state."""
        # Update trainer selector
        trainer_selector = self.query_one("#trainer-selector", TrainerSelector)
        trainer_selector.set_trainer(self.state.current_trainer)

        # Update group list
        group_list = self.query_one("#group-list", GroupList)
        visible_groups = self._get_visible_groups()
        group_list.set_groups(visible_groups)
        group_list.set_current_group(self.state.current_group)

        # Update parameter form
        param_form = self.query_one("#param-form", ParameterForm)
        visible_fields = self._get_visible_fields_for_group(self.state.current_group)
        param_form.set_fields(visible_fields, self.state.parameters)

        # Update command preview
        await self._update_command_preview()

    def _get_visible_groups(self) -> List[str]:
        """Get list of groups visible for current trainer."""
        visible_groups = set()

        for field in self.state.fields:
            # Check if field is visible for current trainer
            scopes = field.get("scope", ["all"])
            if "all" in scopes or self.state.current_trainer in scopes:
                group = field.get("group", "Other")
                visible_groups.add(group)

        # Order groups according to FIELD_GROUPS ordering
        group_order = [
            "Basic", "Data Processing", "Training Configuration",
            "Training Hyperparameters", "PEFT/LoRA", "DPO/ORPO",
            "Hub Integration", "Knowledge Distillation", "Hyperparameter Sweep",
            "Enhanced Evaluation", "Reinforcement Learning (PPO)",
            "Advanced Features", "Inference"
        ]

        ordered = [g for g in group_order if g in visible_groups]
        remaining = sorted(visible_groups - set(ordered))
        return ordered + remaining

    def _get_visible_fields_for_group(self, group: str) -> List[Dict]:
        """Get fields visible for current trainer and group."""
        visible = []

        for field in self.state.fields:
            # Check group
            if field.get("group", "Other") != group:
                continue

            # Check scope
            scopes = field.get("scope", ["all"])
            if "all" in scopes or self.state.current_trainer in scopes:
                visible.append(field)

        return visible

    async def _update_command_preview(self) -> None:
        """Update the command preview based on current parameters."""
        # Build command
        command = self._build_command()

        # Update preview
        command_preview = self.query_one("#command-preview", TextArea)
        command_preview.text = " ".join(command)

    def _build_command(self) -> List[str]:
        """Build the CLI command from current parameters."""
        command = ["aitraining", "llm"]

        # Add trainer if not default
        if self.state.current_trainer != "default":
            command.append(f"--trainer={self.state.current_trainer}")

        # Add all non-None parameters
        for key, value in self.state.parameters.items():
            if value is not None and value != "":
                # Skip defaults to keep command clean
                field_info = self._get_field_by_name(key)
                if field_info:
                    default = field_info.get("default")
                    if value == default:
                        continue

                # Convert key to CLI format
                cli_key = key.replace("_", "-")

                # Handle boolean flags
                if isinstance(value, bool):
                    if value:
                        command.append(f"--{cli_key}")
                else:
                    command.append(f"--{cli_key}={value}")

        # Add --train flag
        command.append("--train")

        return command

    def _get_field_by_name(self, name: str) -> Optional[Dict]:
        """Get field info by field name."""
        for field in self.state.fields:
            field_name = field["arg"].lstrip("-").replace("-", "_")
            if field_name == name:
                return field
        return None

    @work
    async def action_save_config(self) -> None:
        """Save configuration to file."""
        # Show save dialog
        save_dialog = SaveConfigDialog()
        filename = await self.push_screen_wait(save_dialog)

        if filename:
            try:
                config = {
                    "trainer": self.state.current_trainer,
                    "parameters": {
                        k: v for k, v in self.state.parameters.items()
                        if v is not None and v != ""
                    }
                }

                path = Path(filename)
                if path.suffix == ".yaml" or path.suffix == ".yml":
                    import yaml
                    with open(path, "w") as f:
                        yaml.dump(config, f, default_flow_style=False)
                else:
                    with open(path, "w") as f:
                        json.dump(config, f, indent=2)

                log_viewer = self.query_one("#log-viewer", RichLog)
                log_viewer.write(f"[green]✓[/green] Configuration saved to {path}")

            except Exception as e:
                log_viewer = self.query_one("#log-viewer", RichLog)
                log_viewer.write(f"[red]✗[/red] Failed to save config: {e}")

    @work
    async def action_load_config(self) -> None:
        """Load configuration from file."""
        # Show load dialog
        load_dialog = LoadConfigDialog()
        filename = await self.push_screen_wait(load_dialog)

        if filename:
            await self._load_config_file(filename)

    async def _load_config_file(self, filename: str) -> None:
        """Load configuration from a file."""
        try:
            path = Path(filename)
            if not path.exists():
                raise FileNotFoundError(f"Config file not found: {path}")

            if path.suffix == ".yaml" or path.suffix == ".yml":
                import yaml
                with open(path) as f:
                    config = yaml.safe_load(f)
            else:
                with open(path) as f:
                    config = json.load(f)

            # Apply config
            if "trainer" in config:
                self.state.set_trainer(config["trainer"])

            if "parameters" in config:
                for key, value in config["parameters"].items():
                    self.state.set_parameter(key, value)

            # Refresh UI
            await self._refresh_ui()

            log_viewer = self.query_one("#log-viewer", RichLog)
            log_viewer.write(f"[green]✓[/green] Configuration loaded from {path}")

        except Exception as e:
            log_viewer = self.query_one("#log-viewer", RichLog)
            log_viewer.write(f"[red]✗[/red] Failed to load config: {e}")

    async def action_run_training(self) -> None:
        """Run training with current configuration."""
        # Build command
        command = self._build_command()

        # Switch to logs tab
        tabs = self.query_one("#right-tabs", TabbedContent)
        tabs.active = "logs-tab"

        # Clear logs
        log_viewer = self.query_one("#log-viewer", RichLog)
        log_viewer.clear()

        # Show command
        log_viewer.write(Panel(
            " ".join(command),
            title="Command",
            border_style="blue"
        ))

        if self.dry_run:
            log_viewer.write("[yellow]DRY RUN MODE[/yellow] - Command will not be executed")
            log_viewer.write("[dim]This is a preview of what would be executed[/dim]")
            return

        # Run command
        log_viewer.write("\n[cyan]Starting training...[/cyan]\n")

        try:
            # Run in background
            await self.runner.run_command(command, log_viewer)
        except Exception as e:
            log_viewer.write(f"\n[red]Error:[/red] {e}")

    async def action_toggle_help(self) -> None:
        """Toggle help overlay."""
        help_screen = HelpScreen()
        await self.push_screen(help_screen)

    async def action_toggle_dry_run(self) -> None:
        """Toggle dry run mode."""
        self.dry_run = not self.dry_run
        self.runner.dry_run = self.dry_run
        self.sub_title = f"Theme: {self.theme_name} | Dry Run: {'ON' if self.dry_run else 'OFF'}"

        log_viewer = self.query_one("#log-viewer", RichLog)
        log_viewer.write(f"Dry run mode: {'[green]ON[/green]' if self.dry_run else '[red]OFF[/red]'}")

    async def action_toggle_theme(self) -> None:
        """Toggle between light and dark themes."""
        self.theme_name = "light" if self.theme_name == "dark" else "dark"
        self.sub_title = f"Theme: {self.theme_name} | Dry Run: {'ON' if self.dry_run else 'OFF'}"

    async def action_show_command(self) -> None:
        """Show the command preview tab."""
        tabs = self.query_one("#right-tabs", TabbedContent)
        tabs.active = "command-tab"

    @work
    async def action_search(self) -> None:
        """Open parameter search."""
        search_dialog = SearchDialog(self.state.fields)
        result = await self.push_screen_wait(search_dialog)

        if result:
            # Find the field's group and switch to it
            field = result
            group = field.get("group", "Other")

            # Switch to group
            self.state.current_group = group
            await self._refresh_ui()

            # Highlight the field (future enhancement)
            log_viewer = self.query_one("#log-viewer", RichLog)
            log_viewer.write(f"Jumped to: {field['arg']} in {group}")

    @on(TrainerSelector.TrainerChanged)
    async def handle_trainer_change(self, event: TrainerSelector.TrainerChanged) -> None:
        """Handle trainer selection change."""
        self.state.set_trainer(event.trainer)

        # Choose a sensible default group for this trainer
        preferred = self._default_group_for_trainer(event.trainer)
        visible_groups = self._get_visible_groups()
        if preferred in visible_groups:
            self.state.current_group = preferred
        elif self.state.current_group not in visible_groups and visible_groups:
            # Fallback to first visible group if current group is no longer available
            self.state.current_group = visible_groups[0]

        await self._refresh_ui()

    def _default_group_for_trainer(self, trainer: str) -> str:
        """Return the default group to focus for a trainer selection."""
        trainer = (trainer or "default").lower()
        if trainer == "ppo":
            return "Reinforcement Learning (PPO)"
        if trainer in ("dpo", "orpo"):
            return "DPO/ORPO"
        return "Basic"

    @on(GroupList.GroupSelected)
    async def handle_group_change(self, event: GroupList.GroupSelected) -> None:
        """Handle group selection change."""
        self.state.current_group = event.group
        await self._refresh_ui()

    @on(ParameterForm.ParameterChanged)
    async def handle_parameter_change(self, event: ParameterForm.ParameterChanged) -> None:
        """Handle parameter value change."""
        self.state.set_parameter(event.name, event.value)
        await self._update_command_preview()

        # Update context panel
        context = self.query_one("#context-panel", ContextPanel)
        field = self._get_field_by_name(event.name)
        if field:
            context.show_field_info(field, event.value)


class SaveConfigDialog(ModalScreen):
    """Modal dialog for saving configuration."""

    def compose(self) -> ComposeResult:
        with Container(id="dialog"):
            yield Label("Save Configuration", id="dialog-title")
            yield Input(
                placeholder="Enter filename (e.g., config.json or config.yaml)",
                id="filename-input"
            )
            with Horizontal(id="dialog-buttons"):
                yield Button("Save", variant="primary", id="save-button")
                yield Button("Cancel", variant="default", id="cancel-button")

    @on(Button.Pressed, "#save-button")
    async def save(self) -> None:
        """Save and close dialog."""
        filename = self.query_one("#filename-input", Input).value
        if filename:
            self.dismiss(filename)

    @on(Button.Pressed, "#cancel-button")
    async def cancel(self) -> None:
        """Cancel and close dialog."""
        self.dismiss(None)


class LoadConfigDialog(ModalScreen):
    """Modal dialog for loading configuration."""

    def compose(self) -> ComposeResult:
        with Container(id="dialog"):
            yield Label("Load Configuration", id="dialog-title")
            yield Input(
                placeholder="Enter filename (e.g., config.json or config.yaml)",
                id="filename-input"
            )
            with Horizontal(id="dialog-buttons"):
                yield Button("Load", variant="primary", id="load-button")
                yield Button("Cancel", variant="default", id="cancel-button")

    @on(Button.Pressed, "#load-button")
    async def load(self) -> None:
        """Load and close dialog."""
        filename = self.query_one("#filename-input", Input).value
        if filename:
            self.dismiss(filename)

    @on(Button.Pressed, "#cancel-button")
    async def cancel(self) -> None:
        """Cancel and close dialog."""
        self.dismiss(None)


class SearchDialog(ModalScreen):
    """Modal dialog for searching parameters."""

    def __init__(self, fields: List[Dict]):
        """Initialize search dialog."""
        super().__init__()
        self.fields = fields
        self.filtered_fields = fields

    def compose(self) -> ComposeResult:
        with Container(id="search-dialog"):
            yield Label("Search Parameters", id="dialog-title")
            yield Input(
                placeholder="Type to search...",
                id="search-input"
            )
            yield ListView(id="search-results")
            with Horizontal(id="dialog-buttons"):
                yield Button("Select", variant="primary", id="select-button")
                yield Button("Cancel", variant="default", id="cancel-button")

    async def on_mount(self) -> None:
        """Focus search input on mount."""
        self.query_one("#search-input", Input).focus()

    @on(Input.Changed, "#search-input")
    async def filter_results(self, event: Input.Changed) -> None:
        """Filter results based on search query."""
        query = event.value.lower()

        if query:
            self.filtered_fields = [
                field for field in self.fields
                if query in field["arg"].lower() or
                   query in field.get("help", "").lower()
            ]
        else:
            self.filtered_fields = self.fields

        # Update list
        results = self.query_one("#search-results", ListView)
        results.clear()

        for field in self.filtered_fields[:20]:  # Limit to 20 results
            name = field["arg"].lstrip("-")
            help_text = field.get("help", "")[:50]
            results.append(ListItem(Label(f"{name}: {help_text}")))

    @on(Button.Pressed, "#select-button")
    async def select(self) -> None:
        """Select the highlighted field."""
        results = self.query_one("#search-results", ListView)
        if results.highlighted_child and self.filtered_fields:
            index = results.highlighted_child
            if index < len(self.filtered_fields):
                self.dismiss(self.filtered_fields[index])

    @on(Button.Pressed, "#cancel-button")
    async def cancel(self) -> None:
        """Cancel and close dialog."""
        self.dismiss(None)


class HelpScreen(ModalScreen):
    """Help screen with keybindings and instructions."""

    def compose(self) -> ComposeResult:
        help_text = """
# AITraining TUI Help

## Keyboard Shortcuts

### Navigation
- **Tab / Shift+Tab**: Navigate between panels
- **↑/↓**: Navigate lists and menus
- **Enter**: Select/Activate
- **Escape**: Clear search / Close dialogs

### Actions
- **Ctrl+R**: Run training
- **Ctrl+S**: Save configuration
- **Ctrl+L**: Load configuration
- **Ctrl+P**: Preview command
- **Ctrl+D**: Toggle dry run mode
- **Ctrl+T**: Toggle theme

### Other
- **/**: Search parameters
- **F1**: Show this help
- **q / Ctrl+C**: Quit

## Tips

1. Select a trainer to filter relevant parameters
2. Navigate groups to see categorized parameters
3. Modified values are highlighted
4. Use dry run mode to test without execution
5. Save configurations for reuse

Press any key to close this help screen.
        """

        with Container(id="help-screen"):
            yield TextArea(help_text, read_only=True, id="help-content")
            yield Button("Close", id="close-help")

    @on(Button.Pressed, "#close-help")
    async def close(self) -> None:
        """Close help screen."""
        self.dismiss()

    def on_key(self, event) -> None:
        """Close on any key press."""
        self.dismiss()