# MIT License
#
# Copyright (c) 2024 Clivern
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

import click

from txy import __version__
from txy.command import (
    CreateCommand,
    ListCommand,
    InfoCommand,
    RemoveCommand,
    CurrentCommand,
)


@click.group(help="🐺 Python Virtual Environment Manager.")
@click.version_option(version=__version__, help="Show the current version")
def main():
    """Main command group for Txy CLI."""
    pass


@main.command(help="Create a virtual environment")
@click.argument("name")
def create(name):
    CreateCommand().run(name)


@main.command(help="Get info of virtual environments")
@click.argument("name")
def info(name):
    InfoCommand().run(name)


@main.command(help="Get a list of virtual environments")
def list():
    ListCommand().run()


@main.command(help="Get a current virtual environment activate path")
def current():
    CurrentCommand().run()


@main.command(help="Remove a virtual environment")
@click.argument("name")
def remove(name):
    RemoveCommand().run(name)


if __name__ == "__main__":
    main()
