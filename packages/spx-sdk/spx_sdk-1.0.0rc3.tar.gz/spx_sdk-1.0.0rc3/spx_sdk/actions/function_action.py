from typing import Any, Dict
from spx_sdk.registry import register_class
from spx_sdk.actions.action import Action
from spx_sdk.components import SpxComponentState
from spx_sdk.validation.decorators import definition_schema


@register_class(name="function")
@definition_schema({
    "type": "object",
    "required": ["function", "call"],
    "properties": {
        "function": {
            "oneOf": [
                {"type": "string", "pattern": r"^(\$in|\$out|\$attr|\$ext)\([^)]+\)$"},
                {"type": "array", "minItems": 1, "items": {"type": "string", "pattern": r"^(\$in|\$out|\$attr|\$ext)\([^)]+\)$"}}
            ],
            "description": "Target attribute(s): single ref or list of refs to attributes using $in/$out/$attr/$ext."
        },
        "call": {
            "type": "string",
            "minLength": 1,
            "description": "Expression string, may reference inputs via $in(...) and other helpers."
        },
        "params": {
            "type": "object",
            "description": "Optional mapping of parameter names to literal values or attribute references.",
            "additionalProperties": True
        },
    }
}, validation_scope="parent")
class FunctionAction(Action):
    """
    FunctionAction class for executing a function.
    Inherits from Action to manage action components.
    """

    def _populate(self, definition: dict) -> None:
        self.call = None
        merged_definition = dict(definition or {})
        params_block = merged_definition.pop("params", None)
        if params_block is not None:
            if not isinstance(params_block, dict):
                raise ValueError("FunctionAction 'params' section must be a mapping of parameter names to values.")
            for key, value in params_block.items():
                if key in ("function", "output", "call", "params"):
                    continue
                merged_definition.setdefault(key, value)
        super()._populate(merged_definition)

    def run(self, *args, **kwargs) -> Any:
        """
        Evaluate the call expression, resolving attribute references,
        and write the result to all output attributes.
        """
        base_result = super().run()
        if base_result is True:
            return True  # Action disabled
        if self.call is None:
            return False  # No call defined, nothing to run
        evaluated = self._evaluate_call(self.call)
        self.call = evaluated
        result = self.write_outputs(evaluated)
        self.state = SpxComponentState.STOPPED
        return result

    def _build_eval_context(self) -> Dict[str, Any]:
        """
        Collect resolved parameter values exposed on the action for expression evaluation.
        """
        context: Dict[str, Any] = {"self": self}
        for key in self.params.keys():
            if key in ("call", "params"):
                continue
            if hasattr(self, key):
                context[key] = getattr(self, key)
        return context

    def _evaluate_call(self, call_value: Any) -> Any:
        """
        Evaluate the call expression with access to resolved parameters.
        Falls back to the original value if evaluation fails.
        """
        if not isinstance(call_value, str):
            return call_value
        try:
            return eval(call_value, globals(), self._build_eval_context())
        except Exception:
            return call_value
