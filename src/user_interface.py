import tkinter as tk
from tkinter import simpledialog
import sys
from mnemonic.mnemonic import Mnemonic

class UserInterface:
    def __init__(self):
        self.index_input_str = ""
        self.index_input_int = 0
        self.index_input_is_valid = False
        self.user_chosen_input = ""
        self.get_theme()
        self.mnemo = Mnemonic(self.user_chosen_input)
        self.user_chosen_input = "" #clearing variable

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
        root = tk.Tk() #edits
        root.withdraw()
        self.index_input_int = simpledialog.askinteger("Input", text, minvalue=min, maxvalue=max)
        # No need to set self.index_input_is_valid since askinteger ensures a valid input
        root.destroy()

    def get_theme(self) : #TODO user-safety me, sof-code me
        holderstr = "Choose your Formosa theme:\n"
        theme_list = []
        theme_list.append("manual input")
        theme_list.append("medieval_fantasy")
        theme_list.append("BIP39")
        theme_list.append("copy_left")
        theme_list.append("BIP39_french")
        theme_list.append("sci - fi")
        theme_list.append("farm_animals")
        theme_list.append("tourism")
        theme_list.append("cute_pets")
        theme_list.append("finances")
        for i in range(len(theme_list)):
            holderstr += str(i) + ") " + theme_list[i] + "\n"
        self.prompt_integer(holderstr, 0, len(theme_list)-1)

        self.user_chosen_input = sys.stdin.readline().strip() if self.index_input_int == 0 else theme_list[self.index_input_int]

    def get_sa0(self) :
        root = tk.Tk()
        root.withdraw()
        secret_input = simpledialog.askstring("Input", "Enter Time-Lock Puzzle password:", show='*')
        root.destroy()
        self.user_chosen_input = self.mnemo.expand_password(secret_input)
