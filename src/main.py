import random
import sys
import argon2
import getpass
from src.mnemonic.mnemonic import Mnemonic


class GreatWall:
    def __init__(self, mnemo, sa0):
        self.mnemo = mnemo
        self.sa0 = bytes(self.mnemo.to_entropy(sa0))
        self.sa1 = bytes(self.mnemo.to_entropy(sa0))    //dummy initialization
        self.sa2 = bytes(self.mnemo.to_entropy(sa0))    //dummy initialization
        self.sa3 = bytes(self.mnemo.to_entropy(sa0))    //dummy initialization
        self.state = self.sa0
        self.input_chosen = self.index_input = self.level = 0
        self.iterations = 64
        self.states = [bytes.fromhex("00")]*self.iterations
        self.number_sentences = 4

        self.time_intensive_derivation(sa0_entropy)
        self.user_dependent_derivation()

    def time_intensive_derivation(self, sa0_entropy):
        # Calculating SA1 from SA0
        self.update_with_quick_hash()
        self.sa1 = self.state
        self.update_with_long_hash()
        self.sa2 = self.state
        self.state = self.sa0 + self.state
        self.update_with_quick_hash()
        self.sa3 = self.state

    def update_with_long_hash(self):
        """ Update self.level_hash with the hash of the previous self.level_hash taking presumably a long time"""
        # This salt should be a counter
        salt = "00000000000000000000000000000000"
        t = 32
        m = 16
        self.state = argon2.argon2_hash(self.state, salt, t=t, m=m)
        # self.level_hash += bytes.fromhex("0a")

    def update_with_quick_hash(self):
        """ Update self.level_hash with the hash of the previous self.level_hash taking presumably a quick time"""
        # This salt should be a counter
        salt = "00000000000000000000000000000000"
        m = 16
        self.state = argon2.argon2_hash(self.state, salt, m=m)
        # self.level_hash += bytes.fromhex("0a")

    def shuffle_bytes(self) -> list[bytes]:
        """ Shuffles a section of level_hash bytes"""
        # Remove magic number
        a = self.number_sentences
        shuffled_bytes = [self.state[a * i:a * (i + 1)] for i in range(a)]
        random.shuffle(shuffled_bytes)
        return shuffled_bytes

    def user_choose(self):
        """ Ask user to choose between a set of sentences generated from the shuffled level_hash bytes"""
        shuffled_bytes = self.shuffle_bytes()
        choose_message = "\nChoose 1, 2, 3, 4 for level %d"
        choose_message += "" if self.level < 1 else ", choose 0 to go back"
        print(choose_message % self.level)
        [print(self.mnemo.to_mnemonic(bytes_sentence)) for bytes_sentence in shuffled_bytes]

        possible_inputs = ["1", "2", "3", "4"]
        self.index_input = ""
        if self.level > 0:
            possible_inputs.append("0")
        while self.index_input not in possible_inputs:
            self.index_input = sys.stdin.readline().strip()
        self.index_input = int(self.index_input)
        self.input_chosen = shuffled_bytes[self.index_input - 1]

    def confirm_output(self):
        sentences = self.mnemo.to_mnemonic(self.state[0:16])
        # Split and remove the password line getting the following sentences
        sentences = " ".join(self.mnemo.format_mnemonic(sentences).split("\n", 1)[1:])
        confirm_message = "\nChoose 1 to confirm the sentences, choose 0 to go back\n" + sentences
        print(confirm_message)
        self.index_input = int(sys.stdin.readline().strip())

    def finish_output(self):
        print(self.state.hex())
        return self.state

    def user_dependent_derivation(self):
        self.level = 0
        finish = False

        while not finish:
            self.user_choose()
            if self.index_input:
                self.states[self.level] = self.state
                self.state += self.input_chosen
                self.update_with_quick_hash()
                self.level += 1
            else:
                self.level -= 1
                self.state = self.states[self.level]
            if self.level >= self.iterations:
                self.confirm_output()
                if self.index_input:
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
    secret_input = getpass.getpass(prompt="Enter hidden input: ").split("\n", 1)[0]
    sa = mnemo.expand_password(secret_input)
    GreatWall(mnemo, sa)


if __name__ == "__main__":
    main()
