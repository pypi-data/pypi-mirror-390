import numpy as np

from ..kinetic_model import KineticModel
import catrxneng.utils.equations as eqn
from catrxneng.reactions import RWGS, Co2ToMeoh
import catrxneng.species as species
import catrxneng.quantities as quant


class Ghosh2021NoH2InDenom(KineticModel):
    LIMITING_REACTANT = "co2"
    T_REF = quant.Temperature(C=300)
    COMPONENTS = {
        "co2": species.CO2,
        "h2": species.H2,
        "ch3oh": species.CH3OH,
        "h2o": species.H2O,
        "co": species.CO,
        "inert": species.Inert,
    }
    C_ATOMS = np.array([comp.C_ATOMS for comp in COMPONENTS.values()])
    REACTIONS = {
        "co2_to_meoh": Co2ToMeoh,
        "rwgs": RWGS,
    }
    ORDER = np.array([2.0, 1.5, 1.0])
    STOICH_COEFF = np.array(
        [
            [-1, -3, 1, 1, 0, 0],
            [-1, -1, 0, 1, 1, 0],
        ]
    )
    K_REF = np.array([6.9e-4, 1.8e-3])
    E_A = np.array([35.7, 54.5])

    def __init__(self, site_model="single", T=None, kref=None, Ea=None):
        self.site_model = site_model
        self.kref = kref
        if self.kref is None:
            self.kref = self.K_REF
        self.Ea = Ea
        if self.Ea is None:
            self.Ea = self.E_A
        super().__init__(T)

    def compute_temp_dependent_constants(self):
        self.K_h2 = eqn.vant_hoff_eqn(
            0.76, quant.Energy(kJmol=-12.5), self.T, self.T_REF
        ).si
        self.K_co2 = eqn.vant_hoff_eqn(
            0.79, quant.Energy(kJmol=-25.9), self.T, self.T_REF
        ).si
        self.K_co2_to_meoh = Co2ToMeoh().Keq(self.T)
        self.K_rwgs = RWGS().Keq(self.T)
        self.Keq = np.array([self.K_co2_to_meoh, self.K_rwgs])
        self.k = np.array(
            [
                quant.RateConstant(
                    molskgcatbar=kref,
                    Ea=quant.Energy(kJmol=Ea),
                    Tref=self.T_REF,
                    order=order,
                )(self.T).molhgcatbar
                for kref, Ea, order in zip(self.kref, self.Ea, self.ORDER)
            ]
        )

    def calculate_rates(self, p: quant.Pressure) -> quant.ReactionRate:
        return quant.ReactionRate(
            molhgcat=self.rate_equations(p_array=p.bar), keys=self.comp_list()
        )

    def rate_equations(self, p_array: np.ndarray) -> np.array:
        """
        Calculate reaction rates from partial pressures.

        Pressure in bar
        Rates in mol/h/gcat

        Parameters
        ----------
        p_array : array-like
            Partial pressures. Can be:
            - 1D array of shape (7,) for a single point
            - 2D array of shape (7, n) for n points

        Returns
        -------
        rates : ndarray
            Reaction rates with the same shape as input.
            - 1D array of shape (7,) if input is 1D
            - 2D array of shape (7, n) if input is 2D
        """
        p_co2 = p_array[0]  # co2
        p_h2 = p_array[1]  # h2
        p_ch3oh = p_array[2]  # ch3oh
        p_h2o = p_array[3]  # h2o
        p_co = p_array[4]  # co

        base = 1 + self.K_co2 * p_co2 + np.sqrt(self.K_h2 * p_h2)
        inhib = base * base

        # Reaction 1: CO2 + 3H2 -> CH3OH + H2O (CO2-to-MeOH)
        fwd = p_co2 * p_h2
        rev = p_ch3oh * p_h2o / self.K_co2_to_meoh
        r1 = self.k[0] * (fwd - rev) / inhib

        # Reaction 2: CO2 + H2 -> CO + H2O (RWGS)
        fwd = p_co2 * np.sqrt(p_h2)
        rev = p_co * p_h2o / self.K_rwgs
        r2 = self.k[1] * (fwd - rev) / inhib

        return np.array(
            [
                -r1 - r2,  # co2
                -3 * r1 - r2,  # h2
                r1,  # ch3oh
                r1 + r2,  # h2o
                r2,  # co
                0.0 * r1,  # inert
            ]
        )
