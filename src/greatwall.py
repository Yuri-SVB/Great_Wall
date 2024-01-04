import random
import argon2
from typing import Optional, Union
from src.mnemonic.mnemonic import Mnemonic
from Shaper import Shaper
# from user_interface import UserInterface


# class Shaper:
#     def __init__(self, size: int = 101):
#         self.size = size
#
#         # Create a new image with a black background
#         self.image = Image.new("RGB", (size, size), "black")
#         self.draw = ImageDraw.Draw(self.image)
#
#     @staticmethod
#     def get_first_digit(number: bytes):
#         bytes_1st_digit = int(str(number[0]))
#         integer_1st_digit = str(bytes_1st_digit)[0]
#         return int(integer_1st_digit)
#
#     def draw_regular_shape(self, sides: Union[int, bytes, bytearray] = 3):
#         if isinstance(sides, bytes) or isinstance(sides, bytearray):
#             # If sides is given as bytes it will get the int of the first digit with an offset of 2
#             sides = self.get_first_digit(sides)+2
#         size = self.size
#
#         # Calculate the coordinates for the polygon points
#         center_x, center_y = size // 2, size // 2
#
#         # Calculate the angle step in radians for each vertex
#         angle = 2*math.pi/sides
#
#         # Calculate the vertices
#         vertices = [(int(center_x * math.sin(angle * i)) + center_x,
#                      -int(center_y * math.cos(angle * i)) + center_y)
#                     for i in range(sides)
#                     ]
#
#         # Draw the polygon
#         self.draw.polygon(vertices, outline="white")
#         # Showing for debugging purpose
#         self.image.show()
#         filename = f"s{sides}-polygon"
#         print(filename)
#         self.image.save(filename+".png")
#         return self.image


