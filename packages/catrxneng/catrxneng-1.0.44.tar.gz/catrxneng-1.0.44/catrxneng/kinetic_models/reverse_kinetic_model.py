import numpy as np
from .kinetic_model import KineticModel
from catrxneng.reactions import Reaction
from catrxneng.species import Species
from .. import quantities as quant


class ReverseKineticModel(KineticModel):
    FORWARD_MODEL: type[KineticModel]
    COMPONENTS: dict[str, Species]
    REACTIONS: dict[str, Reaction]
    LIMITING_REACTANT: str
    C_ATOMS: np.ndarray

    forward_model: KineticModel

    def __init__(self, T: quant.Temperature = None, **forward_model_kwargs):
        self.forward_model = self.FORWARD_MODEL(T=T, **forward_model_kwargs)
        super().__init__(T)

    def compute_temp_dependent_constants(self) -> None:
        self.forward_model.compute_temp_dependent_constants()

    def calculate_rates(self, p: quant.Pressure) -> quant.ReactionRate:
        return -1.0 * self.forward_model.calculate_rates(p)

    def rate_equations(self, p_array):
        return -1.0 * self.forward_model.rate_equations(p_array)
