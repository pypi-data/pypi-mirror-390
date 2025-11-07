from .color import AnsiColor
import sys


class ConsoleWriter:
    def __init__(self, stdout=sys.stdout, stderr=sys.stderr, colorizer=AnsiColor()):
        self.stdout = stdout
        self.stderr = stderr
        self.colorizer = colorizer

    def header(self, message, eol=True):
        self.write(self.colorizer.white(message, attr="bold"), eol)

    def success(self, message, eol=True):
        self.write(self.colorizer.green(message), eol)

    def warn(self, message, eol=True):
        self.write(self.colorizer.yellow(message), eol)

    def error(self, message, eol=True):
        self.write_error(self.colorizer.red(message), eol)

    def write(self, message, eol=True):
        self.stdout.write(message)
        if eol:
            self.stdout.write("\n")

    def write_error(self, message, eol=True):
        self.stderr.write(message)
        if eol:
            self.stderr.write("\n")
