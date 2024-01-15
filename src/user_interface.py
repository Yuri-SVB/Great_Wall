import sys
import getpass
from mnemonic.mnemonic import Mnemonic


class UserInterface:
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
                    print('parameter cannot be lower than ', min_value)
                elif max_value < self.index_input_int:
                    print('parameter cannot be higher than ', max_value)
                else:
                    self.index_input_is_valid = True
            except ValueError:
                # Handle the exception
                print('Please enter an integer')

    def prompt_integer(self, text, min_value, max_value):
        print(text)
        self.get_integer(min_value, max_value)

    def get_theme(self):
        holderstr = "Choose your Formosa theme:\n"
        theme_list = Mnemonic.find_themes()
        for i in range(len(theme_list)):
            holderstr += str(i) + ") " + theme_list[i] + "\n"
        self.prompt_integer(holderstr, 0, len(theme_list)-1)
        self.user_chosen_input = theme_list[self.index_input_int]

    def get_sa0(self):
        secret_input = getpass.getpass(prompt="Enter Time-Lock Puzzle password:").split("\n", 1)[0]
        self.user_chosen_input = self.mnemo.expand_password(secret_input)
