import scipy.integrate as integrate

from .reaction import Reaction
from ..quantities import *
from ..species import *


class RWGS(Reaction):
    COMPONENTS = {
        "co2": CO2,
        "h2": H2,
        "co": CO,
        "h2o": H2O,
        "inert": Ar,
    }
    STOICH_COEFF = Dimensionless(
        si=[-1.0, -1.0, 1.0, 1.0, 0.0], keys=list(COMPONENTS.keys())
    )
    DEFAULT_LIMITING_REACTANT = "co2"
    DH_RXN_298 = CO.HF_298_GAS + H2O.HF_298_LIQ - CO2.HF_298_GAS - H2.HF_298_GAS
    DH_RXN_298_GAS = CO.HF_298_GAS + H2O.HF_298_GAS - CO2.HF_298_GAS - H2.HF_298_GAS
    DS_RXN_298 = CO.S_298_GAS + H2O.S_298_LIQ - CO2.S_298_GAS - H2.S_298_GAS

    @staticmethod
    def dCp_1(T_K):
        T = Temperature(K=T_K)
        dCp = CO.Cp_gas(T) + H2O.Cp_liq(T) - CO2.Cp_gas(T) - H2.Cp_gas(T)
        return dCp.JmolK

    @staticmethod
    def dCp_2(T_K):
        T = Temperature(K=T_K)
        dCp = CO.Cp_gas(T) + H2O.Cp_gas(T) - CO2.Cp_gas(T) - H2.Cp_gas(T)
        return dCp.JmolK

    @classmethod
    def dH_rxn(cls, T):
        Tb_h2o = H2O.BOILING_TEMP.K
        if T.K < Tb_h2o:
            dHr = cls.DH_RXN_298.Jmol
            dHr += integrate.quad(cls.dCp_1, 298, T.K)[0]
            return Energy(Jmol=dHr)
        if T.K >= Tb_h2o:
            dHr = cls.DH_RXN_298.Jmol
            dHr += integrate.quad(cls.dCp_1, 298, Tb_h2o)[0]
            dHr += H2O.DH_VAP.Jmol
            dHr += integrate.quad(cls.dCp_2, Tb_h2o, T.K)[0]
            return Energy(Jmol=dHr)

    @classmethod
    def dS_rxn(cls, T):
        Tb_h2o = H2O.BOILING_TEMP.K
        integrand1 = lambda T_K: cls.dCp_1(T_K) / T_K
        integrand2 = lambda T_K: cls.dCp_2(T_K) / T_K
        if T.K < Tb_h2o:
            dSr = cls.DS_RXN_298.JmolK
            dSr += integrate.quad(integrand1, 298, T.K)[0]
            return Entropy(JmolK=dSr)
        if T.K >= Tb_h2o:
            dSr = cls.DS_RXN_298.JmolK
            dSr += integrate.quad(integrand1, 298, Tb_h2o)[0]
            dSr += H2O.DS_VAP.JmolK
            dSr += integrate.quad(integrand2, Tb_h2o, T.K)[0]
            return Entropy(JmolK=dSr)
