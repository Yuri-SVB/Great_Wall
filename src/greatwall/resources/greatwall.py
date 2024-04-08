import random
from typing import Optional

from argon2 import low_level
from fs.memoryfs import MemoryFS
from cryptography.fernet import Fernet

from .knowledge.fractal import Fractal
from .knowledge.mnemonic.mnemonic import Mnemonic
from .knowledge.shaper import Shaper

class GreatWall:

    def __init__(self, tacit_knowledge_type: str = "Formosa"):
        self.tacit_knowledge_type = tacit_knowledge_type.lower()

        self.is_finished = False
        self.is_canceled = False
        self.is_initialized = False

        # Formosa
        self.mnemo: Optional[Mnemonic] = None

        # Fractal
        self.fractal = Fractal()

        # Shaper
        self.shaper = Shaper()

        # constants
        self.argon2salt = bytes("00000000000000000000000000000000", "utf-8")

        # topology of TLP derivation
        self.TLP_param: int = 0

        # topology of iterative derivation
        self.tree_depth: int = 0
        self.tree_arity: int = 0

        # diagram dummy init values
        self.sa0: bytes = bytes(00)
        self.sa1: bytes = self.sa0
        self.sa2: bytes = self.sa0
        self.sa3: bytes = self.sa0
        self.protocol_states: list[bytes] = [bytes(00)] * self.tree_depth

        # Initial state
        self.state: bytes = self.sa0
        self.nbytesform: int = 4
        self.current_level: int = 0
        self.shuffled_arity_indxes: list[int] = []

        # file system based in volatile memory (RAM)
        self.memory_file_system = MemoryFS()

        # cryptography for preventing leaks
        session_key = Fernet.generate_key()
        self.session_cipher = Fernet(session_key)

    def cancel_execution(self):
        self.is_canceled = True

    def set_themed_mnemo(self, theme: str) -> bool:
        try:
            self.mnemo = Mnemonic(theme)
            return True
        except ValueError:
            # TODO treat error
            return False

    def set_fractal_function_type(self, func_type: str) -> None:
        self.fractal.func_type = func_type

    def set_tlp(self, tlp: int):
        """Topology of TLP derivation.

        Args:
            tlp (int): parameter is the number of iterations of memory-hard hash,
                from 1 to 24*7*4*3.
        """
        self.TLP_param = tlp

    def set_depth(self, tree_depth: int):
        """Topology of iterative derivation.

        Args:
            tree_depth (int): is the number of iterative procedural memory
                choices needed, from 1 to 256.
        """
        self.tree_depth = tree_depth

    def set_arity(self, tree_arity: int):
        """Topology of iterative derivation.

        Args:
            tree_arity (int): is the number of options at each iteration,
                from 2 to 256
        """
        self.tree_arity = tree_arity

    def set_sa0(self, mnemonic: str) -> bool:
        self.is_canceled = False
        try:
            sa0 = mnemonic.split("\n", 1)[0]
            self.sa0 = bytes(self.mnemo.to_entropy(self.mnemo.expand_password(sa0)))
            self.init_protocol_values()
            return True
        except ValueError:
            # TODO treat error
            return False

    def init_protocol_values(self):
        # Diagram values
        self.sa1 = self.sa0
        self.sa2 = self.sa0
        self.sa3 = self.sa0
        self.protocol_states = [bytes.fromhex("00")] * self.tree_depth

    def init_state_hashes(self):
        self.state = self.sa0
        self.current_level = 0

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

    def update_with_long_hash(self):
        """
        Update self.level_hash with the hash of the previous self.level_hash
            taking presumably a long time.
        """
        for i in range(self.TLP_param):
            print("iteration #", i + 1, " of TLP:")
            self.state = low_level.hash_secret_raw(
                secret=self.state,
                salt=self.argon2salt,
                time_cost=8,
                memory_cost=1048576,
                parallelism=1,
                hash_len=128,
                type=low_level.Type.I,
            )

    def update_with_quick_hash(self):
        """
        Update self.level_hash with the hash of the previous self.level_hash
            taking presumably a quick time.
        """
        self.state = low_level.hash_secret_raw(
            secret=self.state,
            salt=self.argon2salt,
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

    def get_tacit_knowledge_param_from(
        self, branch_idx: int, tacit_knowledge_param: Optional[str] = None
    ):
        branch_idx_bytes = branch_idx.to_bytes(length=4, byteorder="big")

        # jth candidate L_(i+1), the state resulting from appending bytes of j
        # (here, branch_idx_bytes to current state L_i and hashing it)
        next_state_candidate = low_level.hash_secret_raw(
            secret=self.state + branch_idx_bytes,
            salt=self.argon2salt,
            time_cost=32,
            memory_cost=1024,
            parallelism=1,
            hash_len=128,
            type=low_level.Type.I,
        )

        if tacit_knowledge_param is not None:
            tacit_knowledge_param_bytes = tacit_knowledge_param.encode(encoding="utf-8")
            next_state_candidate = low_level.hash_secret_raw(
                secret=next_state_candidate + tacit_knowledge_param_bytes,
                salt=self.argon2salt,
                time_cost=32,
                memory_cost=1024,
                parallelism=1,
                hash_len=128,
                type=low_level.Type.I,
            )

        return next_state_candidate[0 : self.nbytesform]

    def get_fractal_query(self) -> list:
        self._shuffle_arity_indxes()
        shuffled_fractals = [
            self.fractal.update(
                func_type=self.fractal.func_type,
                real_p=self.fractal.get_valid_real_p_from(
                    self.get_tacit_knowledge_param_from(arity_idx, "real_p")
                ),
                imag_p=self.fractal.get_valid_imag_p_from(
                    self.get_tacit_knowledge_param_from(arity_idx, "imag_p")
                ),
            )
            for arity_idx in self.shuffled_arity_indxes
        ]
        listr = f"Choose 1, ..., {self.tree_arity} for level {self.current_level}"
        listr += f"{'' if not self.current_level else ', choose 0 to go back'}\n"
        shuffled_fractals = [listr] + shuffled_fractals
        return shuffled_fractals

    def get_li_str_query(self) -> str:
        self._shuffle_arity_indxes()
        shuffled_sentences = [
            self.mnemo.to_mnemonic(self.get_tacit_knowledge_param_from(arity_idx))
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
                self.get_tacit_knowledge_param_from(arity_idx)
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
        if chosen_input:
            self.protocol_states[self.current_level] = self.state
            self.state += bytes(self.shuffled_arity_indxes[chosen_input - 1])
            self.update_with_quick_hash()
            self.current_level += 1
        else:
            self.return_level()

    def return_level(self):
        if not self.current_level:
            return
        if self.is_finished:
            self.is_finished = False
        self.current_level -= 1
        self.state = self.protocol_states[self.current_level]

    def memory_file_system_data_load(self, name):

        try:
            virtual_file = self.memory_file_system.openbin(name, 'r')
            data = virtual_file.read()
            data = self.session_cipher.decrypt(data)
            return data
        except Exception:
            return None

    def memory_file_system_data_name(self, key, extension):

        name = f'{ key }{ extension }'
        return name

    def memory_file_system_data_save(self, name, data):

        data = self.session_cipher.encrypt(data)

        virtual_file = self.memory_file_system.openbin(name, 'w')
        virtual_file.write(data)
        virtual_file.close()
