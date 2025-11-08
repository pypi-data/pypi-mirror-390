from typing import Any
from numpy.typing import NDArray
from .quantity import Quantity
from catrxneng.utils import *


class Pressure(Quantity):

    # def __init__(self, **kwargs):
    #     if len(kwargs.keys()) == 1 and kwargs.get("keys", None) is not None:
    #         si = {"si": np.zeros(len(kwargs["keys"]))}
    #         kwargs = {**si, **kwargs}
    #     super().__init__(**kwargs)

    @property
    def Pa(self):
        return self.si

    @Pa.setter
    def Pa(self, value):
        self.si = self.to_float(value)

    @property
    def bar(
        self,
    ) -> pd.Series | NDArray[np.number[Any]] | float:
        return self.si / 100000

    @bar.setter
    def bar(self, value):
        self.si = self.to_float(value) * 100000

    @property
    def kPa(self):
        return self.si / 1000

    @kPa.setter
    def kPa(self, value):
        self.si = self.to_float(value) * 1000

    @property
    def atm(self):
        return self.si / 101325

    @atm.setter
    def atm(self, value):
        self.si = self.to_float(value) * 101325

    @property
    def MPa(self):
        return self.si / 1000000

    @MPa.setter
    def MPa(self, value):
        self.si = self.to_float(value) * 1000000
