from typing import cast

import numpy as np
from sympy import fwht

from classiq.interface.exceptions import ClassiqValueError

from classiq.qmod.builtins.functions import CX, RY
from classiq.qmod.builtins.operations import (
    bind,
    skip_control,
)
from classiq.qmod.qfunc import qfunc
from classiq.qmod.qmod_variable import QArray, QBit, QNum


def _get_graycode(size: int, i: int) -> int:
    if i == 2**size:
        return _get_graycode(size, 0)
    return i ^ (i >> 1)


def _get_graycode_angles_wh(size: int, angles: list[float]) -> list[float]:
    transformed_angles = fwht(np.array(angles) / 2**size)
    return [transformed_angles[_get_graycode(size, j)] for j in range(2**size)]


def _get_graycode_ctrls(size: int) -> list[int]:
    return [
        (_get_graycode(size, i) ^ _get_graycode(size, i + 1)).bit_length() - 1
        for i in range(2**size)
    ]


@qfunc
def assign_amplitude_table(
    amplitudes: list[float], index: QNum, indicator: QBit
) -> None:
    """
    [Qmod Classiq-library function]

    Load a specified list of real amplitudes into a quantum variable using an extra indicator qubit:
    \\( |i\\rangle|0\\rangle \\rightarrow a(i),\\ |i\\rangle|1\\rangle + \\sqrt{1 - a(i)^2},\\ |x\\rangle|0\\rangle \\).
    Here, \\(a(i)\\) is the i-th amplitude, determined by the QNum when the index is in state \\(i\\).
    A list extracted from a given classical function \\(f(x)\\), with indexing according to a given QNum, can be obtained via the utility SDK function `lookup_table`.
    This function expects the indicator qubit to be initialized to \\(|0\\rangle\\).

    Args:
        amplitudes: Real values for the amplitudes
        index: The quantum variable used for amplitude indexing
        indicator: The quantum indicator qubit

    Example:
        ```python
        from classiq import *


        @qfunc
        def main(x: Output[QNum[5, UNSIGNED, 5]], ind: Output[QBit]) -> None:
            allocate(x)
            hadamard_transform(x)
            allocate(ind)

            assign_amplitude_table(lookup_table(lambda x: x**2, x), x, ind)
        ```
    """
    if len(amplitudes) != 2**index.size:
        raise ClassiqValueError(
            f"The number of amplitudes must be 2**index.size={2 ** index.size}, got "
            f"{len(amplitudes)}"
        )

    angles_to_load = cast(list[float], 2 * np.arcsin(amplitudes))
    size = cast(int, index.size)
    transformed_angles = _get_graycode_angles_wh(size, angles_to_load)
    controllers = _get_graycode_ctrls(size)

    qba: QArray = QArray()
    bind(index, qba)
    for k in range(2**size):
        RY(transformed_angles[k], indicator)
        skip_control(
            lambda k=k: CX(qba[controllers[k]], indicator)  # type:ignore[misc]
        )
    bind(qba, index)
