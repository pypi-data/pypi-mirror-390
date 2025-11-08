import pickle

import numpy as np
from typing_extensions import Self


class DataObject:
    __slots__ = ["_data"]

    def __init__(self, data: np.ndarray, frozen: bool) -> None:
        self._data = data
        self._data.flags.writeable = not frozen

    def __getstate__(self) -> bytes:
        return self._data.dumps()

    def __setstate__(self, data: bytes) -> None:
        self._data = pickle.loads(data)

    def copy(self) -> Self:
        return self.from_data(self._data.copy())

    def __deepcopy__(self, memo: dict) -> Self:
        return self.copy()

    @classmethod
    def from_data(cls, data: np.ndarray) -> Self:
        res = cls.__new__(cls)
        res.data = data
        return res

    @property
    def data(self) -> np.ndarray:
        return self._data

    @data.setter
    def data(self, newval: np.ndarray) -> None:
        self._data = newval

    @property
    def frozen(self) -> bool:
        return not self._data.flags.writeable

    @frozen.setter
    def frozen(self, val: bool) -> None:
        self._data.flags.writeable = not val
