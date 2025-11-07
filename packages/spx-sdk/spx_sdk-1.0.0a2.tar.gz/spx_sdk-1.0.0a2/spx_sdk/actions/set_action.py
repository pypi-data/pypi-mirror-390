from typing import Any, Dict
from spx_sdk.registry import register_class
from spx_sdk.actions.action import Action
from spx_sdk.diagnostics import guard, trace
from spx_sdk.validation.decorators import definition_schema


@register_class(name="set")
@register_class(name="Set")
@definition_schema({
    "type": "object",
    "required": ["set", "value"],
    "properties": {
        "set": {
            "oneOf": [
                {"type": "string", "pattern": r"^(\$in|\$out|\$attr|\$ext)\([^)]+\)$"},
                {"type": "array", "minItems": 1, "items": {"type": "string", "pattern": r"^(\$in|\$out|\$attr|\$ext)\([^)]+\)$"}}
            ],
            "description": "Target attribute(s): single ref or list of refs to attributes using $in/$out/$attr/$ext."
        },
        "value": {
            "anyOf": [
                {"type": "null"},
                {"type": "boolean"},
                {"type": "number"},
                {"type": "string"},
                {"type": "array"},
                {"type": "object"}
            ]
        }
    },
    "additionalProperties": False,
}, validation_scope="parent")
class SetAction(Action):
    """
    SetAction class for assigning a literal value to one or more attributes.
    Inherits from Action to manage outputs and inputs.
    """

    @guard("config.populate", bubble=True, http_status=422)
    def _populate(self, definition: Dict[str, Any]) -> None:
        """
        Populate the SetAction with the given definition.
        Extracts 'value' from definition.params and
        then delegates to base class.
        """
        # Extract literal value: can be top‑level or inside "params"
        if "value" in definition:
            self.value = definition.pop("value")
            params = definition.get("params", {})
        else:
            params = definition.get("params", {})
            self.value = params.pop("value", None)
        # Now let base Action handle function, outputs, and remaining params
        super()._populate(definition)

    @guard(prefix="lifecycle.", http_status=500)
    def run(self, *args, **kwargs) -> Any:
        """
        Execute the set operation: assign the literal value to all outputs.
        Returns the value that was set.
        """
        # Assign the stored literal value to each output wrapper
        for name, wrapper in self.outputs.items():
            # Add precise breadcrumb per output; bubble on failure (runtime -> 500)
            with trace(self, action="actions.set.output", bubble=True, http_status=500, extra={"output": name}):
                wrapper.set(self.value)
        return True
