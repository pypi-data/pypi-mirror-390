from functools import cached_property

from dyngle.model.expression import expression
from dyngle.model.live_data import LiveData
from dyngle.model.operation import Operation


class Dyngleverse:
    """Represents the entire immutable set of definitions for operations,
    expresssions, and values. Operates as a sort of index/database."""

    def __init__(self):
        self.operations = {}
        self.all_globals = {}

    def load_config(self, config: dict):
        """
        Load additional configuration, which will always take higher precedence
        than previously loaded configuration.
        """
        ops_defs = config.get('operations') or {}
        for key, op_def in ops_defs.items():
            operation = Operation(self, op_def, key)
            self.operations[key] = operation
        self.all_globals |= Dyngleverse.parse_constants(config)

    @staticmethod
    def parse_constants(definition: dict):
        """
        At either the global (dyngleverse) or local (within an operation)
        level, we might find values and expressions.
        """

        expr_texts = definition.get('expressions') or {}
        expressions = {k: expression(t) for k, t in expr_texts.items()}
        values = definition.get('values') or {}
        return expressions | values
