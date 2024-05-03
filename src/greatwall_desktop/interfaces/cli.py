import getpass
import sys

from ..greatwall.knowledge.mnemonic.mnemonic import Mnemonic
from ..greatwall.protocol import GreatWall
from ..interfaces.cli import CommandLineInterface


class CommandLineInterface:
    def __init__(self):
        self.index_input_str = ""
        self.index_input_int = 0
        self.index_input_is_valid = False
        self.user_chosen_input = ""
        self.get_theme()
        self.mnemo = Mnemonic(self.user_chosen_input)
        # Clearing variable
        self.user_chosen_input = ""

    def get_integer(self, min_value, max_value):
        self.index_input_is_valid = False
        while not self.index_input_is_valid:
            self.index_input_str = sys.stdin.readline().strip()
            try:
                self.index_input_int = int(self.index_input_str)
                if self.index_input_int < min_value:
                    print("parameter cannot be lower than ", min_value)
                elif max_value < self.index_input_int:
                    print("parameter cannot be higher than ", max_value)
                else:
                    self.index_input_is_valid = True
            except ValueError:
                # Handle the exception
                print("Please enter an integer")

    def prompt_integer(self, text, min_value, max_value):
        print(text)
        self.get_integer(min_value, max_value)

    def get_theme(self):
        holderstr = "Choose your Formosa theme:\n"
        theme_list = Mnemonic.find_themes()
        for i in range(len(theme_list)):
            holderstr += str(i) + ") " + theme_list[i] + "\n"
        self.prompt_integer(holderstr, 0, len(theme_list) - 1)
        self.user_chosen_input = theme_list[self.index_input_int]

    def get_sa0(self):
        secret_input = getpass.getpass(prompt="Enter Time-Lock Puzzle password:").split(
            "\n", 1
        )[0]
        self.user_chosen_input = self.mnemo.expand_password(secret_input)


def main_cli():
    greatwall = GreatWall()
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
