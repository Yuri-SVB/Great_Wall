import sys

from .interfaces.cli import main_cli
from .interfaces.gui.greatwall_window import main_gui


def main():
    if len(sys.argv) == 2:
        if sys.argv[1].upper() == "GUI":
            main_gui()
        elif sys.argv[1].upper() == "CLI":
            main_cli()
    else:
        print(
            f'  (use "main.py GUI" to run the GreatWall application with graphic user interface)\n'
            f'  (or "main.py CLI" to run with command-line interface)'
        )


if __name__ == "__main__":
    main()
