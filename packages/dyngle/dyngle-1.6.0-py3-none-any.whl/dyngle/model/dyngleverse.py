from functools import cached_property

from dyngle.model.expression import expression
from dyngle.model.context import Context
from dyngle.model.operation import Operation


class Dyngleverse:
    """Represents the entire set of definitions for operations, expressions,
    and values.

    The Dyngleverse acts as a registry/index for all operations and global
    constants (values and expressions). It maintains:

    - operations: A dict of Operation objects indexed by name
    - global_constants: A Context containing global values and expressions

    When operations are created, they receive a reference to global_constants
    and merge them with their own local constants, establishing the proper
    scoping hierarchy:

    1. Global constants (lowest precedence)
    2. Local operation constants (higher precedence)
    3. Live data from execution (highest precedence, shared across operations)
    """

    def __init__(self):
        self.operations = {}
        self.global_constants = Context()

    def load_config(self, config: dict):
        """
        Load additional configuration, which will always take higher precedence
        than previously loaded configuration.
        """
        self.global_constants |= Dyngleverse.parse_constants(config)
        ops_defs = config.get('operations') or {}
        for key, op_def in ops_defs.items():
            operation = Operation(self, op_def, key)
            self.operations[key] = operation

    @staticmethod
    def parse_constants(definition: dict) -> Context:
        """
        At either the global (dyngleverse) or local (within an operation)
        level, we might find values and expressions.
        """

        expr_texts = definition.get('expressions') or {}
        expressions = {k: expression(t) for k, t in expr_texts.items()}
        values = definition.get('values') or {}
        return Context(expressions) | values
