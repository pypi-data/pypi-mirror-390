import plotly.graph_objects as go
import pandas as pd

from catrxneng.kinetic_models import KineticModel


class Reactor:

    kinetic_model_class: type[KineticModel]

    @property
    def molar_flowrate_df_molh(self):
        try:
            return self.molar_flowrate_df_molh_cache
        except AttributeError:
            molar_flowrate_dict = {
                key: value for key, value in zip(self.F.keys, self.F.molh)
            }
            self.molar_flowrate_df_molh_cache = molar_flowrate_dict
            return self.molar_flowrate_df_molh_cache

    @molar_flowrate_df_molh.setter
    def molar_flowrate_df_molh(self, value):
        self.molar_flowrate_df_molh_cache = value

    def __init__(self):
        from catrxneng.quantities import MolarFlowRate

        self.aggregate_flow_rates: dict[str, MolarFlowRate] = {}

    def check_components(self):
        if self.p0.size != len(self.kinetic_model.COMPONENTS):
            raise ValueError(
                "Number of components for reactor and rate model do not match."
            )

    def plot(self, x, y, names, modes, xlabel, ylabel, title=None):
        fig = go.Figure()
        for i in range(len(y)):
            trace = go.Scatter(x=x[i], y=[i], mode=modes[i], name=names[i])
            fig.add_trace(trace)
        fig.update_layout(
            title=dict(text=f"<b>{title}</b>", x=0.5),
            xaxis_title=f"<b>{xlabel}</b>",
            yaxis_title=f"<b>{ylabel}</b>",
            width=800,
        )
        fig.show()
