from __future__ import annotations

import numpy as np
from model.core import CoreTimeSeries
from model.ev import Ev
import cvxpy as cvx


class Fleet(CoreTimeSeries):

    def __init__(
            self,
            date_range,
            ev_capacity: int = 1,
            peak_demand_cost: float = 15,
            peak_energy_cost: float = 0.5,
            normal_energy_cost: float = 0.35,
            initial_soc_list: list = [],
            slow_charge_cost: float = 100,
            **kwargs
    ):

        super().__init__(**kwargs)

        self.time_range = date_range
        self.ev_capacity = ev_capacity
        self.peak_demand_cost = peak_demand_cost
        self.peak_energy_cost = peak_energy_cost
        self.normal_energy_cost = normal_energy_cost
        self.initial_soc_list = initial_soc_list
        self.slow_charge_cost = slow_charge_cost

        self.ev_list = []

        self.total_energy_in = cvx.Variable(shape=(self.n,), nonneg=True, name=self.name + "_total_energy_state")
        self.total_power_state = cvx.Variable(shape=(self.n,), nonneg=True, name=self.name + "_total_power_state")

        self.initialize_fleet_model()
        self.energy_price_vector = self.create_energy_price_vector()

    def initialize_fleet_model(self):
        for i in range(self.ev_capacity):
            electric_vehicle = Ev(dt=self.dt, name=f'ev_{i}', initial_soc=self.initial_soc_list[i])
            self.ev_list.append(electric_vehicle)

    def create_energy_price_vector(self):
        energy_price_vector = np.zeros(self.n)
        for i in range(self.n):
            if 15 <= self.time_range[i].hour <= 19:
                energy_price_vector[i] = self.peak_energy_cost
            else:
                energy_price_vector[i] = self.normal_energy_cost
        return energy_price_vector

    def solve(self):
        constraints = super().constraints()

        for electric_vehicle in self.ev_list:
            constraints += electric_vehicle.constraints()

        evs = sum(electric_vehicle for electric_vehicle in self.ev_list)

        constraints += [
            self.total_energy_in == evs.energy_in,
            self.total_power_state == evs.power_state
        ]

        # minimize for energy cost
        objective = cvx.Minimize(-1 * cvx.sum(cvx.multiply(evs.energy_in, self.energy_price_vector)))

        # minimize for peak demand
        objective += cvx.Minimize(cvx.max(self.total_power_state) * self.peak_demand_cost)

        objective += cvx.Minimize(-1 * cvx.min(self.total_power_state) * self.slow_charge_cost)

        p = cvx.Problem(objective=objective, constraints=constraints)

        p.solve()

        status = p.status

        return status, self.ev_list, self.energy_price_vector
