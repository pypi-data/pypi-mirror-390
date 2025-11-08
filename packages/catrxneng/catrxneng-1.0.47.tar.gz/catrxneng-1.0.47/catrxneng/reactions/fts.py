import numpy as np

from .reaction import Reaction
from ..quantities import *
from ..species import CO, H2, C2H4, H2O, Ar


class FTS(Reaction):
    COMPONENTS = {"CO": CO, "H2": H2, "C2H4": C2H4, "H2O": H2O, "inert": Ar}
    STOICH_COEFF = Dimensionless(
        si=[-2.0, -4.0, 1.0, 2.0, 0.0], keys=list(COMPONENTS.keys())
    )
    DEFAULT_LIMITING_REACTANT = "co"
