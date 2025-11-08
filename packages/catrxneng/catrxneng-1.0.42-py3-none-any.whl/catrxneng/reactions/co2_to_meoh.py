import scipy.integrate as integrate

from .reaction import Reaction
from .. import species
from .. import quantities as quant


class Co2ToMeoh(Reaction):
    EQUATION = "CO₂ + 3H₂ ⇌ CH₃OH + H₂O"
    REACTANTS = {
        "co2": species.CO2,
        "h2": species.H2,
    }
    PRODUCTS = {
        "ch3oh": species.CH3OH,
        "h2o": species.H2O,
    }
    COMPONENTS = {**REACTANTS, **PRODUCTS, "inert": species.Inert}
    STOICH_COEFF = quant.Dimensionless(
        si=[-1.0, -3.0, 1.0, 1.0, 0.0], keys=list(COMPONENTS.keys())
    )
    DEFAULT_LIMITING_REACTANT = "co2"
    DH_RXN_298 = (
        species.CH3OH.HF_298_LIQ
        + species.H2O.HF_298_LIQ
        - species.CO2.HF_298_GAS
        - 3 * species.H2.HF_298_GAS
    )
    DS_RXN_298 = (
        species.CH3OH.S_298_LIQ
        + species.H2O.S_298_LIQ
        - species.CO2.S_298_GAS
        - 3 * species.H2.S_298_GAS
    )

    @staticmethod
    def dCp_1(T_K):
        T = quant.Temperature(K=T_K)
        dCp = (
            species.CH3OH.Cp_liq(T)
            + species.H2O.Cp_liq(T)
            - species.CO2.Cp_gas(T)
            - 3 * species.H2.Cp_gas(T)
        )
        return dCp.JmolK

    @staticmethod
    def dCp_2(T_K):
        T = quant.Temperature(K=T_K)
        dCp = (
            species.CH3OH.Cp_gas(T)
            + species.H2O.Cp_liq(T)
            - species.CO2.Cp_gas(T)
            - 3 * species.H2.Cp_gas(T)
        )
        return dCp.JmolK

    @staticmethod
    def dCp_3(T_K):
        T = quant.Temperature(K=T_K)
        dCp = (
            species.CH3OH.Cp_gas(T)
            + species.H2O.Cp_gas(T)
            - species.CO2.Cp_gas(T)
            - 3 * species.H2.Cp_gas(T)
        )
        return dCp.JmolK

    @classmethod
    def dH_rxn(cls, T):
        Tb_ch3oh = species.CH3OH.BOILING_TEMP.K
        Tb_h2o = species.H2O.BOILING_TEMP.K
        if T.K < Tb_ch3oh:
            dHr = cls.DH_RXN_298.Jmol
            dHr += integrate.quad(cls.dCp_1, 298, T.K)[0]
            return quant.Energy(Jmol=dHr)
        if Tb_ch3oh <= T.K < Tb_h2o:
            dHr = cls.DH_RXN_298.Jmol
            dHr += integrate.quad(cls.dCp_1, 298, Tb_ch3oh)[0]
            dHr += species.CH3OH.DH_VAP.Jmol
            dHr += integrate.quad(cls.dCp_2, Tb_ch3oh, T.K)[0]
            return quant.Energy(Jmol=dHr)
        if T.K >= Tb_h2o:
            dHr = cls.DH_RXN_298.Jmol
            dHr += integrate.quad(cls.dCp_1, 298, Tb_ch3oh)[0]
            dHr += species.CH3OH.DH_VAP.Jmol
            dHr += integrate.quad(cls.dCp_2, Tb_ch3oh, Tb_h2o)[0]
            dHr += species.H2O.DH_VAP.Jmol
            dHr += integrate.quad(cls.dCp_3, Tb_h2o, T.K)[0]
            return quant.Energy(Jmol=dHr)

    @classmethod
    def dS_rxn(cls, T):
        Tb_ch3oh = species.CH3OH.BOILING_TEMP.K
        Tb_h2o = species.H2O.BOILING_TEMP.K
        integrand1 = lambda T_K: cls.dCp_1(T_K) / T_K
        integrand2 = lambda T_K: cls.dCp_2(T_K) / T_K
        integrand3 = lambda T_K: cls.dCp_3(T_K) / T_K
        if T.K < Tb_ch3oh:
            dSr = cls.DS_RXN_298.JmolK
            dSr += integrate.quad(integrand1, 298, T.K)[0]
            return quant.Entropy(JmolK=dSr)
        if Tb_ch3oh <= T.K < Tb_h2o:
            dSr = cls.DS_RXN_298.JmolK
            dSr += integrate.quad(integrand1, 298, Tb_ch3oh)[0]
            dSr += species.CH3OH.DS_VAP.JmolK
            dSr += integrate.quad(integrand2, Tb_ch3oh, T.K)[0]
            return quant.Entropy(JmolK=dSr)
        if T.K >= Tb_h2o:
            dSr = cls.DS_RXN_298.JmolK
            dSr += integrate.quad(integrand1, 298, Tb_ch3oh)[0]
            dSr += species.CH3OH.DS_VAP.JmolK
            dSr += integrate.quad(integrand2, Tb_ch3oh, Tb_h2o)[0]
            dSr += species.H2O.DS_VAP.JmolK
            dSr += integrate.quad(integrand3, Tb_h2o, T.K)[0]
            return quant.Entropy(JmolK=dSr)
