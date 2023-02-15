from __future__ import annotations

import numpy as np
from model.core import CoreTimeSeries
from model.battery import Battery
import cvxpy as cvx


class Portfolio(CoreTimeSeries):

    def __init__(
            self,
            sites_capacity: int = 1,
            final_soe_list: float = [],
            pv_forecast: float = 0.0,
            load_forecast: float = 0.0,
            baseline_da: float = 0.0,
            **kwargs
    ):

        super().__init__(**kwargs)

        self.sites_capacity = sites_capacity
        self.pv_forecast = pv_forecast
        self.load_forecast = load_forecast
        self.baseline_da = baseline_da
        self.final_soe_list = final_soe_list

        self.battery_list = []

        self.total_energy_flow = cvx.Variable(shape=(self.n,), nonneg=True, name=self.name + "_total_energy_state")

        self.initialize_portfolio_model()

    def initialize_portfolio_model(self):
        for i in range(self.sites_capacity):
            battery = Battery(dt=self.dt, name=f'battery_{i}', final_energy_state=self.final_soe_list[i])
            self.battery_list.append(battery)

    def solve(self,
              error_margin_load_forecast: float = 0.0,
              error_margin_solar_forecast: float = 0.0,
              ):
        constraints = super().constraints()

        for battery in self.battery_list:
            constraints += battery.constraints()

        bats = sum(battery for battery in self.battery_list)

        constraints += [
            self.total_energy_flow == bats.energy_flow
        ]

        # estimate max flex energy
        objective = cvx.Maximize(
            self.baseline_da
            - self.load_forecast * (1 + error_margin_load_forecast)
            + self.pv_forecast * (1 - error_margin_solar_forecast)
            + cvx.sum(self.total_energy_flow)
        )

        p = cvx.Problem(objective=objective, constraints=constraints)

        p.solve()

        flex_energy = self.baseline_da - self.load_forecast * (
                1 + error_margin_load_forecast) + self.pv_forecast * (
                1 - error_margin_solar_forecast) + np.sum(self.total_energy_flow.value)

        return flex_energy
