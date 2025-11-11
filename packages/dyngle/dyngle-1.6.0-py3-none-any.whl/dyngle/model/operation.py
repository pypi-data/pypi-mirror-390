from dataclasses import dataclass
from functools import cached_property
import re
import shlex
import subprocess

from dyngle.error import DyngleError
from dyngle.model.context import Context
from dyngle.model.template import Template


class Operation:
    """A named operation defined in configuration. Can be called from a Dyngle
    command (i.e. `dyngle run`) or as a sub-operation."""

    local_constants = {}

    def __init__(self, dyngleverse, definition: dict | list, key: str):
        """
        definition: Either a dict containing steps and local
        expressions/values, or a list containing only steps
        """
        self.dyngleverse = dyngleverse
        if isinstance(definition, list):
            steps_def = definition
            local_constants = Context()
        elif isinstance(definition, dict):
            steps_def = definition.get('steps') or []
            local_constants = dyngleverse.parse_constants(definition)
        self.constants = dyngleverse.global_constants | local_constants
        self.sequence = Sequence(dyngleverse, self, steps_def)

    def run(self, data: Context, args: list):
        self.sequence.run(data, args)


class Sequence:
    """We allow for the possibility that a sequence of steps might run at other
    levels than the operation itself, for example in a conditional block."""

    def __init__(self, dyngleverse, operation: Operation, steps_def: list):
        self.steps = [Step.parse_def(
            dyngleverse, operation.constants, d) for d in steps_def]

    def run(self, data: Context, args: list):
        for step in self.steps:
            step.run(data, args)


class Step:

    @staticmethod
    def parse_def(dyngleverse, constants: Context, definition: dict | str):
        for step_type in [CommandStep, SubOperationStep]:
            if step_type.fits(definition):
                return step_type(dyngleverse, constants, definition)
        raise DyngleError(f"Unknown step definition\n{definition}")


# Ideally these would be subclasses in a ClassFamily (or use an ABC)

class CommandStep:
    """Executes a system command with optional input/output operators.

    Supports the following operators:
    - `->` (input): Passes a value from the namespace to stdin
    - `=>` (output): Captures stdout to live data

    The step creates a namespace by merging:
    1. Operation's constants (declared values/expressions) - lowest precedence
    2. Shared live data (mutable across operations) - middle precedence
    3. Current args - highest precedence

    Template resolution happens in this namespace, but output assignments
    go directly to the shared live data to persist across operations.
    """

    PATTERN = re.compile(
        r'^\s*(?:([\w.-]+)\s+->\s+)?(.+?)(?:\s+=>\s+([\w.-]+))?\s*$')

    @classmethod
    def fits(cls, definition: dict | str):
        return isinstance(definition, str)

    def __init__(self, dyngleverse, constants: Context, definition: str):
        self.constants = constants
        self.markup = definition
        if match := self.PATTERN.match(definition):
            self.input, command_text, self.output = match.groups()
            command_template = shlex.split(command_text.strip())
            self.command_template = command_template
        else:
            raise DyngleError(f"Invalid step markup {{markup}}")

    def run(self, data: Context, args: list):
        namespace = self.constants | data | {'args': args}
        command = [Template(word).render(namespace).strip()
                   for word in self.command_template]
        pipes = {}
        if self.input:
            pipes["input"] = namespace.resolve(self.input)
        if self.output:
            pipes['stdout'] = subprocess.PIPE
        result = subprocess.run(command, text=True, **pipes)
        if result.returncode != 0:
            raise DyngleError(
                f'Step failed with code {result.returncode}: {self.markup}')
        if self.output:
            data[self.output] = result.stdout.rstrip()


class SubOperationStep:
    """Calls another operation as a sub-step.

    Sub-operations maintain proper scoping:
    - Each operation has its own constants (declared values/expressions)
    - Constants are locally scoped and do not leak between operations
    - Live data (set via =>) is shared and persists across operations
    - Args are locally scoped to each operation

    The sub-operation receives the same shared live data object, allowing
    it to read data set by the parent and persist changes back to the parent.
    """

    @classmethod
    def fits(cls, definition: dict | str):
        return isinstance(definition, dict) and 'sub' in definition

    def __init__(self, dyngleverse, declarations: Context, definition: dict):
        self.dyngleverse = dyngleverse
        self.declarations = declarations
        self.operation_key = definition['sub']
        self.args_template = definition.get('args') or ''

    def run(self, data: Context, args: list):
        namespace = self.declarations | data | {'args': args}
        operation = self.dyngleverse.operations.get(self.operation_key)
        if not operation:
            raise DyngleError(f"Unknown operation {self.operation_key}")
        sub_args = [Template(word).render(namespace).strip()
                    for word in self.args_template]
        operation.run(data, sub_args)
