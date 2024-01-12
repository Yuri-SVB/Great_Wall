import random
import argon2
import tkinter as tk
from tkinter import simpledialog
from argon2 import PasswordHasher
from src.mnemonic.mnemonic import Mnemonic
from user_interface import UserInterface

class GreatWallUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Great Wall UI")
        self.create_widgets()



    def create_widgets(self):
        self.label = tk.Label(self.root, text="Welcome to Great Wall UI!")
        self.label.pack(pady=10)

        self.derivation_button = tk.Button(self.root, text="Start Derivation", command=self.start_derivation)
        self.derivation_button.pack(pady=10)

        self.info_label = tk.Label(self.root, text="")
        self.info_label.pack(pady=10)




    def start_derivation(self):
        self.info_label.config(text="Derivation in progress...")
        self.root.after(100, self.execute_derivation)

    def execute_derivation(self):
        great_wall = GreatWall(self)
        great_wall.user_dependent_derivation()
        result = great_wall.finish_output()
        messagebox.showinfo("Derivation Result", f"KA = {result.hex()}")
        self.root.quit()

    def get_user_input(self, prompt, minvalue, maxvalue):
        return simpledialog.askinteger("User Input", prompt, minvalue=minvalue, maxvalue=maxvalue)



    def get_li_str_query(self):
        self.info_label.config(text="Choosing from shuffled options...")
        self.shuffle_window = tk.Toplevel(self.root)
        self.shuffle_window.title("Shuffled Options")

        listr = GreatWall(self).get_li_str_query()
        label = tk.Label(self.shuffle_window, text=listr)
        label.pack(pady=10)

        user_choice = self.get_user_input("Enter a choice:", 0, GreatWall(self).tree_arity)
        self.shuffle_window.destroy()
        return user_choice

    def choose_formosa_theme(self):
        self.info_label.config(text="Choosing Formosa Theme...")
        self.choose_formosa_theme()

        selected_theme = self.user_interface.user_chosen_input
        self.info_label.config(text=f"Selected Formosa Theme: {selected_theme}")


        user_interface = UserInterface()
        user_interface.get_theme()  # Call the get_theme method
        selected_theme = user_interface.user_chosen_input
        self.info_label.config(text=f"Selected Formosa Theme: {selected_theme}")






