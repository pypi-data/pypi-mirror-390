from metripy.Component.Output.CliOutput import CliOutput


class ProgressBar:
    def __init__(self, output: CliOutput, total: int):
        self.output = output
        self.total = total
        self.current = 0

    def start(self):
        self.current = 0

    def advance(self):
        self.current += 1

        if self.output.has_ansi():
            percent = round(self.current / self.total * 100)
            self.output.write("\x0d")
            self.output.write("\x1b[2K")
            self.output.write(f"... {percent}% ...")
        else:
            self.output.write(".")

    def clear(self):
        if self.output.has_ansi():
            self.output.write("\x0d")
            self.output.write("\x1b[2K")
