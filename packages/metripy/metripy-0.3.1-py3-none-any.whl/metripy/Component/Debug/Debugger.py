from typing import Self

from metripy.Component.Output.CliOutput import CliOutput


class Debugger:
    def __init__(self, output: CliOutput):
        self.enabled = False
        self.output = output

    def enable(self) -> Self:
        self.enabled = True

        return self

    def debug(self, message: str):
        if not self.enabled:
            return

        self.output.writeln(f"<debug>{message}</debug>")
