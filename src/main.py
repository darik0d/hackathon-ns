#!/usr/bin/env python3
"""
A command line utility for bug handling and tracking
"""

import sys
import os
import logging
import time
import platform
import threading

import click
import pyfiglet
from halo import Halo  # Import Halo


name = "DevProbe"

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
        
        self.logger = setup_logging()
        if show_ascii:
            display_welcome()
        self.logger.info(click.style(f"Initializing {name}", fg="green"))

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
    ctx.logger.info(click.style("Starting evaluation of your performance", fg="yellow"))
    
    # Create and start the spinner
    spinner = IndeterminateSpinner("Evaluating your performance in finding the bugs", spinner='dots')
    
    try:
        spinner.start()
        
        # Simulate work being done (replace with your actual implementation)
        time.sleep(5)  # Simulating longer work
        
        # TODO: Implement your evaluation logic here
        
        spinner.stop()
        click.secho("✓ Evaluation complete", fg="green")
        
        # Sample output (replace with actual results)
    except Exception as e:
        spinner.stop()
        ctx.logger.error(click.style(f"Evaluation failed: {str(e)}", fg="red"))
        raise

@cli.command()
@click.pass_obj
def start(ctx):
    """Introduce bugs into the code and save the original code"""
    ctx.logger.info(click.style(f"Starting {name}", fg="magenta"))
    
    # Create and start the spinner
    spinner = IndeterminateSpinner("Introducing bugs into your codebase 😈", spinner='dots')
    
    try:
        spinner.start()
        
        # Simulate startup sequence (replace with your actual implementation)
        time.sleep(4)  # Simulating work
        
        # TODO: Implement your startup logic here
        
        spinner.stop()
        click.secho(f"✓ {name} successfully introduced bugs in your code", fg="green")
        
    except Exception as e:
        spinner.stop()
        ctx.logger.error(click.style(f"Startup failed: {str(e)}", fg="red"))
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

