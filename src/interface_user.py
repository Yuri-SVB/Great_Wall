import tkinter as tk
from tkinter import simpledialog
from tkinter import messagebox
import sys
import getpass
from src.mnemonic.mnemonic import Mnemonic

class UserInterface:
    def __init__(self):
        self.root = tk.Tk()
        self.index_input_int = 0
        self.index_input_is_valid = False
    #    self.user_chosen_input = ""
        self.user_chosen_input = ""  # Clearing variable
        self.mnemo = Mnemonic(self.user_chosen_input)
        self.get_theme()
        self.get_sa0()






    def run_gui(self):
        self.get_integer(min, max)
        self.root.mainloop()

    def get_integer(self, min, max):
        # Replace this with the actual code to get an integer from the GUI
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
        # For simplicity, using simpledialog.askinteger for demonstration
        self.index_input_int = simpledialog.askinteger("Input", "Enter an integer:", minvalue=min, maxvalue=max)
        self.index_input_is_valid = (min <= self.index_input_int <= max)

    def prompt_integer(self, text, min, max):
        # Replace this with the actual code to display text in the GUI
        label = tk.Label(self.root, text=text)
        label.pack()

        # For simplicity, using Entry widget for input
        entry = tk.Entry(self.root)
        entry.pack()

        # Button click event handler
        def on_button_click():
            nonlocal entry
            input_value = entry.get()

            try:
                self.index_input_int = int(input_value)
                if min <= self.index_input_int <= max:
                    self.index_input_is_valid = True
                    label.pack_forget()  # Hide the label
                    entry.pack_forget()  # Hide the entry
                    button.pack_forget()  # Hide the button
                else:
                    print('parameter cannot be lower than ', min)
            except ValueError:
                print('Please enter an integer')

        # Button widget to confirm the input
        button = tk.Button(self.root, text="OK", command=on_button_click)
        button.pack()
        # For simplicity, using print for demonstration


    def get_theme(self):
        holderstr = "Choose your Formosa theme:\n"
        theme_list = [
            "manual input",
            "medieval_fantasy",
            "BIP39",
            "copy_left",
            "BIP39_french",
            "sci-fi",
            "farm_animals",
            "tourism",
            "cute_pets",
            "finances"
        ]

        for i, theme in enumerate(theme_list):
            holderstr += f"{i}) {theme}\n"

        self.prompt_integer(holderstr, 0, len(theme_list) - 1)


    def get_sa0(self):
        # Replace this with the actual code to get a password from the GUI
        # For simplicity, using simpledialog.askstring for demonstration
        secret_input = simpledialog.askstring("Input", "Enter Time-Lock Puzzle password:")
        self.user_chosen_input = self.mnemo.expand_password(secret_input)
