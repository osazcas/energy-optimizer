import cvxpy as cvx
from model.core import CoreTimeSeries

"""
Enhanced battery model which considers charging and discharging efficiency, and uses initial soc. 
This model cannot be aggregated the same way the 'Battery' model is. 
"""


class BatteryEnhanced(CoreTimeSeries):

    def __init__(
            self,
            rated_energy: float = 100.0,
            p_max_charge: float = 50.0,
            initial_soc: float = 0.5,
            charging_efficiency: float = 1,
            discharging_efficiency: float = 1,
            **kwargs
    ):
        """
        :param capacity: capacity in kWh
        :param power_charge
        """
        super().__init__(**kwargs)

        self.rated_energy = rated_energy
        self.p_max_charge_discharge = p_max_charge
        self.initial_soc = initial_soc
        self.charging_efficiency = charging_efficiency
        self.discharging_efficiency = discharging_efficiency

        self.energy_state = cvx.Variable(shape=(self.n + 1,), nonneg=True, name=self.name + "_energy_state")
        self.soc = cvx.Variable(shape=(self.n + 1,), nonneg=True, name=self.name + "_soc")

        self.power_state = cvx.Variable(shape=(self.n,), nonneg=False, name=self.name + "_power_state")

        self.charge = cvx.Variable(shape=(self.n,), nonneg=False, name=self.name + "_charge")
        self.discharge = cvx.Variable(shape=(self.n,), nonneg=False, name=self.name + "_discharge")

        self.energy_in = cvx.Variable(shape=(self.n,), nonneg=False, name=self.name + "_energy_in")
        self.energy_out = cvx.Variable(shape=(self.n,), nonneg=False, name=self.name + "_energy_out")

    def constraints(self):
        constraints = super().constraints()

        constraints += [

            self.energy_state[0] == self.initial_soc * self.rated_energy,

            # Energy Bounds
            self.energy_state >= 0,
            self.energy_state <= self.rated_energy,

            # Battery can charge and discharge

            self.charge >= 0,
            self.charge <= self.p_max_charge_discharge,

            self.discharge >= 0,
            self.discharge <= self.p_max_charge_discharge,

            self.power_state == self.discharge - self.charge,

            # Energy in and out

            self.energy_in == cvx.multiply(self.charge, self.dt / 3600) * self.charging_efficiency,
            self.energy_out == cvx.multiply(self.charge, self.dt / 3600) / self.discharging_efficiency,

            self.energy_state[1:] == self.cumulative_sum(self.energy_in - self.energy_out) + self.energy_state[0],

            self.soc == self.energy_state / self.rated_energy

        ]

        return constraints
