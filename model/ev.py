from __future__ import annotations
import cvxpy as cvx
from model.core import CoreTimeSeries


class Ev(CoreTimeSeries):

    def __init__(
            self,
            rated_energy: float = 100.0,
            p_max_charge: float = 50.0,
            efficiency: float = 0.9,
            initial_soc: float = 0.0,
            max_soc_derating: float = 0.8,
            **kwargs
    ):
        """
        :param capacity: capacity in kWh
        :param power_charge
        """
        super().__init__(**kwargs)

        self.mip = False
        self.rated_energy = rated_energy
        self.p_max_charge = p_max_charge
        self.efficiency = efficiency
        self.initial_soc = initial_soc
        self.max_soc_derating = max_soc_derating

        self.energy_state = cvx.Variable(shape=(self.n + 1,), nonneg=True, name=self.name + "_energy_state")
        self.soc = cvx.Variable(shape=(self.n + 1,), nonneg=True, name=self.name + "_soc")

        self.power_state = cvx.Variable(shape=(self.n,), nonneg=True, name=self.name + "_power_state")

        self.energy_in = cvx.Variable(shape=(self.n,), nonneg=True, name=self.name + "_energy_in")

        self.above_max_soc_derating = cvx.Variable(shape=(self.n,), boolean=True, name=self.name + "_above_max_soc_derating")

    def constraints(self):
        constraints = super().constraints()

        constraints += [

            self.energy_state[0] == self.initial_soc * self.rated_energy,

            # Energy Bounds
            self.energy_state >= 0,
            self.energy_state <= self.rated_energy,

            # EV only charges
            self.power_state >= 0,
            self.power_state <= self.p_max_charge,

            self.energy_in == cvx.multiply(self.power_state, self.dt / 3600) * self.efficiency,

            self.energy_state[1:] == self.cumulative_sum(self.energy_in) + self.energy_state[0],

            # State as a percentage
            self.soc == self.energy_state / self.rated_energy,

            self.soc[24*2] >= 0.8
        ]

        if self.mip:
            constraints += [
                # When the SoC is above a certain threshold, power is derated to half
                self.above_max_soc_derating >= self.soc[1:] / self.max_soc_derating,
                self.power_state <= self.above_max_soc_derating * (self.p_max_charge / 2) + (
                            1 - self.max_soc_derating) * self.p_max_charge
            ]

        return constraints

    def __add__(self, other: Ev) -> Ev:
        """
        Returns an instance of an Ev class. Overloads the add operator to
        allow for the addition of classes and aggregation of these classes
        properties.
        :param other: Ev
        :return: Ev
        """

        ev = Ev(dt=self.dt)  # Takes time vector from first class

        ev.power_state = self.power_state + other.power_state
        ev.energy_in = self.energy_in + other.energy_in

        return ev

    def __radd__(self, other: Ev) -> Ev:
        """
        Overloading the radd method to enable summing multiple Storage classes
        :param other: Storage
        :return: Storage
        """

        if isinstance(other, Ev):
            return self.__add__(other)
        return self
