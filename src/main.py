import sys
from gui import main as gui_main
from cli import UserInterface
from greatwall import GreatWall


def run_greatwall_cli():
    greatwall = GreatWall("Formosa")
    cli = UserInterface()
    greatwall.set_themed_mnemo(cli.mnemo.base_theme)
    # Topology of TLP derivation
    cli.prompt_integer("Choose TLP parameter --- # of iterations of memory-hard hash", 1, 24*7*4*3)
    greatwall.set_tlp(cli.index_input_int)
    # Topology of iterative derivation
    cli.prompt_integer("Choose tree depth --- # of iterative procedural memory choices needed", 1, 256)
    greatwall.set_depth(cli.index_input_int)
    cli.prompt_integer("Choose tree arity --- # of options at each iteration", 2, 256)
    greatwall.set_arity(cli.index_input_int)
    # Diagram values
    cli.get_sa0()
    greatwall.set_sa0(cli.user_chosen_input)

    while not greatwall.is_finished:
        if not greatwall.current_level and not greatwall.is_initialized:
            greatwall.initialize_state_hashes()
        if greatwall.current_level < greatwall.tree_depth:
            listr = greatwall.get_li_str_query()
            cli.prompt_integer(listr, 0 if greatwall.current_level != 0 else 1, greatwall.tree_arity)
            greatwall.derive_from_user_choice(cli.index_input_int)
        else:
            greatwall.finish_output()
            cli.prompt_integer("Enter 1 to terminate derivation and 0 to go back:", 0, 1)
            if not cli.index_input_int:
                greatwall.derive_from_user_choice(cli.index_input_int)


def main():
    if len(sys.argv) == 2:
        if sys.argv[1].upper() == "GUI":
            gui_main()
        elif sys.argv[1].upper() == "CLI":
            run_greatwall_cli()
    else:
        print(f"  (use \"main.py GUI\" to run the GreatWall application with graphic user interface)\n"
              f"  (or \"main.py CLI\" to run with command-line interface)")


if __name__ == '__main__':
    main()
