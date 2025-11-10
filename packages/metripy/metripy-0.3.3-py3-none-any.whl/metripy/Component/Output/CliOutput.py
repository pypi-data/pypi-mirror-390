import re
import sys
from typing import Self


class CliOutput:
    def __init__(self):
        self.quiet_mode = False

    def set_quiet_mode(self, quiet_mode: bool):
        self.quiet_mode = quiet_mode

    def writeln(self, message: str) -> Self:
        self.write(str(message), end="\n")

        return self

    def write(self, message: str, end="") -> Self:
        if matches := re.search(r"<([a-z]+)>(.*?)</([a-z]+)>", message):
            type = matches.group(1)
            message = matches.group(2)
            color = {
                "error": "\033[31m",
                "warning": "\033[33m",
                "success": "\033[32m",
                "info": "\033[34m",
                "debug": "\033[95m",
            }
            message = color[type] + message + "\033[0m"

        if not self.quiet_mode:
            print(message, end=end)

        return self

    def err(self, message: str) -> Self:
        sys.stderr.write(message)

        return self

    def clearln(self) -> Self:
        if self.has_ansi():
            self.write("\x0d")
            self.write("\x1b[2K")

        return self

    def has_ansi(self) -> bool:
        return sys.stdout.isatty()
