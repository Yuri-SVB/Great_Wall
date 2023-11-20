import tkinter as tk
from tkinter import messagebox
from tkinter import simpledialog
import random
import argon2
from argon2 import PasswordHasher
from src.mnemonic.mnemonic import Mnemonic
from interface_user import UserInterface
import sys


class GreatWall:
    def __init__(self, sa0, TLP_param, tree_depth, tree_arity, nbytesform):
        # Your existing initialization logic

        #user interface
        self.interface_user = UserInterface()
        self.interface_user.run_gui()

        # formosa

        self.mnemo = Mnemonic()
        self.nbytesform = nbytesform

    # topology
        self.TLP_param = TLP_param
        self.tree_depth = tree_depth
        self.tree_arity = tree_arity

        self.sa0 = self.interface_user.get_sa0()
        self.sa0 = bytes(self.mnemo.to_entropy(self.interface_user.user_chosen_input))

        self.argon2salt = "00000000000000000000000000000000"

        self.states = [bytes.fromhex("00")]*self.tree_depth  # dummy initialization
        self.current_level = 0

        # ... other initialization


#        self.sa0 = bytes(self.mnemo.to_entropy(self.interface_user.user_chosen_input))

# more
        self.state = self.sa0
        self.shuffled_bytes = self.sa0 #dummy initialization
        self.current_level = 0


        self.time_intensive_derivation()
#        self.update_with_long_hash()
#        self.shuffle_bytes()
#        self.get_li_str_query()
#        self.finish_output()
        self.user_dependent_derivation()
    # Your existing CLI methods


    def time_intensive_derivation(self):
        # Existing code
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

    def update_with_long_hash(self):
        # Existing code
        # Existing code
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

    def update_with_quick_hash(self):
        # Existing code
         # Existing code
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
        # Existing code
        """ Shuffles a section of level_hash bytes"""
        a = 4 * ((self.nbytesform * self.tree_arity) // 4)
        self.shuffled_bytes = [self.state[a * i:a * (i + 1)] for i in range(self.tree_arity)]
        random.shuffle(self.shuffled_bytes)

    def get_li_str_query(self):
        # Existing code
        self.shuffle_bytes()
        shuffled_sentences = [self.mnemo.to_mnemonic(bytes_sentence) for bytes_sentence in self.shuffled_bytes]
        listr = "Choose 1, ..., "
        listr += str(self.tree_arity)
        listr += " for level "
        listr += str(self.current_level)
        listr += "\n" if self.current_level == 0 else ", choose 0 to go back\n"
        for i in range(len(shuffled_sentences)):
            listr += str(i + 1) + ") " + shuffled_sentences[i] + "\n"
        return listr

    def finish_output(self):
        if isinstance(self.state, str):
        # Convert string to bytes using UTF-8 encoding
            self.state = self.state.encode('utf-8')
    # Existing code
        print("KA = \n", self.state.hex())
        return self.state

    def user_dependent_derivation(self):
        # Existing code
        self.current_level = 0
        finish = False

        while not finish:
        # Ask user to choose between a set of sentences generated from the shuffled level_hash bytes
            listr = self.get_li_str_query()
            self.interface_user.prompt_integer(listr, 0 if self.current_level != 0 else 1, self.tree_arity)

            if self.interface_user.index_input_int != 0:
                self.interface_user.user_chosen_input = self.shuffled_bytes[self.interface_user.index_input_int - 1]
                # Update the state with user-chosen input

                self.states[self.current_level] = self.state
                self.state += self.interface_user.user_chosen_input

                self.update_with_quick_hash()
                self.current_level += 1
            else:
                self.current_level -= 1
            # Go back to the previous level

                self.state = self.states[self.current_level]

            if self.current_level >= self.tree_depth:
            # Finish and prompt for termination
                self.finish_output()
                self.interface_user.prompt_integer("Enter 1 to terminate derivation and 0 to go back:", 0, 1)

                if self.interface_user.index_input_int == 1:
                    finish = True
                else:
                # Go back to the previous level
                    self.current_level -= 1
                    self.state = self.states[self.current_level]

# from here


#up to here
        self.finish_output()


class RedirectText:
    def __init__(self, text_widget):
        self.text_widget = text_widget

    def write(self, message):
        if isinstance(message, list):
            # If the message is a list, display each element on a new line
            for item in message:
                self.text_widget.insert(tk.END, str(item) + '\n')
        else:
            self.text_widget.insert(tk.END, str(message))


class GreatWallGUI:
    def __init__(self, master):
        self.master = master
        master.title("Great Wall GUI")

        # Initialize variables
        self.sa0_entry = tk.Entry(master)
        self.TLP_param_entry = tk.Entry(master)
        self.tree_depth_entry = tk.Entry(master)
        self.tree_arity_entry = tk.Entry(master)
        self.nbytesform = tk.Entry(master)

        # Create labels and entry fields
        tk.Label(master, text="SA0:").grid(row=0, column=0)
        self.sa0_entry.grid(row=0, column=1)

        tk.Label(master, text="TLP Parameter:").grid(row=1, column=0)
        self.TLP_param_entry.grid(row=1, column=1)

        tk.Label(master, text="Tree Depth:").grid(row=2, column=0)
        self.tree_depth_entry.grid(row=2, column=1)

        tk.Label(master, text="Tree Arity:").grid(row=3, column=0)
        self.tree_arity_entry.grid(row=3, column=1)

        tk.Label(master, text="nbytesform:").grid(row=4, column=0)  # Add this line
        self.nbytesform.grid(row=4, column=1)



        # Create buttons
        tk.Button(master, text="OK", command=self.ok_button).grid(row=5, column=0)
        tk.Button(master, text="Cancel", command=self.cancel_button).grid(row=5, column=1)
        tk.Button(master, text="Go Back", command=self.go_back_button).grid(row=5, column=2)


    def ok_button(self):
        # Retrieve values from entry fields
        sa0_input = self.sa0_entry.get()
        nbytesform = self.nbytesform.get()

        try:
            # Convert the input string to bytes using UTF-8 encoding
            sa0_value = bytes(sa0_input, encoding='utf-8')
            nbytesform = int(nbytesform)

        except UnicodeEncodeError:
            # Handle the case where the input is not a valid string
            messagebox.showerror("Error", "SA0 must be a valid string.")
            return

        self.sa0 = sa0_value
        TLP_param_value = int(self.TLP_param_entry.get())
        tree_depth_value = int(self.tree_depth_entry.get())
        tree_arity_value = int(self.tree_arity_entry.get())
        nbytesform = int(self.nbytesform.get())

        # Create an instance of GreatWall and perform operations
        great_wall_instance = GreatWall(sa0=sa0_value, TLP_param=TLP_param_value, tree_depth=tree_depth_value, tree_arity=tree_arity_value, nbytesform=nbytesform)


        # Perform other operations based on your CLI logic
        great_wall_instance.time_intensive_derivation()
        great_wall_instance.update_with_long_hash()
        great_wall_instance.update_with_quick_hash()
        great_wall_instance.shuffle_bytes()
        great_wall_instance.get_li_str_query()
        great_wall_instance.finish_output()
        great_wall_instance.user_dependent_derivation()

        # Optionally, display the result or perform additional actions
        result = great_wall_instance.finish_output()

        messagebox.showinfo("Result", f"Final Output: {result.hex()}")

    def cancel_button(self):
        self.master.destroy()

    def go_back_button(self):
        # Implement the go back logic if needed
        pass


def main():
    root = tk.Tk()
    app = GreatWallGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()
