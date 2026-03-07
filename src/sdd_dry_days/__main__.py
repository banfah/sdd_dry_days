"""Entry point for the SDD Dry Days CLI application.

This module serves as the main entry point for the application, enabling users
to run the application using either:
- `python -m sdd_dry_days add` (module execution)
- `sdd add` (after installation with pip install -e .)

The entry point imports the CLI class and instantiates it to handle command-line
argument parsing and command routing.
"""

from .cli import CLI


def main():
    """Main entry point for the SDD Dry Days application.

    Instantiates the CLI class and calls its run() method to process
    command-line arguments and execute the requested command.
    """
    cli = CLI()
    cli.run()


if __name__ == "__main__":
    main()