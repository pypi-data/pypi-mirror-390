from typing import TYPE_CHECKING

from .quantity import Quantity
from catrxneng.utils import *

if TYPE_CHECKING:
    from ..species import GasMixture


class SpaceTime(Quantity):

    def __init__(self, gas_mixture: "GasMixture" = None, **kwargs):
        self.gas_mixture = gas_mixture
        super().__init__(**kwargs)

    @property
    def skgcatmol(self):
        return self.si

    @skgcatmol.setter
    def skgcatmol(self, value):
        self.si = self.to_float(value)

    @property
    def hgcatmol(self):
        return self.si / 3600 * 1000

    @hgcatmol.setter
    def hgcatmol(self, value):
        self.si = self.to_float(value) * 3600 / 1000

    @property
    def hgcatsmL(self):
        return self.si / 3600 / 22.4

    @hgcatsmL.setter
    def hgcatsmL(self, value):
        self.si = self.to_float(value) * 3600 * 22.4

    @property
    def hr(self):
        try:
            return self.si * 1000 / self.gas_mixture.avg_mol_weight / 3600
        except TypeError:
            raise AttributeError("Spacetime has no gas mixture assigned.")

    @hr.setter
    def hr(self, value):
        try:
            self.si = value / 1000 * self.gas_mixture.avg_mol_weight * 3600
        except TypeError:
            raise AttributeError("Spacetime has no gas mixture assigned.")

    @property
    def sec(self):
        try:
            return self.si * 1000 / self.gas_mixture.avg_mol_weight
        except TypeError:
            raise AttributeError("Spacetime has no gas mixture assigned.")

    @sec.setter
    def sec(self, value):
        try:
            self.si = value / 1000 * self.gas_mixture.avg_mol_weight
        except TypeError:
            raise AttributeError("Spacetime has no gas mixture assigned.")
