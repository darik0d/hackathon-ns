#!/usr/bin/env python3
"""
A command line utility for bug handling and tracking
"""

import sys
import os
import logging
import time
import platform
from introduce_bugs import introduce_bugs
from evaluation import evaluate
import random
import click
import pyfiglet
from halo import Halo  # Import Halo
from rich.console import Console
from rich.markdown import Markdown


name = "Bugify"

def clear_screen():
    """Clear the terminal screen based on the operating system"""
    if platform.system() == "Windows":
        os.system('cls')
    else:
        os.system('clear')

def setup_logging():
    """Configure logging for the application"""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[logging.StreamHandler()]
    )
    return logging.getLogger(name)

def display_welcome():
    """Display a welcome ASCII art message using pyfiglet"""
    welcome_text = pyfiglet.figlet_format(name, font='slant')
    click.secho(welcome_text, fg="blue", bold=True)
    click.secho("[ Bug tracking and fixing utility ]", fg="green")

class IndeterminateSpinner:
    """Class for running Halo as an indeterminate spinner"""
    def __init__(self, desc="Processing", **kwargs):
        self.desc = desc
        self.kwargs = kwargs
        self.spinner = None

    def start(self):
        """Start the spinner using Halo"""
        self.spinner = Halo(text=self.desc, **self.kwargs)
        self.spinner.start()

    def stop(self):
        """Stop the spinner and move to next line"""
        if self.spinner:
            self.spinner.stop()
            # Move to next line for clean output after spinner
            sys.stdout.write("\n")
            sys.stdout.flush()

class BugHeroContext:
    """Context class for the CLI"""
    def __init__(self, show_ascii=True, clear_terminal=True):
        if clear_terminal:
            clear_screen()
        
        if show_ascii:
            display_welcome()

# Main CLI group
@click.group()
@click.option('--show-ascii/--no-ascii', default=True, help='Show ASCII art header')
@click.option('--no-clear', is_flag=True, help='Do not clear terminal screen')
@click.pass_context
def cli(ctx, show_ascii, no_clear):
    """BugHero - A command line utility for bug handling and tracking"""
    ctx.obj = BugHeroContext(show_ascii=show_ascii, clear_terminal=not no_clear)

@cli.command()
@click.pass_obj
def eval(ctx):
    """Evaluate the bugfixes created by the developer team"""
    # Create and start the spinner
    spinner = IndeterminateSpinner("Evaluating your performance in finding the bugs", spinner='dots')

    try:
        spinner.start()
        # Simulate work being done (replace with your actual implementation)
        res = evaluate()
        spinner.stop()
        click.secho("✓ Evaluation complete", fg="green")
        #click.secho(res)

        # Convert Markdown text to a Rich object
        rich_md = Markdown(res)

        # Create a Console object from Rich to print formatted Markdown
        console = Console()

        # Print the formatted Markdown to the console
        console.print(rich_md)

        # Sample output (replace with actual results)
    except Exception as e:
        spinner.stop()
        raise

@cli.command()
@click.pass_obj
def start(ctx):
    """Introduce bugs into the code and save the original code"""

    # Get the file list to inject the bugs

    # Get the bug introduction level
    bug_level = click.prompt("Enter the bug level", default=6, type=int)

    # Create the file 
    directory = click.prompt("Please enter a directory path", type=click.Path(exists=True, file_okay=False, dir_okay=True, readable=True))

    file_list = []
    for file in os.listdir(directory):
        item_path = os.path.join(directory, file)
        file_list.append((item_path, random.randint(0, bug_level)))

    # Create and start the spinner
    spinner = IndeterminateSpinner("Introducing bugs into your codebase 😈", spinner='dots')

    try:
        spinner.start()
        introduce_bugs(file_list)
        spinner.stop()
        click.secho(f"✓ {name} successfully introduced bugs in your code", fg="green")

    except Exception as e:
        spinner.stop()
        raise

if __name__ == "__main__":
    try:
        cli()
    except KeyboardInterrupt:
        click.echo()  # New line
        click.secho(f"{name} operation interrupted by user", fg="yellow")
        sys.exit(1)
    except Exception as e:
        click.secho(f"Error: {e}", fg="red")
        sys.exit(1)

