import numpy as np
from numpy.typing import NDArray

import catrxneng.species as species
from .kinetic_model import KineticModel
import catrxneng.quantities as quant


class CompositeKineticModel(KineticModel):
    KINETIC_MODEL_CLASSES: list[type[KineticModel]]

    map_child_components_to_parent_components: list[list[int]]
    catalyst_fraction: NDArray

    kinetic_models: list[KineticModel]

    def __init__(
        self, catalyst_frac: NDArray, T: quant.Temperature | None = None, **kwargs
    ):
        super().__init__(T=T, **kwargs)
        self.catalyst_frac = np.asarray(catalyst_frac)
        self.kinetic_models = [KM(T=T, **kwargs) for KM in self.KINETIC_MODEL_CLASSES]
        self.map_child_components_to_parent_components = [
            [self.comp_list().index(comp) for comp in KM.comp_list()]
            for KM in self.KINETIC_MODEL_CLASSES
        ]

    @property
    def T(self):
        return self._T

    @T.setter
    def T(self, value):
        if value is not None and (not hasattr(self, "_T") or value.si != self._T.si):
            self._T = value
            try:
                for kinetic_model in self.kinetic_models:
                    kinetic_model.T = value
            except AttributeError:
                pass
