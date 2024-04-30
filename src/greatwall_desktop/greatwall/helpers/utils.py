from typing import Optional

from argon2 import low_level


class DerivationPath(list):
    """A representation of the tree-like derivation key."""

    def copy(self):
        """Create a shallow copy of the path"""
        new_instance = DerivationPath(self)
        return new_instance

    def __contains__(self, item):
        return item in " -> ".join(str(node) for node in self)

    def __eq__(self, other):
        return " -> ".join(str(node) for node in self) == other

    def __hash__(self):
        return hash(" -> ".join(str(node) for node in self))

    def __str__(self):
        if len(self) > 1:
            return " -> ".join(str(node) for node in self)
        elif len(self) == 1:
            return "".join(str(node) for node in self)
        else:
            return ""


class TacitKnowledgeParam:
    """A representation of the tacit knowledge params."""

    ARGON2_SALT: bytes = bytes("00000000000000000000000000000000", "utf-8")
    NUM_BYTES_FORM: int = 4

    def __init__(self, state: bytes, **kwargs) -> None:
        self.state: bytes = state
        self.adjustment_params: dict[str, bytes] = kwargs

        self._value: Optional[bytes] = None

    def get_value(self):
        """Get the value of the param."""
        self._value = self._compute_value()

        return self._value

    def _compute_value(self):
        """Get a valid tacit knowledge value from provided adjustment params."""

        # jth candidate L_(i+1), the state resulting from appending bytes of j
        # (here, branch_idx_bytes to current state L_i and hashing it)
        next_state_candidate = self.state
        for param in self.adjustment_params:
            tacit_knowledge_param_bytes = self.adjustment_params[param]

            next_state_candidate = low_level.hash_secret_raw(
                secret=next_state_candidate + tacit_knowledge_param_bytes,
                salt=self.ARGON2_SALT,
                time_cost=32,
                memory_cost=1024,
                parallelism=1,
                hash_len=128,
                type=low_level.Type.I,
            )

        return next_state_candidate[0 : self.NUM_BYTES_FORM]


class FractalTacitKnowledgeParam(TacitKnowledgeParam):
    """A representation of the fractal tacit knowledge param."""

    def _compute_real_p_value(self, value: bytes):
        # NOTE: We inverting the order of digits by operation [::-1] on string,
        # to minimize Benford's law bias.
        real_p = "2." + str(int.from_bytes(value, "big"))[::-1]
        return float(real_p)

    def _compute_imag_p_value(self, value: bytes):
        # NOTE: We inverting the order of digits by operation [::-1] on string,
        # to minimize Benford's law bias.
        imag_p = "0." + str(int.from_bytes(value, "big"))[::-1]
        return float(imag_p)

    def _compute_value(self):
        if "real_p" in self.adjustment_params.keys():
            return self._compute_real_p_value(super()._compute_value())
        elif "imag_p" in self.adjustment_params.keys():
            return self._compute_imag_p_value(super()._compute_value())
        else:
            return super()._compute_value()


class FormosaTacitKnowledgeParam(TacitKnowledgeParam):
    """A representation of the formosa tacit knowledge param."""

    def _compute_value(self):
        return super()._compute_value()


class ShapeTacitKnowledgeParam(TacitKnowledgeParam):
    """A representation of the shape tacit knowledge param."""

    def _compute_value(self):
        return super()._compute_value()
