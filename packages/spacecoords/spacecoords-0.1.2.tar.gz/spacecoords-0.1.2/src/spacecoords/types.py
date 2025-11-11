"""
This module contains convenient type information so that typing can be precise
but not too verbose in the code itself.
"""
from typing import TypeVar
import numpy.typing as npt

T = TypeVar("T")

NDArray_N = npt.NDArray
"(n,) shaped ndarray"

NDArray_3 = npt.NDArray
"(3,) shaped ndarray"

NDArray_6 = npt.NDArray
"(6,) shaped ndarray"

NDArray_3xN = npt.NDArray
"(3,n) shaped ndarray"

NDArray_6xN = npt.NDArray
"(6,n) shaped ndarray"

NDArray_NxN = npt.NDArray
"(n,n) shaped ndarray"

NDArray_3x3 = npt.NDArray
"(3,3) shaped ndarray"

NDArray_2x2 = npt.NDArray
"(2,2) shaped ndarray"

NDArray_3x3xN = npt.NDArray
"(3,3,n) shaped ndarray"
