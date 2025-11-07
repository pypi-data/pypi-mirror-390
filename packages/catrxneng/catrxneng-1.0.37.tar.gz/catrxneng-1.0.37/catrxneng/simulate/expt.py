import os, requests, pandas as pd
from typing import List

from catrxneng import utils
import catrxneng.quantities as quant
from .step import Step


class Expt:

    @property
    def steady_state_steps(self) -> List[Step]:
        return [step for step in self.steps if step.step_name == "steadyState"]

    @property
    def date_str(self):
        return self.steps[0].start.date_str

    def __init__(
        self,
        expt_type,
        reactor_class,
        kinetic_model_class,
        step_class: type[Step],
        catalyst,
        mcat,
        unit,
        lab_notebook_id,
        project,
        gc=None,
        **kinetic_model_kwargs,
    ):
        self.expt_type = expt_type
        self.reactor_class = reactor_class
        self.kinetic_model_class = kinetic_model_class
        self.kinetic_model_kwargs = kinetic_model_kwargs
        self.step_class = step_class
        self.catalyst = catalyst
        self.mcat = mcat
        self.unit = unit
        self.gc = gc
        self.lab_notebook_id = lab_notebook_id
        self.project = project
        # self.T = T
        # self.p0 = p0
        # self.whsv = whsv
        self.steps: List[Step] = []
        self.pickle_name = self.lab_notebook_id

    def add_step(self, step_name, duration, T, p0, whsv=None, F0=None, start=None):
        if start is None:
            start = self.steps[-1].end
        end = start + duration
        reactor = self.reactor_class(
            T=T,
            kinetic_model_class=self.kinetic_model_class,
            p0=p0,
            whsv=whsv,
            F0=F0,
            mcat=self.mcat,
            **self.kinetic_model_kwargs,
        )
        step = self.step_class(
            self, step_name, len(self.steps) + 1, start, end, reactor
        )
        self.steps.append(step)

    def simulate(self, dt_sec, std_dev=None):
        for step in self.steps:
            step.simulate(dt_sec, std_dev)
        dataframes = [step.time_series_data for step in self.steps]
        self.time_series_data = pd.concat(dataframes, ignore_index=True)
        self._compute_tos()
        for index, step in enumerate(self.steady_state_steps):
            step.steady_state_step_num = index + 1

    def upload_data_to_influx(self, bucket, measurement):
        influx = utils.Influx(
            url=os.getenv("INFLUXDB_URL"),
            org=os.getenv("INFLUXDB_ORG"),
            bucket=bucket,
            measurement=measurement,
        )
        df = self.time_series_data.rename(columns=utils.getconf(self.unit, "tags"))
        influx.upload_dataframe(dataframe=df, token=os.getenv("INFLUXDB_TOKEN"))

    def _compute_tos(self):
        for step in self.steps:
            if step.step_name == "steadyState":
                start = step.start.UET
                break
        self.tos_sec = self.time_series_data["timestamp"] - start
        self.tos_hr = self.tos_sec / 3600.0

    def upload_to_emp(self, host, dt_sec, notes=""):
        endpoint = f"/api/create_simulated_expt/{self.project}"
        url = host + endpoint
        params = {
            "expt_type": self.expt_type,
            "lab_notebook_id": self.lab_notebook_id,
            "unit": self.unit,
            "gc": self.gc,
            "material__common_name": self.catalyst,
            "sample_mass": self.mcat.g,
            "start__ET_str": self.steps[0].start.ET_str,
            "end__ET_str": self.steps[-1].end.ET_str,
            "dt_sec": dt_sec,
            "notes": notes,
        }
        self.delete_from_emp(host)
        resp = requests.post(url, json=params, timeout=10)

        if not resp.ok:
            try:
                error_data = resp.json()
                return {"status_code": resp.status_code, "error": error_data}
            except ValueError:
                return {"status_code": resp.status_code, "body": resp.text}

        try:
            return resp.json()
        except ValueError:
            return {"status_code": resp.status_code, "body": resp.text}

    def delete_from_emp(self, host):
        endpoint = f"/api/delete_expt/{self.project}"
        if not host.startswith("http://") and not host.startswith("https://"):
            host = "http://" + host
        url = host + endpoint
        params = {"lab_notebook_id": self.lab_notebook_id, "project": self.project}
        resp = requests.delete(url, json=params, timeout=10)

        if not resp.ok:
            try:
                error_data = resp.json()
                return {"status_code": resp.status_code, "error": error_data}
            except ValueError:
                return {"status_code": resp.status_code, "body": resp.text}

        try:
            return resp.json()
        except ValueError:
            return {"status_code": resp.status_code, "body": resp.text}

    def compute_inlet_partial_pressures(self):
        df = self.time_series_data.copy()
        mask = [col for col in df.columns if "_mfc" in col]
        total_inlet_flow_molh = df[mask].sum(axis=1)
        for col in mask:
            y = df[col] / total_inlet_flow_molh
            p_col_id = f"p_{col.split('_mfc')[0]}_bar"
            df[p_col_id] = y * df["pressure"]
        return df
