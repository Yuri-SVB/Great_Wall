import random
from typing import Optional

from argon2 import low_level

from .helpers.utils import (
    DerivationPath,
    FormosaTacitKnowledgeParam,
    FractalTacitKnowledgeParam,
    ShapeTacitKnowledgeParam,
)
from .knowledge.fractal import Fractal
from .knowledge.mnemonic.mnemonic import Mnemonic
from .knowledge.shaper import Shaper


class GreatWall:
    ARGON2_SALT: bytes = bytes("00000000000000000000000000000000", "utf-8")
    NUM_BYTES_FORM: int = 4

    def __init__(self):
        self.is_finished: bool = False
        self.is_canceled: bool = False
        self.is_initialized: bool = False

        self._derivation_path: DerivationPath = DerivationPath()
        self._saved_states: dict = {}
        self._saved_fractals = {}

        # Palettes
        self.mnemo: Optional[Mnemonic] = None
        self.fractal: Optional[Fractal] = Fractal()
        self.shaper: Optional[Shaper] = Shaper()

        # Initial derivation values
        self.tree_depth: int = 0
        self.tree_arity: int = 0
        self.tlp_param: int = 0

        # Dummy initialization of protocol values
        self.init_protocol_values()

    def init_protocol_values(self):
        self.sa0: bytes = bytes(00)
        self.sa1: bytes = self.sa0
        self.sa2: bytes = self.sa0
        self.sa3: bytes = self.sa0

        self.state: bytes = self.sa0

        self.current_level: int = 0
        self.shuffled_arity_indxes: list[int] = []

    def set_themed_mnemo(self, theme: str) -> bool:
        try:
            self.mnemo = Mnemonic(theme)
            return True
        except ValueError:
            # TODO treat error
            return False

    def set_fractal_function_type(self, func_type: str) -> None:
        """Set the type of chosen fractal set."""
        self.fractal.func_type = func_type

    def set_tlp_param(self, iter_num: int):
        """Set the Time-Lock Puzzle param for derivation.

        Args:
            iter_num (int): The number of iterations of memory-hard hash,
                from 1 to 24*7*4*3.
        """
        self.tlp_param = iter_num

    def set_depth(self, tree_depth: int):
        """Set the number of needed choices of iteration of procedural memory.

        This method represents the depth of the tree that represents the
        topology of derivation.

        Args:
            tree_depth (int): is the number of iterative procedural memory
                choices needed, from 1 to 256.
        """
        self.tree_depth = tree_depth

    def set_arity(self, tree_arity: int):
        """Set the number of options at each iteration of derivation.

        This method represents the arity of the tree that represents the
        topology of derivation.

        Args:
            tree_arity (int): is the number of options at each iteration,
                from 2 to 256
        """
        self.tree_arity = tree_arity

    def set_sa0(self, mnemonic: str) -> bool:
        self.is_canceled = False
        try:
            self.init_protocol_values()
            self.sa0 = bytes(
                self.mnemo.to_entropy(
                    self.mnemo.expand_password(mnemonic.split("\n", 1)[0])
                )
            )
            return True
        except ValueError:
            # TODO treat error
            return False

    def init_state_hashes(self):
        self.state = self.sa0
        self.current_level = 0

        self._derivation_path = DerivationPath()
        self._saved_states = {}
        self._saved_fractals = {}

        # Actual work
        self.time_intensive_derivation()
        self.is_initialized = True

    def time_intensive_derivation(self):
        print("Initializing SA0")
        self.state = self.sa0
        if self.is_canceled:
            print("Task canceled")
            return  # Exit the task if canceled
        print("Deriving SA0 -> SA1")
        self.update_with_quick_hash()
        self.sa1 = self.state
        if self.is_canceled:
            print("Task canceled")
            return  # Exit the task if canceled
        print("Deriving SA1 -> SA2")
        self.update_with_long_hash()
        self.sa2 = self.state
        self.state = self.sa0 + self.state
        if self.is_canceled:
            print("Task canceled")
            return  # Exit the task if canceled
        print("Deriving SA2 -> SA3")
        self.update_with_quick_hash()
        self.sa3 = self.state

        self._saved_states[self._derivation_path.copy()] = self.state

    def update_with_long_hash(self):
        """Update the state with the its hash taking presumably a long time."""
        for i in range(self.tlp_param):
            print("iteration #", i + 1, " of TLP:")
            self.state = low_level.hash_secret_raw(
                secret=self.state,
                salt=self.ARGON2_SALT,
                time_cost=8,
                memory_cost=1048576,
                parallelism=1,
                hash_len=128,
                type=low_level.Type.I,
            )

    def update_with_quick_hash(self):
        """Update the state with the its hash taking presumably a quick time."""
        self.state = low_level.hash_secret_raw(
            secret=self.state,
            salt=self.ARGON2_SALT,
            time_cost=32,
            memory_cost=1024,
            parallelism=1,
            hash_len=128,
            type=low_level.Type.I,
        )

    def _shuffle_arity_indxes(self):
        """Shuffles the indexes in range `tree_arity` attribute."""
        self.shuffled_arity_indxes = [arity_idx for arity_idx in range(self.tree_arity)]
        random.shuffle(self.shuffled_arity_indxes)

    def get_fractal_query(self) -> list:
        if self._derivation_path in self._saved_fractals:
            return self._saved_fractals[self._derivation_path]
        else:
            self._shuffle_arity_indxes()
            shuffled_fractals = [
                self.fractal.update(
                    func_type=self.fractal.func_type,
                    real_p=FractalTacitKnowledgeParam(
                        self.state,
                        branch_idx=arity_idx.to_bytes(length=4, byteorder="big"),
                        real_p="real_p".encode(encoding="utf-8"),
                    ).get_value(),
                    imag_p=FractalTacitKnowledgeParam(
                        self.state,
                        branch_idx=arity_idx.to_bytes(length=4, byteorder="big"),
                        imag_p="imag_p".encode(encoding="utf-8"),
                    ).get_value(),
                )
                for arity_idx in self.shuffled_arity_indxes
            ]
            listr = f"Choose 1, ..., {self.tree_arity} for level {self.current_level}"
            listr += f"{'' if not self.current_level else ', choose 0 to go back'}\n"
            shuffled_fractals = [listr] + shuffled_fractals
            self._saved_fractals[self._derivation_path.copy()] = shuffled_fractals
            return shuffled_fractals

    def get_li_str_query(self) -> str:
        self._shuffle_arity_indxes()
        shuffled_sentences = [
            self.mnemo.to_mnemonic(
                FormosaTacitKnowledgeParam(
                    self.state,
                    branch_idx=arity_idx.to_bytes(length=4, byteorder="big"),
                ).get_value()
            )
            for arity_idx in self.shuffled_arity_indxes
        ]
        listr = f"Choose 1, ..., {self.tree_arity} for level {self.current_level}"
        listr += f"{'' if not self.current_level else ', choose 0 to go back'}\n"
        for i in range(len(shuffled_sentences)):
            listr += f"{shuffled_sentences[i]}\n"
        return listr

    def get_shape_query(self) -> list:
        self._shuffle_arity_indxes()
        shuffled_shapes = [
            self.shaper.draw_regular_shape(
                ShapeTacitKnowledgeParam(
                    self.state,
                    branch_idx=arity_idx.to_bytes(length=4, byteorder="big"),
                ).get_value()
            )
            for arity_idx in self.shuffled_arity_indxes
        ]
        listr = f"Choose 1, ..., {self.tree_arity} for level {self.current_level}"
        listr += f"{'' if not self.current_level else ', choose 0 to go back'}\n"
        shuffled_shapes = [listr] + shuffled_shapes
        return shuffled_shapes

    def finish_output(self):
        print("KA = \n", self.state.hex())
        self.is_finished = True
        return self.state

    def derive_from_user_choice(self, chosen_input: int):
        """Drive the protocol state depending on the user choice.

        Args:
            chosen_input (int): The index of the user choice; If this argument
                is 0, this method will go back one level. If this argument is
                greater than 0, this method will update the state depending on
                this choice.
        """
        if chosen_input > 0:
            self.current_level += 1
            self._derivation_path.append(chosen_input)

            if self._derivation_path in self._saved_states.keys():
                self.state = self._saved_states[self._derivation_path]
            else:
                self.state += bytes(self.shuffled_arity_indxes[chosen_input - 1])
                self.update_with_quick_hash()
                self._saved_states[self._derivation_path.copy()] = self.state
        else:
            self.return_level()

    def return_level(self):
        if not self.current_level:
            return
        if self.is_finished:
            self.is_finished = False

        self.current_level -= 1
        self._derivation_path.pop()

        self.state = self._saved_states[self._derivation_path]

    def cancel_execution(self):
        self.is_canceled = True
