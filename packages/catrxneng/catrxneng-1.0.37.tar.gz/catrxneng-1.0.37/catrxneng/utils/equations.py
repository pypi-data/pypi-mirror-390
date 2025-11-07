import numpy as np
from typing import Any

import catrxneng.quantities as quant


def Hf_shomate(T, params):
    from catrxneng.quantities import Energy

    t = T.K / 1000
    dHf = (
        params["A"] * t
        + params["B"] * t**2 / 2
        + params["C"] * t**3 / 3
        + params["D"] * t**4 / 4
        - params["E"] / t
        + params["F"]
        # - params["H"]
    )  # kJ/mol
    return Energy(kJmol=dHf)


def S_shomate(T, params):
    from catrxneng.quantities import Entropy

    t = T.K / 1000
    S = (
        params["A"] * np.log(t)
        + params["B"] * t
        + params["C"] * t**2 / 2
        + params["D"] * t**3 / 3
        - params["E"] / (2 * t**2)
        + params["G"]
    )  # J/mol/K
    return Entropy(JmolK=S)


def Cp_shomate(T, params):
    from catrxneng.quantities import HeatCapacity

    t = T.K / 1000
    Cp = (
        params["A"]
        + params["B"] * t
        + params["C"] * t**2
        + params["D"] * t**3
        + params["E"] / (t**2)
    )
    return HeatCapacity(JmolK=Cp)


def vant_hoff_eqn(
    x_ref: Any, dH: quant.Energy, T: quant.Temperature, Tref: quant.Temperature
):
    return x_ref * np.exp(dH / quant.R * (1 / Tref - 1 / T))