class GreatWall:
    def __init__(self, query_type: str = "Formosa"):

        self.query_type = query_type.lower()

        # user interface
        # self.user_interface = UserInterface()
        self.user_chosen_input: int = 0

        self.is_finished = False
        self.is_canceled = False

        # Formosa
        self.mnemo: Optional[Mnemonic] = None
        self.nbytesform: int = 0

        # constants
        self.argon2salt = "00000000000000000000000000000000"

        # topology of TLP derivation
        self.TLP_param: int = 0

        # topology of iterative derivation
        self.tree_depth: int = 0
        self.tree_arity: int = 0

        # diagram values
        # self.sa0 = bytes(bytearray(32 // 8))
        self.sa0: bytes = bytes(00)
        self.sa1: bytes = self.sa0         # dummy initialization
        self.sa2: bytes = self.sa0         # dummy initialization
        self.sa3: bytes = self.sa0         # dummy initialization
        self.states: list[bytes] = [bytes.fromhex("00")]*self.tree_depth  # dummy initialization

        # Initial state
        self.state: bytes = self.sa0
        self.shuffled_bytes: bytes = self.sa0  # dummy initialization
        self.current_level: int = 0

    def cancel_execution(self):
        self.is_canceled = True

    def set_themed_mnemo(self, theme: str) -> bool:
        try:
            self.mnemo = Mnemonic(theme)
            self.nbytesform = 4 #if self.mnemo.is_bip39_theme else 2 #number of bytes in formosa sentence TODO soft code me
            return True
        except ValueError:
            # TODO treat error
            return False

    def set_tlp(self, tlp: int):
        # topology of TLP derivation,
        # tlp parameter is the number of iterations of memory-hard hash, from 1 to 24*7*4*3
        self.TLP_param = tlp

    def set_depth(self, tree_depth: int):
        # topology of iterative derivation,
        # tree depth is the number of iterative procedural memory choices needed, from 1 to 256
        self.tree_depth = tree_depth

    def set_arity(self, tree_arity: int):
        # topology of iterative derivation, tree arity is the number of options at each iteration, from 2 to 256
        self.tree_arity = tree_arity

    def set_sa0(self, mnemonic: str) -> bool:
        self.is_canceled = False
        try:
            sa0 = mnemonic.split("\n", 1)[0]
            self.sa0 = bytes(self.mnemo.to_entropy(self.mnemo.expand_password(sa0)))
            self.init_diagram_values()
            return True
        except ValueError:
            # TODO treat error
            return False

    def init_diagram_values(self):
        # Diagram values
        self.sa1 = self.sa0         # dummy initialization
        self.sa2 = self.sa0         # dummy initialization
        self.sa3 = self.sa0         # dummy initialization
        self.states = [bytes.fromhex("00")]*self.tree_depth  # dummy initialization

    def initialize_state_hashes(self):
        self.state = self.sa0
        self.shuffled_bytes = self.sa0  # dummy initialization
        self.current_level = 0

        # Actual work
        self.time_intensive_derivation()

    def time_intensive_derivation(self):
        # Calculating SA1 from SA0
        print('Initializing SA0')
        self.state = self.sa0
        if self.is_canceled:
            print("Task canceled")
            return  # Exit the task if canceled
        print('Deriving SA0 -> SA1')
        self.update_with_quick_hash()
        self.sa1 = self.state
        if self.is_canceled:
            print("Task canceled")
            return  # Exit the task if canceled
        print('Deriving SA1 -> SA2')
        self.update_with_long_hash()
        self.sa2 = self.state
        self.state = self.sa0 + self.state
        if self.is_canceled:
            print("Task canceled")
            return  # Exit the task if canceled
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
        # self.shuffled_bytes = [bytes(self.state[a * i:a * (i + 1)]) for i in range(self.tree_arity)]
        self.shuffled_bytes = [self.state[a * i:a * (i + 1)] for i in range(self.tree_arity)]
        random.shuffle(self.shuffled_bytes)

    def get_li_str_query(self) -> str:
        self.shuffle_bytes()
        shuffled_sentences = [self.mnemo.to_mnemonic(bytes_sentence) for bytes_sentence in self.shuffled_bytes]
        listr = "Choose 1, ..., %d for level %d".format(self.tree_arity, self.current_level)
        listr += "%s\n".format("" if not self.current_level else ", choose 0 to go back")
        for i in range(len(shuffled_sentences)):
            listr += str(i + 1) + ") " + shuffled_sentences[i] + "\n"
        return listr

    def get_shape_query(self) -> list:
        self.shuffle_bytes()
        shuffled_shapes = [Shaper().draw_regular_shape(bytes_sentence)
                           for bytes_sentence in self.shuffled_bytes]
        listr = "Choose 1, ..., %d for level %d".format(self.tree_arity, self.current_level)
        listr += "%s\n".format("" if not self.current_level else ", choose 0 to go back")
        shuffled_shapes = [listr] + shuffled_shapes
        return shuffled_shapes

    def finish_output(self):
        print("KA = \n", self.state.hex())
        self.is_finished = True
        return self.state

    def derive_from_user_choice(self, chosen_input: int):
        if chosen_input:
            self.states[self.current_level] = self.state
            self.state += bytes(self.shuffled_bytes[chosen_input - 1])
            self.update_with_quick_hash()
            self.current_level += 1
            self.user_chosen_input = chosen_input
        else:
            self.return_level()

    def return_level(self):
        if not self.current_level:
            return
        self.current_level -= 1
        self.state = self.states[self.current_level]

    # def finish_derivation(self):
    #     if self.current_level >= self.tree_depth:
    #         self.finish_output()
    #         self.user_interface.prompt_integer("Enter 1 to terminate derivation and 0 to go back:", 0, 1)
    #         if self.user_interface.index_input_int == 1:
    #             self.is_finished = True
    #         else:
    #             self.current_level -= 1
    #             self.state = self.states[self.current_level]
    #
    #
    #
    # def _user_dependent_derivation(self):
    #     while not self.is_finished:
    #         # Ask user to choose between a set of sentences generated from the shuffled level_hash bytes
    #         listr = self.get_li_str_query()
    #         self.user_interface.prompt_integer(listr, 0 if self.current_level != 0 else 1, self.tree_arity)
    #         if self.user_interface.index_input_int != 0:
    #             self.user_interface.user_chosen_input = self.shuffled_bytes[self.user_interface.index_input_int - 1]
    #             self.states[self.current_level] = self.state
    #             self.state += self.user_interface.user_chosen_input
    #             self.update_with_quick_hash()
    #             self.current_level += 1
    #         else:
    #             self.current_level -= 1
    #             self.state = self.states[self.current_level]
    #         if self.current_level >= self.tree_depth:
    #             self.finish_output()
    #             self.user_interface.prompt_integer("Enter 1 to terminate derivation and 0 to go back:", 0, 1)
    #             if self.user_interface.index_input_int == 1:
    #                 self.is_finished = True
    #             else:
    #                 self.current_level -= 1
    #                 self.state = self.states[self.current_level]
    #     # self.finish_output()


def main():
    # GreatWall()
    for i in range(16):
        Shaper(3).draw_regular_shape(i+3)


if __name__ == "__main__":
    main()
