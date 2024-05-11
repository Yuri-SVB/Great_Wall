import sys

from .interfaces.cli import main_cli
from .interfaces.gui.main_window import main_gui


def main():
    if len(sys.argv) == 2:
        if sys.argv[1].upper() == "GUI":
            main_gui()
        elif sys.argv[1].upper() == "CLI":
            main_cli()
    else:
        print(
            "Use 'main.py GUI' to run the app with graphic user interface and\n"
            + "use 'main.py GUI' to run the app with command-line interface."
        )


if __name__ == "__main__":
    main()
