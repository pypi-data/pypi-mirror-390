import numpy as np
from numpy.typing import NDArray
from scipy.optimize import least_squares

import catrxneng as cat
import catrxneng.quantities as quant
from catrxneng.species import Species


class KineticModel:
    LIMITING_REACTANT: str
    T_REF: quant.Temperature
    REACTANTS: dict[str, type[Species] | Species]
    PRODUCTS: dict[str, type[Species] | Species]
    COMPONENTS: dict[str, type[Species] | Species]
    REACTIONS: dict[str, type[cat.reactions.Reaction]]
    STOICH_COEFF: NDArray
    ORDER: NDArray
    C_ATOMS: NDArray

    def __init__(self, T):
        self.T = T
        self.comp_idx = {comp: i for i, comp in enumerate(self.COMPONENTS)}
        self.rxn_idx = {rxn: i for i, rxn in enumerate(self.REACTIONS)}
        self.fugacity_coeff = np.ones(len(self.COMPONENTS))

    def compute_temp_dependent_constants(self):
        raise NotImplementedError(
            "Child class must implement compute_temp_dependent_constants."
        )

    @classmethod
    def comp_list(cls):
        return list(cls.COMPONENTS.keys())

    @property
    def T(self):
        return self._T

    @T.setter
    def T(self, value):
        if value is not None and (not hasattr(self, "_T") or value.si != self._T.si):
            self._T = value
            self.compute_temp_dependent_constants()

    def _compute_final_molfrac(self, initial_moles, extent):
        delta_moles = self.STOICH_COEFF.T @ extent
        final_moles = initial_moles + delta_moles
        total_final_moles = np.sum(final_moles)
        molfrac = final_moles / total_final_moles
        return molfrac, delta_moles

    def _compute_extent_bounds(self, initial_moles):
        lower_bounds = [0] * len(self.REACTIONS)
        upper_bounds = []
        for i in range(len(self.REACTIONS)):
            stoich_lim = self.STOICH_COEFF[i][self.comp_idx[self.LIMITING_REACTANT]]
            max_extent = initial_moles[self.comp_idx[self.LIMITING_REACTANT]] / abs(
                stoich_lim
            )
            upper_bounds.append(max_extent)
        return (lower_bounds, upper_bounds)

    def _equilibrium_objective(self, extent, P_bar, initial_moles, Keq):
        molfrac = self._compute_final_molfrac(initial_moles, extent)[0]
        molfrac[molfrac < 0] = 0.00001
        p = molfrac * P_bar
        fugacity = self.fugacity_coeff * p
        activity = fugacity / quant.STD_STATE_FUGACITY.bar
        K_calc = np.prod(activity**self.STOICH_COEFF, axis=1)
        return (np.log(K_calc) - np.log(Keq)) ** 2

    def equilibrate(
        self,
        p0: quant.Pressure,
        T: quant.Temperature,
        initial_guesses=None,
        allow_component_mismatch=False,
    ):
        self.T = T
        initial_total_moles = 100
        if allow_component_mismatch:
            p0_bar = [p0[comp].bar for comp in self.comp_list()]
            p0 = quant.Pressure(bar=p0_bar, keys=self.comp_list())
        P = quant.Pressure(si=np.sum(p0.si))
        initial_molfrac = p0 / P
        initial_moles = initial_molfrac.si * initial_total_moles
        assert isinstance(initial_moles, np.ndarray)
        if not initial_guesses:
            num_rxns = len(self.REACTIONS)
            initial_guess = (
                initial_moles[self.comp_idx[self.LIMITING_REACTANT]] / num_rxns
            )
            initial_guesses = np.ones(num_rxns) * initial_guess / 2

        def objective(extent):
            return self._equilibrium_objective(extent, P.bar, initial_moles, self.Keq)

        solution = least_squares(
            objective,
            initial_guesses,
            bounds=self._compute_extent_bounds(initial_moles),
            method="trf",
            ftol=1e-10,
            max_nfev=1000,
        )
        extent = solution.x
        eq_molfrac, delta_moles = self._compute_final_molfrac(initial_moles, extent)
        delta = delta_moles[self.comp_idx[self.LIMITING_REACTANT]]
        initial = initial_moles[self.comp_idx[self.LIMITING_REACTANT]]
        self.eq_conversion = quant.Fraction(si=-delta / initial)
        self.eq_molfrac = quant.Fraction(si=eq_molfrac, keys=self.comp_list())
        self.eq_partial_pressure = self.eq_molfrac * P

    @classmethod
    def carbon_balance(cls, reactor):
        carbon_in = np.sum(reactor.F0.si * cls.C_ATOMS)
        carbon_out = np.sum(reactor.F.si * cls.C_ATOMS[:, np.newaxis], axis=0)
        c_bal = cat.utils.divide(carbon_out, carbon_in)
        return quant.Fraction(si=c_bal)

    def calculate_rates(self, p: quant.Pressure):
        raise NotImplementedError("Child class must implement calculate_rates().")
