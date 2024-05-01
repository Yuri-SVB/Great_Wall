import sys

from .greatwall.protocol import GreatWall
from .interfaces.cli import CommandLineInterface
from .interfaces.gui.greatwall_window import GreatWallWindow
from .interfaces.gui.memorization_window import MemorizationAssistantWindow


def run_greatwall_cli():
    greatwall = GreatWall("Formosa")
    commandline_interface = CommandLineInterface()
    greatwall.set_themed_mnemo(commandline_interface.mnemo.base_theme)
    # Topology of TLP derivation
    commandline_interface.prompt_integer(
        "Choose TLP parameter --- # of iterations of memory-hard hash",
        1,
        24 * 7 * 4 * 3,
    )
    greatwall.set_tlp_param(commandline_interface.index_input_int)
    # Topology of iterative derivation
    commandline_interface.prompt_integer(
        "Choose tree depth --- # of iterative procedural memory choices needed", 1, 256
    )
    greatwall.set_depth(commandline_interface.index_input_int)
    commandline_interface.prompt_integer(
        "Choose tree arity --- # of options at each iteration", 2, 256
    )
    greatwall.set_arity(commandline_interface.index_input_int)
    # Diagram values
    commandline_interface.get_sa0()
    greatwall.set_sa0(commandline_interface.user_chosen_input)

    while not greatwall.is_finished:
        if not greatwall.current_level and not greatwall.is_initialized:
            greatwall.init_protocol_values()
        if greatwall.current_level < greatwall.tree_depth:
            list_str = greatwall.get_li_str_query()
            commandline_interface.prompt_integer(
                list_str, 0 if greatwall.current_level != 0 else 1, greatwall.tree_arity
            )
            greatwall.derive_from_user_choice(commandline_interface.index_input_int)
        else:
            greatwall.finish_output()
            commandline_interface.prompt_integer(
                "Enter 1 to terminate derivation and 0 to go back:", 0, 1
            )
            if not commandline_interface.index_input_int:
                greatwall.derive_from_user_choice(commandline_interface.index_input_int)


def main():
    if len(sys.argv) == 2:
        if sys.argv[1].upper() == "GUI":
            app = QApplication([])
            window = GreatWallWindow()
            window.show()
            app.exec_()
        elif sys.argv[1].upper() == "CLI":
            run_greatwall_cli()
    else:
        print(
            f'  (use "main.py GUI" to run the GreatWall application with graphic user interface)\n'
            f'  (or "main.py CLI" to run with command-line interface)'
        )


if __name__ == "__main__":
    main()
