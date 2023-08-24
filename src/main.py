import random
import sys
import argon2
import getpass
from src.mnemonic.mnemonic import Mnemonic


class GreatWall:
    def __init__(self, mnemo, sa0):
        #topology of iterative derivation
        self.tree_depth = 64
        self.tree_arity = 8
        self.nbytesform = 4 #number of bytes in formosa sentence
        self.argon2salt = "00000000000000000000000000000000"
        #diagram variables
        self.mnemo = mnemo
        self.sa0 = bytes(self.mnemo.to_entropy(sa0))
        self.sa1 = bytes(self.mnemo.to_entropy(sa0))    # dummy initialization
        self.sa2 = bytes(self.mnemo.to_entropy(sa0))    # dummy initialization
        self.sa3 = bytes(self.mnemo.to_entropy(sa0))    # dummy initialization
        self.states = [bytes.fromhex("00")]*self.tree_depth
        #state
        self.state = self.sa0
        self.level = 0
        #user interface
        self.index_input_str = ""
        self.index_input_int = 0
        self.index_input_is_valid = False
        self.user_chosen_input = 0

        self.time_intensive_derivation()
        self.user_dependent_derivation()

    def time_intensive_derivation(self):
        # Calculating SA1 from SA0
        self.state = self.sa0
        self.update_with_quick_hash()
        self.sa1 = self.state
        self.update_with_long_hash()
        self.sa2 = self.state
        self.state = self.sa0 + self.state
        self.update_with_quick_hash()
        self.sa3 = self.state

    def update_with_long_hash(self):
        """ Update self.level_hash with the hash of the previous self.level_hash taking presumably a long time"""
        self.state = argon2.argon2_hash(
            password=self.state,
            salt=self.argon2salt,
            t=32,
            m=16,
            p=1,
            buflen=128,
            argon_type=argon2.Argon2Type.Argon2_i
        )
        # self.level_hash += bytes.fromhex("0a")

    def update_with_quick_hash(self):
        """ Update self.level_hash with the hash of the previous self.level_hash taking presumably a quick time"""
        self.state = argon2.argon2_hash(self.state, self.argon2salt, m=16)
        # self.state = argon2.argon2_hash(
        #     password=self.state,
        #     salt=self.argon2salt,
        #     t=32,
        #     m=16,
        #     p=1,
        #     buflen=128,
        #     argon_type=argon2.Argon2Type.Argon2_i
        # )
        # self.level_hash += bytes.fromhex("0a")

    def shuffle_bytes(self) -> list[bytes]:
        """ Shuffles a section of level_hash bytes"""
        a = self.nbytesform
        shuffled_bytes = [self.state[a * i:a * (i + 1)] for i in range(self.tree_arity)]
        random.shuffle(shuffled_bytes)
        return shuffled_bytes

    def user_choose(self):
        """ Ask user to choose between a set of sentences generated from the shuffled level_hash bytes"""
        shuffled_bytes = self.shuffle_bytes()
        choose_message = "\nChoose 1, ..., %d for level %d"
        choose_message += "" if self.level < 1 else ", choose 0 to go back"
        print(choose_message % (self.tree_arity,  self.level))
        [print(self.mnemo.to_mnemonic(bytes_sentence)) for bytes_sentence in shuffled_bytes]

        self.index_input_is_valid = False
        while not self.index_input_is_valid:
            self.index_input_str = sys.stdin.readline().strip()
            try:
                self.index_input_int = int(self.index_input_str)
                if self.index_input_int == 0:
                    if self.level < 1:
                        print('You cannot go back at this point. This is level 0.')
                        # self.index_input_is_valid = False # it was already False
                    else:
                        self.index_input_is_valid = True
                else:
                    if 1 <= self.index_input_int and self.index_input_int <= self.tree_arity:
                        self.index_input_is_valid = True
                    else:
                        print('Index must be within valid range.')
                        # self.index_input_is_valid = False # it was already False
            except ValueError:
                # Handle the exception
                print('Please enter an integer')
        self.user_chosen_input = shuffled_bytes[self.index_input_int - 1]

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
            if self.index_input_int:
                self.states[self.level] = self.state
                self.state += self.user_chosen_input
                self.update_with_quick_hash()
                self.level += 1
            else:
                self.level -= 1
                self.state = self.states[self.level]
            if self.level >= self.tree_depth:
                self.confirm_output()
                if self.index_input_int:
                    finish = True
                else:
                    self.level -= 1
        self.finish_output()

def main():
    # sa = "e41feeeee282bc5411ce97df78b3660e"
    # sa = "00000000000000000000000000000000"
    # sa = "00000000000000"
    # print(entropy)
    # sentences = "king unveil sweet wine queen throne_room ogre swing wooden club cyclops mountain " \
    #             "summoner create secret spellbook spirit temple pirate swing fizzy tankard buccaneer brewery"

    # entropy = "".join([str(i).zfill(2) for i in range(16)])
    # entropy = bytes.fromhex(entropy)
    # mnemo = Mnemonic("medieval_fantasy")
    # sa = mnemo.to_mnemonic(entropy)
    # sa = mnemo.format_mnemonic(sa)
    # print(sa)

    mnemo = Mnemonic("medieval_fantasy")
    # Get the first line, which is the line password, from the inserted input
    secret_input = getpass.getpass(prompt="Enter Time-Lock Puzzle password:").split("\n", 1)[0]
    sa = mnemo.expand_password(secret_input)
    GreatWall(mnemo, sa)


if __name__ == "__main__":
    main()
