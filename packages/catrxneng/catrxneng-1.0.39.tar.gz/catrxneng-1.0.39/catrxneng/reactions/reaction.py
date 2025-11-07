import numpy as np
from numpy.typing import NDArray
from scipy.optimize import minimize_scalar

from catrxneng.species import Species
import catrxneng.quantities as quant


class Reaction:
    EQUATION: str
    STOICH_COEFF: quant.Dimensionless
    COMPONENTS: dict[str, type[Species]]
    DEFAULT_LIMITING_REACTANT: str

    @property
    def limiting_reactant(self):
        try:
            return self._limiting_reactant
        except AttributeError:
            return self.DEFAULT_LIMITING_REACTANT

    @limiting_reactant.setter
    def limiting_reactant(self, value):
        self._limiting_reactant = value

    @classmethod
    def comp_list(cls):
        return list(cls.COMPONENTS.keys())

    @classmethod
    def active_components(cls):
        # return {key: cls.COMPONENTS[key] for key in cls.COMPONENTS if key != "inert"}
        return {**cls.REACTANTS, **cls.PRODUCTS}

    @classmethod
    def stoich_coeff_active(cls):
        stoich_si = np.asarray(cls.STOICH_COEFF.si)
        return quant.Dimensionless(
            si=stoich_si[stoich_si != 0],
            keys=list(cls.active_components().keys()),
        )

    @classmethod
    def dH_rxn_298_gas(cls) -> quant.Energy:
        Hf_298_gas = np.array(
            [cls.COMPONENTS[key].HF_298_GAS.si for key in cls.active_components()]
        )
        dHr_298_gas = np.sum(Hf_298_gas * cls.stoich_coeff_active().si)
        return quant.Energy(si=dHr_298_gas)

    @classmethod
    def dH_rxn_gas(cls, T):
        # Hf_gas = np.array(
        #     [cls.COMPONENTS[key].Hf_gas(T).si for key in cls.active_components()]
        # )
        Hf_gas = np.array(
            [comp_cls.Hf_gas(T).si for comp_cls in cls.active_components().values()]
        )
        dHr_gas = np.sum(Hf_gas * cls.stoich_coeff_active().si)
        return quant.Energy(si=dHr_gas)

    @classmethod
    def dS_rxn_298_gas(cls) -> quant.Entropy:
        S_298_gas = np.array(
            [cls.COMPONENTS[key].S_298_GAS.si for key in cls.active_components()]
        )
        dSr_298_gas = np.sum(S_298_gas * cls.stoich_coeff_active().si)
        return quant.Entropy(si=dSr_298_gas)

    @classmethod
    def dS_rxn_gas(cls, T):
        S_gas = np.array(
            [cls.COMPONENTS[key].S_gas(T).si for key in cls.active_components()]
        )
        dSr_gas = np.sum(S_gas * cls.stoich_coeff_active().si)
        return quant.Entropy(si=dSr_gas)

    @classmethod
    def dG_rxn_298_gas(cls):
        T = quant.Temperature(K=298)
        return cls.dH_rxn_298_gas() - T * cls.dS_rxn_298_gas()

    @classmethod
    def dG_rxn(cls, T: quant.Temperature) -> quant.Energy:
        return cls.dH_rxn(T) - T * cls.dS_rxn(T)

    @classmethod
    def dG_rxn_gas(cls, T):
        return cls.dH_rxn_gas(T) - T * cls.dS_rxn_gas(T)

    @classmethod
    def Keq(cls, T: quant.Temperature) -> float:
        return np.exp(-cls.dG_rxn(T) / (quant.R * T)).si

    @classmethod
    def check_components(cls, p0, allow_component_mismatch):
        if p0.keys != list(cls.COMPONENTS.keys()) and not allow_component_mismatch:
            raise ValueError("Partial pressure keys do not match reaction components.")

    def equilibrate(
        self,
        p0: quant.Pressure,
        T: quant.Temperature,
        Keq: float | None = None,
        fug_coeff: NDArray | None = None,
        allow_component_mismatch: bool = False,
        limiting_reactant: str | None = None,
    ):
        """
        Pressure in bar
        """
        if limiting_reactant is None:
            limiting_reactant = self.DEFAULT_LIMITING_REACTANT
        self.check_components(p0, allow_component_mismatch=allow_component_mismatch)

        if allow_component_mismatch:
            p0_bar = np.array([p0[comp].bar for comp in self.comp_list()])
            p0 = quant.Pressure(bar=p0_bar.astype(float), keys=self.comp_list())

        P_bar = np.sum(p0.bar)
        initial_total_moles = 100.0
        initial_molfrac = p0.bar / P_bar
        initial_moles = initial_molfrac * initial_total_moles

        std_state_fugacity_bar = quant.Pressure(
            atm=np.ones(len(self.COMPONENTS)).astype(float)
        ).bar
        if fug_coeff is None:
            fug_coeff = np.ones(len(self.COMPONENTS)).astype(float)

        stoich_coeff = self.STOICH_COEFF.si
        if Keq is None:
            Keq = type(self).Keq(T=T)

        def objective(extent):
            moles = initial_moles + extent * stoich_coeff
            if np.any(moles < 0):
                return 1e10
            total_moles = np.sum(moles)
            molfrac = moles / total_moles
            fugacity = molfrac * fug_coeff * P_bar
            activity = fugacity / std_state_fugacity_bar
            Ka = np.prod(activity**stoich_coeff)
            if Ka <= 0:
                return 1e10
            log_error = np.log(Ka) - np.log(Keq)  # type: ignore
            return log_error * log_error

        # Calculate extent bounds from stoichiometry
        # Maximum extent limited by complete consumption of any reactant
        adj_init_mol_reactants = np.array(
            [
                mol / stoich
                for mol, stoich in zip(initial_moles, stoich_coeff)
                if stoich < 0
            ]
        )
        min_extent = 1e-5  # Small positive value to avoid numerical issues
        max_extent = np.min(-adj_init_mol_reactants) * 0.999  # Leave small margin

        # Use bounded scalar minimization - more efficient and robust for 1D problems
        result = minimize_scalar(
            objective,
            bounds=(min_extent, max_extent),
            method="bounded",
            options={"xatol": 1e-8, "maxiter": 500},
        )

        if result.success:
            self.extent = quant.Moles(si=result.x)
            initial_moles = quant.Moles(si=initial_moles, keys=self.comp_list())
            moles = initial_moles + self.extent * self.STOICH_COEFF
            self.eq_conversion = (
                initial_moles[limiting_reactant] - moles[limiting_reactant]
            ) / initial_moles[limiting_reactant]
            total_moles = quant.Moles(si=np.sum(moles.si))
            self.eq_molfrac = moles / total_moles
        else:
            raise ValueError("Optimization failed: " + result.message)
