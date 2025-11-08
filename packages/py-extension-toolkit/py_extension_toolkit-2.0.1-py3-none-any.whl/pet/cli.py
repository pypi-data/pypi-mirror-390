#!/usr/bin/env python3
"""
Python Extension Toolkit (PET) CLI
A Python equivalent of the Zoho Extension Toolkit (zet)
"""

import click
from pet.commands import init
from pet.commands import run
from pet.commands import login, logout
from pet.commands import validate
from pet.commands import pack
from pet.commands import push
from pet.commands import pull
from pet.commands import list_workspace


@click.group()
@click.version_option(version="2.0.1")
def cli():
    """Python Extension Toolkit (PET) - A CLI tool for extension development."""
    pass


# Add all commands to the CLI
cli.add_command(init)
cli.add_command(run)
cli.add_command(login)
cli.add_command(logout)
cli.add_command(validate)
cli.add_command(pack)
# cli.add_command(push)
# cli.add_command(pull)
cli.add_command(list_workspace)


if __name__ == "__main__":
    cli()