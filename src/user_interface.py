import sys
import getpass
from src.mnemonic.mnemonic import Mnemonic

class UserInterface:
    def __init__(self, mnemo):
        self.mnemo = mnemo
        self.index_input_str = ""
        self.index_input_int = 0
        self.index_input_is_valid = False
        self.user_chosen_input = ""

    def get_integer(self, min, max) :
        self.index_input_is_valid = False
        while not self.index_input_is_valid:
            self.index_input_str = sys.stdin.readline().strip()
            try:
                self.index_input_int = int(self.index_input_str)
                if self.index_input_int < min:
                    print('parameter cannot be lower than ', min)
                elif max < self.index_input_int:
                    print('parameter cannot be higher than ', max)
                else:
                    self.index_input_is_valid = True
            except ValueError:
                # Handle the exception
                print('Please enter an integer')

    def prompt_integer(self, text, min, max):
        print(text)
        self.get_integer(min, max)

    def get_theme(self) :
        pass

    def get_sa0(self) :
        secret_input = getpass.getpass(prompt="Enter Time-Lock Puzzle password:").split("\n", 1)[0]
        self.user_chosen_input = self.mnemo.expand_password(secret_input)