class GreatWall:
    def __init__(self, ui):
        #user interface
        self.ui = ui
        self.user_interface = UserInterface()

        #Formosa
        self.mnemo = self.user_interface.mnemo
        self.nbytesform = 4 #number of bytes in formosa sentence TODO soft code me

        #constants
        self.argon2salt = "00000000000000000000000000000000"

        #topology of TLP derivation
        self.user_interface.prompt_integer("Choose TLP parameter --- # of iterations of memory-hard hash", 1, 24*7*4*3)
        self.TLP_param = self.user_interface.index_input_int

        #topology of iterative derivation
        self.user_interface.prompt_integer("Choose tree depth --- # of iterative procedural memory choices needed", 1, 256)
        self.tree_depth = self.user_interface.index_input_int
        self.user_interface.prompt_integer("Choose tree arity --- # of options at each iteration", 2, 256)
        self.tree_arity = self.user_interface.index_input_int

        #diagram values
        self.user_interface.get_sa0()
        self.sa0 = bytes(self.mnemo.to_entropy(self.user_interface.user_chosen_input))
        self.sa1 = self.sa0         # dummy initialization
        self.sa2 = self.sa0         # dummy initialization
        self.sa3 = self.sa0         # dummy initialization
        self.states = [bytes.fromhex("00")]*self.tree_depth  # dummy initialization

        #state
        self.state = self.sa0
        self.shuffled_bytes = self.sa0 #dummy initialization
        self.current_level = 0

        #actuall work
        self.time_intensive_derivation()
        self.user_dependent_derivation()

    def time_intensive_derivation(self):# Existing code
        print('Initializing SA0')
        initial_state = self.sa0
        if isinstance(self.sa0, str):
            self.sa0 = self.sa0.encode('utf-8')

        if isinstance(initial_state, str):
            self.state = self.state.encode('utf-8')

        self.state = self.sa0 + initial_state

        print('Deriving SA0 -> SA1')
        self.update_with_quick_hash()
        self.sa1 = self.state
        self.state = initial_state
        print('Deriving SA1 -> SA2')
        self.update_with_long_hash()
        self.sa2 = self.state

        print('Deriving SA2 -> SA3')
        self.update_with_quick_hash()
        self.sa3 = self.state

    def update_with_long_hash(self):# Existing code
        """ Update self.level_hash with the hash of the previous self.level_hash taking presumably a long time"""
        ph = PasswordHasher()

        salt_bytes = bytes.fromhex(self.argon2salt)

        for i in range(self.TLP_param):
            print("iteration #", i+1, " of TLP:")

            if isinstance(self.sa0, str):
                self.sa0 = self.sa0.encode('utf-8')

            if isinstance(self.state, str):
                self.state = self.state.encode('utf-8')

            password = self.sa0 + self.state

            self.state = ph.hash(
            password=password,
            salt=salt_bytes,
    #        time_cost=8,
    #        memory_cost=1048576,
    #        parallelism=1,
    #        hash_len=128,
    #        type='argon2i'
        )

    def update_with_quick_hash(self): # Existing code
        """ Update self.level_hash with the hash of the previous self.level_hash taking presumably a quick time"""
        ph = PasswordHasher()
        salt_bytes = bytes.fromhex(self.argon2salt)
        self.state = ph.hash(
        password=self.state,
        salt=salt_bytes,
    #    time_cost=32,
    #    parallelism=1,
    #    hash_len=128,
    #    type='argon2i'
        )

    def shuffle_bytes(self):
        """ Shuffles a section of level_hash bytes"""
        a = self.nbytesform
        self.shuffled_bytes = [self.state[a * i:a * (i + 1)] for i in range(self.tree_arity)]
        random.shuffle(self.shuffled_bytes)

    def get_li_str_query(self):
        self.shuffle_bytes()
        shuffled_sentences = [self.mnemo.to_mnemonic(bytes_sentence) for bytes_sentence in self.shuffled_bytes]
        listr = "Choose 1, ..., "
        listr += str(self.tree_arity)
        listr += " for level "
        listr += str(self.current_level)
        listr += "\n" if self.current_level == 0 else ", choose 0 to go back\n"

        for i, sentence in enumerate(shuffled_sentences):
            listr += f"{i + 1}) {sentence}\n"

#        for i in range(len(shuffled_sentences)):
#            listr += str(i + 1) + ") " + shuffled_sentences[i] + "\n"
        return listr

    def finish_output(self):
        result = self.state.hex()
        self.ui.info_label.config(text=f"KA = \n{result}")
        return self.state
        print("KA = \n", self.state.hex())
        return self.state

    def user_dependent_derivation(self):
        # Existing code
        self.current_level = 0
        finish = False
        while not finish:
        # Ask user to choose between a set of sentences generated from the shuffled level_hash bytes
            listr = self.get_li_str_query()
            self.ui.info_label.config(text=listr)

            user_choice = simpledialog.askinteger(
                "User Input",
                f"Enter a choice (1 to {self.tree_arity}, 0 to go back):",
                initialvalue=0 if self.current_level != 0 else 1,
                minvalue=0 if self.current_level != 0 else 1,
                maxvalue=self.tree_arity
            )


            if 0 < user_choice <= self.tree_arity:
                self.user_interface.user_chosen_input = self.shuffled_bytes[user_choice - 1]
                self.states[self.current_level] = self.state
                self.state += self.user_interface.user_chosen_input
                self.update_with_quick_hash()
                self.current_level += 1
            elif user_choice == 0:
                self.current_level -= 1
                self.state = self.states[self.current_level]
            else:
                print("Invalid choice. Please enter a valid option.")

            if self.current_level >= self.tree_depth:

                termination_choice = simpledialog.askinteger(
                    "User Input",
                    "Enter 1 to terminate derivation and 0 to go back:",
                    initialvalue=0,
                    minvalue=0,
                    maxvalue=1
                )
                if termination_choice == 1:
                    finish = True
                elif termination_choice == 0:
                    # Go back to the previous level
                    self.current_level -= 1
                    self.state = self.states[self.current_level]
                else:
                    print("Invalid choice. Please enter a valid option.")

    def run_derivation(self):
        self.time_intensive_derivation()
        self.user_dependent_derivation()
        return self.finish_output()


def main():
    root = tk.Tk()
    app = GreatWallUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()
