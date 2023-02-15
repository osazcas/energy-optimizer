from __future__ import annotations
import cvxpy as cvx
from model.core import CoreTimeSeries


"""
Simpler battery model that doesn't consider efficiency and uses final state of energy.
"""


class Battery(CoreTimeSeries):

    def __init__(
            self,
            rated_energy: float = 100.0,
            p_max_charge: float = 50.0,
            final_energy_state: float = 0.0,
            **kwargs
    ):
        """
        :param capacity: capacity in kWh
        :param power_charge
        """
        super().__init__(**kwargs)

        self.rated_energy = rated_energy
        self.p_max_charge_discharge = p_max_charge
        self.final_energy_state = final_energy_state

        self.energy_state = cvx.Variable(shape=(self.n + 1,), nonneg=True, name=self.name + "_energy_state")

        self.power_state = cvx.Variable(shape=(self.n,), nonneg=False, name=self.name + "_power_state")

        self.energy_flow = cvx.Variable(shape=(self.n,), nonneg=True, name=self.name + "_energy_in_out")

    def constraints(self):
        constraints = super().constraints()

        constraints += [

            self.energy_state[-1] == self.final_energy_state,

            # Energy Bounds
            self.energy_state >= 0,
            self.energy_state <= self.rated_energy,

            # Battery can charge and discharge
            self.power_state <= self.p_max_charge_discharge,
            self.power_state >= -1 * self.p_max_charge_discharge,

            self.energy_flow == cvx.multiply(self.power_state, self.dt / 3600),

            self.energy_state[:-1] == self.cumulative_sum(self.energy_flow) + self.energy_state[-1],


        ]

        return constraints

    def __add__(self, other: Battery) -> Battery:
        """
        Returns an instance of a Battery class. Overloads the add operator to
        allow for the addition of classes and aggregation of these classes
        properties.
        :param other: Ev
        :return: Ev
        """

        bat = Battery(dt=self.dt)  # Takes time vector from first class

        bat.energy_flow = self.energy_flow + other.energy_flow

        return bat

    def __radd__(self, other: Battery) -> Battery:
        """
        Overloading the radd method to enable summing multiple Storage classes
        :param other: Storage
        :return: Storage
        """

        if isinstance(other, Battery):
            return self.__add__(other)
        return self
