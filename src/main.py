#!/usr/bin/env python3
"""
BugHero - A command line utility for bug handling and tracking
"""

import argparse
import sys
import os
import logging
import time
import threading
from itertools import cycle
import platform

# Terminal color and formatting modules
try:
    from colorama import init, Fore, Back, Style
    # Initialize colorama for Windows terminals
    init()
    HAS_COLORAMA = True
except ImportError:
    HAS_COLORAMA = False

# Define color constants
if HAS_COLORAMA:
    RED = Fore.RED
    GREEN = Fore.GREEN
    YELLOW = Fore.YELLOW
    BLUE = Fore.BLUE
    CYAN = Fore.CYAN
    MAGENTA = Fore.MAGENTA
    WHITE = Fore.WHITE
    BRIGHT = Style.BRIGHT
    RESET = Style.RESET_ALL
else:
    # Fallback using ANSI escape sequences
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    MAGENTA = '\033[95m'
    WHITE = '\033[97m'
    BRIGHT = '\033[1m'
    RESET = '\033[0m'


def setup_logging():
    """Configure logging for the application"""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[logging.StreamHandler()]
    )
    return logging.getLogger("bughero")


class Spinner:
    """Class to display a spinning animation in the terminal"""
    def __init__(self, message="Processing", speed=0.1):
        self.spinner = cycle(['⣾', '⣽', '⣻', '⢿', '⡿', '⣟', '⣯', '⣷'])
        self.message = message
        self.speed = speed
        self.stop_event = threading.Event()
        self.spinner_thread = None

    def spin(self):
        while not self.stop_event.is_set():
            sys.stdout.write(f"\r{CYAN}{self.message} {next(self.spinner)}{RESET}")
            sys.stdout.flush()
            time.sleep(self.speed)

    def start(self):
        self.spinner_thread = threading.Thread(target=self.spin)
        self.spinner_thread.daemon = True
        self.spinner_thread.start()

    def stop(self):
        if self.spinner_thread:
            self.stop_event.set()
            self.spinner_thread.join()
            sys.stdout.write("\r")
            sys.stdout.flush()


def display_welcome():
    """Display a welcome ASCII art message"""
    welcome_text = f"""{BRIGHT}{BLUE}
 ____              _   _                
|  _ \            | | | |               
| |_) |_   _  __ _| |_| | ___ _ __ ___  
|  _ <| | | |/ _` |  _  |/ _ \ '__/ _ \ 
| |_) | |_| | (_| | | | |  __/ | | (_) |
|____/ \__,_|\__, |_| |_|\___|_|  \___/ 
              __/ |                     
             |___/                      
{RESET}
{GREEN}[ Bug tracking and fixing utility ]{RESET}
"""
    print(welcome_text)


class BugHero:
    """Main class for the BugHero utility"""

    def __init__(self):
        self.logger = setup_logging()
        display_welcome()
        self.logger.info(f"{GREEN}Initializing BugHero{RESET}")

    def eval(self, args):
        """
        Evaluate the bugfixes created by the developer team using diff and LLM
        """
        spinner = Spinner(f"Evaluating your performance in finding the bugs")
        
        try:
            self.logger.info(f"{YELLOW}Starting evaluation of your performance{RESET}")
            spinner.start()
            
            # Simulate work being done (replace with your actual implementation)
            time.sleep(3)  # Simulating work
            
            # TODO: Implement your evaluation logic here
            
            spinner.stop()
            print(f"\n{GREEN}✓ Evaluation complete {RESET}")
            
            # Sample output (replace with actual results)
        except Exception as e:
            spinner.stop()
            self.logger.error(f"{RED}Evaluation failed: {str(e)}{RESET}")
            raise

    def start(self, args):
        """
        Introduces bugs into the code and saves the original code to the ./orginal
        """
        spinner = Spinner(f"Starting BugHero - introducing bugs 😈")
        
        try:
            self.logger.info(f"{MAGENTA}Starting BugHero")
            spinner.start()
            
            # Simulate startup sequence (replace with your actual implementation)
            time.sleep(2)  # Simulating startup
            
            # TODO: Implement your startup logic here
            
            spinner.stop()
            print(f"\n{GREEN}✓ BugHero successfully introduced bugs in your code")
            
        except Exception as e:
            spinner.stop()
            self.logger.error(f"{RED}Startup failed: {str(e)}{RESET}")
            raise


def main():
    """Entry point for the command line utility"""
    if platform.system() == "Windows" and not HAS_COLORAMA:
        print("For best experience, install colorama: pip install colorama")
    
    parser = argparse.ArgumentParser(
        description="BugHero - A command line utility for bug handling and tracking"
    )
    subparsers = parser.add_subparsers(dest="command", help="Commands")
    subparsers.required = True

    # Eval command
    eval_parser = subparsers.add_parser("eval", help="Evaluate code or bug reports")
    eval_parser.set_defaults(func=lambda args: BugHero().eval(args))

    # Start command
    start_parser = subparsers.add_parser("start", help="Start BugHero services")
    start_parser.set_defaults(func=lambda args: BugHero().start(args))

    # Parse args and call the appropriate function
    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n{YELLOW}BugHero operation interrupted by user{RESET}")
        sys.exit(1)
    except Exception as e:
        print(f"{RED}Error: {e}{RESET}")
        sys.exit(1)
