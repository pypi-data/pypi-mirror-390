import numpy as np
from scipy.integrate import solve_ivp

from .. import utils
from .reactor import Reactor
from catrxneng.kinetic_models import KineticModel
from catrxneng.species.gas_mixture import GasMixture
import catrxneng.quantities as quant


class PFR(Reactor):
    def __init__(
        self,
        kinetic_model_class: type[KineticModel],
        T: quant.Temperature,
        p0: quant.Pressure,
        whsv: quant.WHSV | None = None,
        mcat: quant.Mass | None = None,
        F0: quant.MolarFlowRate | None = None,
        **kinetic_model_kwargs,
    ):
        self.kinetic_model_class = kinetic_model_class
        self.kinetic_model: KineticModel = kinetic_model_class(
            T=T, **kinetic_model_kwargs
        )
        self.T = T
        self.p0 = p0
        feed = GasMixture(components=self.kinetic_model_class.COMPONENTS, p=self.p0)
        self.P = quant.Pressure(si=np.sum(p0.si))
        self.P_bar = self.P.bar
        self.y0 = utils.divide(p0, self.P)
        self.whsv = whsv
        self.mcat: quant.Mass = quant.Mass(g=1) if mcat is None else mcat
        if self.whsv:
            if self.whsv.gas_mixture is None:
                self.whsv.gas_mixture = feed
            self.Ft0_active = self.whsv * self.mcat
            self.Ft0 = self.Ft0_active / (1 - self.y0["inert"])
            self.F0 = self.y0 * self.Ft0
        elif F0 is not None:
            self.F0 = F0
            self.Ft0 = quant.MolarFlowRate(molh=np.sum(self.F0.molh))
            self.Ft0_active = self.Ft0 - self.F0["inert"]
            self.whsv = quant.WHSV(
                molhgcat=self.Ft0_active.molh / self.mcat.g, gas_mixture=feed
            )
        else:
            raise ValueError("whsv and F0 cannot both be None.")
        self.check_components()

    def dFdw(self, x, F: np.ndarray) -> np.array:
        p_array = F / np.sum(F) * self.P_bar
        return self.kinetic_model.rate_equations(p_array)

    def dfdx(self, x, f: np.ndarray) -> np.array:
        Ft = np.sum(self.Ft0_active.si * f)
        p = self.P.si * self.Ft0_active.si * f / Ft
        p = quant.Pressure(si=p, keys=self.p0.keys.copy())
        return (
            self.mcat.si
            / self.Ft0_active.si
            * np.array(
                [
                    rate(p, self.T).si
                    for rate in self.kinetic_model.rate_equations.values()
                ]
            )
        )

    def _solve_dimensional(self, points: int, method: str):
        w_span = (0, self.mcat.g)
        w_eval = np.linspace(0, self.mcat.g, points)
        F0 = self.F0.molh
        solution = solve_ivp(self.dFdw, w_span, F0, t_eval=w_eval, method=method)
        self.w = quant.Mass(g=solution.t)
        self.F = quant.MolarFlowRate(molh=solution.y, keys=self.F0.keys)

    def _solve_dimensionless(
        self, points: int, method: str, rtol: float = 1e-3, atol: float = 1e-6
    ):
        x_span = (0, 1)
        x_eval = np.linspace(x_span[0], x_span[1], points)
        f0 = self.F0.si / self.Ft0_active.si
        solution = solve_ivp(
            self.dfdx, x_span, f0, t_eval=x_eval, method=method, rtol=rtol, atol=atol
        )
        self.x = solution.t
        self.f = solution.y
        self.w = quant.Mass(si=(self.x * self.mcat.si))
        F = self.Ft0_active.si * self.f
        self.F = quant.MolarFlowRate(si=F, keys=self.F0.keys)

    def solve(
        self, points: int = 1000, nondimensionalize: bool = False, method: str = "LSODA"
    ):
        if nondimensionalize:
            self._solve_dimensionless(points=points, method=method)
        else:
            self._solve_dimensional(points=points, method=method)
        y_si = np.divide(self.F.si, np.sum(self.F.si, axis=0))
        self.y = quant.Fraction(si=y_si, keys=self.F0.keys)
        self.conversion = utils.divide(
            self.F0[self.kinetic_model.LIMITING_REACTANT]
            - self.F[self.kinetic_model.LIMITING_REACTANT],
            self.F0[self.kinetic_model.LIMITING_REACTANT],
        )
        spacetime = utils.divide(self.w.g, self.Ft0_active.smLh)
        self.spacetime = quant.SpaceTime(hgcatsmL=spacetime)
        self.whsv_array = quant.WHSV(smLhgcat=utils.divide(1, spacetime))
        vol_flow_rate = self.Ft0.si * quant.R.si * self.T.si / self.P.si
        self.vol_flow_rate = quant.VolumetricFlowRate(si=vol_flow_rate)
        self.p = self.y * self.P
        self.rate = self.kinetic_model.calculate_rates(self.p)

    @property
    def conv_rel_to_eq_conv(self):
        self.kinetic_model.equilibrate(p0=self.p0, T=self.T)
        return self.conversion[-1] / self.kinetic_model.eq_conversion

    def compute_carbon_basis_selectivity(self):
        prod_carbon_molh = np.zeros(self.F.si.shape[1])
        for species_id, species in self.kinetic_model_class.PRODUCTS.items():
            prod_carbon_molh += self.F[species_id].molh * species.C_ATOMS
        sel = np.array(
            [
                self.F[species_id].molh * species.C_ATOMS / prod_carbon_molh  # type: ignore
                for species_id, species in self.kinetic_model_class.PRODUCTS.items()
            ]
        )
        self.carbon_basis_selectivity = quant.Fraction(
            si=sel, keys=list(self.kinetic_model_class.PRODUCTS.keys())
        )
