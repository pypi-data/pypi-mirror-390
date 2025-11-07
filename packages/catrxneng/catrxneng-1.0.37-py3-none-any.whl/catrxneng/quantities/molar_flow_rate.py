from .quantity import Quantity
from catrxneng.utils import *
from numpy.typing import NDArray
import numpy as np
from typing import Any


class MolarFlowRate(Quantity):

    @property
    def mols(self) -> NDArray[np.number[Any]] | float:
        return self.si

    @mols.setter
    def mols(self, value):
        self.si = self.to_float(value)

    @property
    def molmin(self) -> NDArray[np.number[Any]] | float:
        return self.si * 60

    @molmin.setter
    def molmin(self, value):
        self.si = self.to_float(value / 60)

    @property
    def molh(self) -> NDArray[np.number[Any]] | float:
        return self.si * 3600

    @molh.setter
    def molh(self, value):
        self.si = self.to_float(value / 3600)

    @property
    def mmolh(self) -> NDArray[np.number[Any]] | float:
        return self.si * 3600 * 1000

    @mmolh.setter
    def mmolh(self, value):
        self.si = self.to_float(value / 3600 / 1000)

    @property
    def smLmin(self) -> NDArray[np.number[Any]] | float:
        return self.si * 60 * 22.4 * 1000

    @smLmin.setter
    def smLmin(self, value):
        self.si = self.to_float(value / 60 / 22.4 / 1000)

    @property
    def smLh(self) -> NDArray[np.number[Any]] | float:
        return self.si * 3600 * 22.4 * 1000

    @smLh.setter
    def smLh(self, value):
        self.si = self.to_float(value / 3600 / 22.4 / 1000)

    @property
    def nmLmin(self) -> NDArray[np.number[Any]] | float:
        return self.si * 60 * 24.05 * 1000

    @nmLmin.setter
    def nmLmin(self, value):
        self.si = self.to_float(value / 60 / 24.05 / 1000)
