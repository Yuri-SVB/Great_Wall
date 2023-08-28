import random
import argon2
from src.mnemonic.mnemonic import Mnemonic
from user_interface import UserInterface


class GreatWall:
    def __init__(self):
        # self.user_interface.get_theme() TODO
        # self.mnemo = self.user_interface.user_chosen_input TODO
        self.mnemo = Mnemonic("medieval_fantasy")
        self.nbytesform = 4 #number of bytes in formosa sentence TODO soft code me
        #constants
        self.argon2salt = "00000000000000000000000000000000"

        #user interface
        self.user_interface = UserInterface(self.mnemo)

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

    def time_intensive_derivation(self):
        # Calculating SA1 from SA0
        print('Initializing SA0')
        self.state = self.sa0
        print('Deriving SA0 -> SA1')
        self.update_with_quick_hash()
        self.sa1 = self.state
        print('Deriving SA1 -> SA2')
        self.update_with_long_hash()
        self.sa2 = self.state
        self.state = self.sa0 + self.state
        print('Deriving SA2 -> SA3')
        self.update_with_quick_hash()
        self.sa3 = self.state

    def update_with_long_hash(self):
        """ Update self.level_hash with the hash of the previous self.level_hash taking presumably a long time"""
        for i in range(self.TLP_param):
            print("iteration #", i+1, " of TLP:")
            self.state = argon2.argon2_hash(
                password=self.state,
                salt=self.argon2salt,
                t=8,
                m=1048576,
                p=1,
                buflen=128,
                argon_type=argon2.Argon2Type.Argon2_i
            )

    def update_with_quick_hash(self):
        """ Update self.level_hash with the hash of the previous self.level_hash taking presumably a quick time"""
        self.state = argon2.argon2_hash(
            password=self.state,
            salt=self.argon2salt,
            t=32,
            m=1024,
            p=1,
            buflen=128,
            argon_type=argon2.Argon2Type.Argon2_i
        )

    def shuffle_bytes(self):
        """ Shuffles a section of level_hash bytes"""
        a = self.nbytesform
        self.shuffled_bytes = [self.state[a * i:a * (i + 1)] for i in range(self.tree_arity)]
        random.shuffle(self.shuffled_bytes)

    def get_li_str_query(self) -> str:
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
        print("KA = \n", self.state.hex())
        return self.state

    def user_dependent_derivation(self):
        self.current_level = 0
        finish = False
        while not finish:
            """ Ask user to choose between a set of sentences generated from the shuffled level_hash bytes"""
            listr = self.get_li_str_query()
            self.user_interface.prompt_integer(listr, 0 if self.current_level != 0 else 1, self.tree_arity)
            if self.user_interface.index_input_int != 0:
                self.user_interface.user_chosen_input = self.shuffled_bytes[self.user_interface.index_input_int - 1]
                self.states[self.current_level] = self.state
                self.state += self.user_interface.user_chosen_input
                self.update_with_quick_hash()
                self.current_level += 1
            else:
                self.current_level -= 1
                self.state = self.states[self.current_level]
            if self.current_level >= self.tree_depth:
                self.finish_output()
                self.user_interface.prompt_integer("Enter 1 to terminate derivation and 0 to go back:", 0, 1)
                if self.user_interface.index_input_int == 1:
                    finish = True
                else:
                    self.current_level -= 1
                    self.state = self.states[self.current_level]
        # self.finish_output()

def main():
    GreatWall()


if __name__ == "__main__":
    main()
