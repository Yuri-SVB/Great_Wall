import random
import sys
import argon2
from src.mnemonic.mnemonic import Mnemonic
from user_interface import UserInterface


class GreatWall:
    def __init__(self):
        self.mnemo = Mnemonic("medieval_fantasy")
        #user interface
        self.user_interface = UserInterface(self.mnemo)

        #topology of TLP derivation
        self.user_interface.get_TLP_param()
        self.TLP_param = self.user_interface.index_input_int

        #topology of iterative derivation
        self.user_interface.get_tree_depth()
        self.tree_depth = self.user_interface.index_input_int
        self.user_interface.get_tree_arity()
        self.tree_arity = self.user_interface.index_input_int
        self.nbytesform = 4 #number of bytes in formosa sentence
        self.argon2salt = "00000000000000000000000000000000"
            #diagram variables
        # self.user_interface.get_theme() TODO
        # self.mnemo = self.user_interface.user_chosen_input TODO
        self.user_interface.get_sa0()
        print(self.user_interface.user_chosen_input)
        self.sa0 = bytes(self.mnemo.to_entropy(self.user_interface.user_chosen_input))
        self.sa1 = self.sa0         # dummy initialization
        self.sa2 = self.sa0         # dummy initialization
        self.sa3 = self.sa0         # dummy initialization
        self.states = [bytes.fromhex("00")]*self.tree_depth  # dummy initialization
        #state
        self.state = self.sa0
        self.level = 0
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

    def shuffle_bytes(self) -> list[bytes]:
        """ Shuffles a section of level_hash bytes"""
        a = self.nbytesform
        shuffled_bytes = [self.state[a * i:a * (i + 1)] for i in range(self.tree_arity)]
        random.shuffle(shuffled_bytes)
        return shuffled_bytes

    def user_choose(self):
        """ Ask user to choose between a set of sentences generated from the shuffled level_hash bytes"""
        shuffled_bytes = self.shuffle_bytes()
        shuffled_sentences = [self.mnemo.to_mnemonic(bytes_sentence) for bytes_sentence in shuffled_bytes]
        self.user_interface.get_Li_branch_choice(self.tree_arity, self.level, shuffled_sentences)
        self.user_interface.user_chosen_input = shuffled_bytes[self.user_interface.index_input_int - 1]

    def confirm_output(self):
        sentences = self.mnemo.to_mnemonic(self.state[0:16])
        # Split and remove the password line getting the following sentences
        sentences = " ".join(self.mnemo.format_mnemonic(sentences).split("\n", 1)[1:])
        confirm_message = "\nChoose 1 to confirm the sentences, choose 0 to go back\n" + sentences
        print(confirm_message)
        self.index_input_str = int(sys.stdin.readline().strip())

    def finish_output(self):
        print(self.state.hex())
        return self.state

    def user_dependent_derivation(self):
        self.level = 0
        finish = False
        while not finish:
            self.user_choose()
            if self.user_interface.index_input_int != 0:
                self.states[self.level] = self.state
                self.state += self.user_interface.user_chosen_input
                self.update_with_quick_hash()
                self.level += 1
            else:
                self.level -= 1
                self.state = self.states[self.level]
            if self.level >= self.tree_depth:
                self.confirm_output()
                if self.user_interface.index_input_int == 1:
                    finish = True
                else:
                    self.level -= 1
        self.finish_output()

def main():
    GreatWall()


if __name__ == "__main__":
    main()
