"""Parameter form widget for editing training parameters."""
import json
from typing import Dict, List, Any, Optional
from textual.app import ComposeResult
from textual.widgets import Static, Input, Checkbox, Select, TextArea, Label, Button
from textual.containers import Vertical, Horizontal, Grid
from textual.message import Message


class ParameterForm(Static):
    """Widget for displaying and editing parameters."""

    class ParameterChanged(Message):
        """Message emitted when a parameter value changes."""

        def __init__(self, name: str, value: Any):
            self.name = name
            self.value = value
            super().__init__()

    def __init__(self, **kwargs):
        """Initialize the parameter form."""
        super().__init__(**kwargs)
        self.fields: List[Dict] = []
        self.values: Dict[str, Any] = {}
        self.widgets: Dict[str, Any] = {}

    def compose(self) -> ComposeResult:
        """Compose the parameter form."""
        with Vertical(id="param-form-container"):
            yield Label("No parameters to display", id="no-params-label")

    def set_fields(self, fields: List[Dict], values: Dict[str, Any]) -> None:
        """Set the fields to display in the form."""
        self.fields = fields
        self.values = values
        self._rebuild_form()

    def _rebuild_form(self) -> None:
        """Rebuild the form with current fields."""
        container = self.query_one("#param-form-container", Vertical)
        container.remove_children()

        if not self.fields:
            container.mount(Label("No parameters to display", id="no-params-label"))
            return

        self.widgets.clear()

        for field in self.fields:
            # Extract field info
            field_name = field["arg"].lstrip("-").replace("-", "_")
            field_type = field.get("type", str)
            field_help = field.get("help", "")
            field_default = field.get("default")
            current_value = self.values.get(field_name, field_default)

            # Create a container for the field
            field_container = Vertical(classes="field-container")

            # Add label
            label_text = field_name.replace("_", " ").title()
            if current_value != field_default and field_default is not None:
                label_text += " *"  # Modified indicator

            field_label = Label(label_text, classes="field-label")
            # Mount the field container first, then add children to avoid MountError
            container.mount(field_container)
            field_container.mount(field_label)

            # Add a compact help line under the label (acts as a tooltip substitute)
            if field_help:
                help_preview = field_help.strip()
                field_container.mount(Label(help_preview, classes="field-help"))

            # Create appropriate widget based on type
            widget = self._create_widget(field, field_type, current_value)
            if widget:
                field_container.mount(widget)
                self.widgets[field_name] = widget

    def _create_widget(self, field: Dict, field_type: type, value: Any) -> Optional[Static]:
        """Create the appropriate widget for a field type."""
        field_name = field["arg"].lstrip("-").replace("-", "_")

        # Boolean -> Checkbox
        if field_type == bool:
            checkbox = Checkbox(
                label="",
                value=bool(value) if value is not None else False,
                id=f"field-{field_name}",
                name=field_name,
            )
            return checkbox

        # Enum/Choices -> Select
        if field_name in ["trainer", "log", "optimizer", "scheduler", "eval_strategy",
                          "save_strategy", "mixed_precision", "quantization", "padding",
                          "chat_template", "chat_format", "sweep_backend", "sweep_direction"]:
            # Define options based on field
            options = self._get_select_options(field_name)
            # Avoid passing None as value. If None, omit the value kwarg so Select defaults to BLANK.
            if value is None:
                select = Select(
                    options=options,
                    allow_blank=True,
                    id=f"field-{field_name}",
                    name=field_name,
                )
            else:
                select = Select(
                    options=options,
                    value=str(value),
                    allow_blank=True,
                    id=f"field-{field_name}",
                    name=field_name,
                )
            return select

        # JSON fields -> TextArea
        if field_name in ["sweep_params", "token_weights", "custom_loss_weights",
                          "custom_metrics", "rl_reward_weights", "rl_env_config"]:
            text_area = TextArea(
                text=json.dumps(value, indent=2) if value else "",
                id=f"field-{field_name}",
                name=field_name,
                tab_behavior="indent",
            )
            text_area.styles.height = 5
            return text_area

        # Multi-line text fields
        if field_name in ["inference_prompts", "eval_metrics", "target_modules"]:
            text_area = TextArea(
                text=str(value) if value else "",
                id=f"field-{field_name}",
                name=field_name,
            )
            text_area.styles.height = 3
            return text_area

        # Number fields
        if field_type in [int, float]:
            input_widget = Input(
                value=str(value) if value is not None else "",
                placeholder=f"Enter {field_type.__name__}",
                id=f"field-{field_name}",
                name=field_name,
                type="number" if field_type == int else "text",
            )
            return input_widget

        # Default to text input
        input_widget = Input(
            value=str(value) if value else "",
            placeholder="Enter value",
            id=f"field-{field_name}",
            name=field_name,
        )
        return input_widget

    def _get_select_options(self, field_name: str) -> List[tuple]:
        """Get select options for specific fields."""
        options_map = {
            "trainer": [
                ("default", "default"),
                ("sft", "sft"),
                ("dpo", "dpo"),
                ("orpo", "orpo"),
                ("ppo", "ppo"),
                ("reward", "reward"),
            ],
            "log": [
                ("none", "none"),
                ("wandb", "wandb"),
                ("tensorboard", "tensorboard"),
            ],
            "optimizer": [
                ("adamw_torch", "adamw_torch"),
                ("adamw_hf", "adamw_hf"),
                ("sgd", "sgd"),
                ("adafactor", "adafactor"),
                ("adagrad", "adagrad"),
            ],
            "scheduler": [
                ("linear", "linear"),
                ("cosine", "cosine"),
                ("constant", "constant"),
                ("polynomial", "polynomial"),
            ],
            "eval_strategy": [
                ("no", "no"),
                ("steps", "steps"),
                ("epoch", "epoch"),
            ],
            "save_strategy": [
                ("no", "no"),
                ("steps", "steps"),
                ("epoch", "epoch"),
            ],
            "mixed_precision": [
                ("fp16", "fp16"),
                ("bf16", "bf16"),
            ],
            "quantization": [
                ("none", "none"),
                ("int4", "int4"),
                ("int8", "int8"),
            ],
            "padding": [
                ("right", "right"),
                ("left", "left"),
            ],
            "chat_template": [
                ("zephyr", "zephyr"),
                ("chatml", "chatml"),
                ("tokenizer", "tokenizer"),
            ],
            "sweep_backend": [
                ("optuna", "optuna"),
                ("ray", "ray"),
                ("grid", "grid"),
                ("random", "random"),
            ],
            "sweep_direction": [
                ("minimize", "minimize"),
                ("maximize", "maximize"),
            ],
        }
        return options_map.get(field_name, [])

    def on_input_changed(self, event: Input.Changed) -> None:
        """Handle input value changes."""
        if hasattr(event.input, "name"):
            name = event.input.name
            value = event.value

            # Type conversion based on field
            field = self._get_field_by_name(name)
            if field:
                field_type = field.get("type", str)
                try:
                    if field_type == int and value:
                        value = int(value)
                    elif field_type == float and value:
                        value = float(value)
                except ValueError:
                    pass  # Keep as string if conversion fails

            self.post_message(self.ParameterChanged(name, value))

    def on_checkbox_changed(self, event: Checkbox.Changed) -> None:
        """Handle checkbox value changes."""
        if hasattr(event.checkbox, "name"):
            name = event.checkbox.name
            value = event.value
            self.post_message(self.ParameterChanged(name, value))

    def on_select_changed(self, event: Select.Changed) -> None:
        """Handle select value changes."""
        if hasattr(event.select, "name"):
            name = event.select.name
            value = event.value
            self.post_message(self.ParameterChanged(name, value))

    def on_text_area_changed(self, event: TextArea.Changed) -> None:
        """Handle text area value changes."""
        if hasattr(event.text_area, "name"):
            name = event.text_area.name
            value = event.text_area.text

            # Try to parse JSON for JSON fields
            if name in ["sweep_params", "token_weights", "custom_loss_weights",
                       "custom_metrics", "rl_reward_weights", "rl_env_config"]:
                if value:
                    try:
                        value = json.loads(value)
                    except json.JSONDecodeError:
                        pass  # Keep as string if not valid JSON

            self.post_message(self.ParameterChanged(name, value))

    def _get_field_by_name(self, name: str) -> Optional[Dict]:
        """Get field info by name."""
        for field in self.fields:
            field_name = field["arg"].lstrip("-").replace("-", "_")
            if field_name == name:
                return field
        return None