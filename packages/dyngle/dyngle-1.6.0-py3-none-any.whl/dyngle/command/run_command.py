from functools import cached_property
import shlex
import subprocess
from wizlib.parser import WizParser
from yaml import safe_load

from dyngle.command import DyngleCommand
from dyngle.model.context import Context
from dyngle.model.expression import expression
from dyngle.model.template import Template
from dyngle.error import DyngleError


class RunCommand(DyngleCommand):
    """Run a workflow defined in the configuration"""

    name = 'run'

    @classmethod
    def add_args(cls, parser: WizParser):
        super().add_args(parser)
        parser.add_argument(
            'operation', help='Operation name to run', nargs='?')
        parser.add_argument(
            'args', nargs='*', help='Optional operation arguments')

    def handle_vals(self):
        super().handle_vals()
        keys = self.app.dyngleverse.operations.keys()
        if not self.provided('operation'):
            self.operation = self.app.ui.get_text('Operation: ', sorted(keys))
            if not self.operation:
                raise DyngleError(f"Operation required.")
        if self.operation not in keys:
            raise DyngleError(f"Invalid operation {self.operation}.")

    @DyngleCommand.wrap
    def execute(self):
        data_string = self.app.stream.text
        data = safe_load(data_string) or {}
        operation = self.app.dyngleverse.operations[self.operation]
        operation.run(Context(data), self.args)
        return f'Operation "{self.operation}" completed successfully'
