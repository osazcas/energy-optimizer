from model.battery_enhanced import BatteryEnhanced
import pandas as pd
import numpy as np
import cvxpy as cvx


class DCMOptimizer:
    def __init__(self):
        self.battery_properties = {}
        self.load_df = None
        self.battery_initial_soc = 0.5

        self.dt = np.zeros(24*4)
        for i in range(24*4):
            self.dt[i] = 15 * 60

        self.battery_soc_schedule = []
        self.battery_power_schedule = []

    def set_load_data(self, load_data_file_str: str):
        self.load_df = pd.read_csv(load_data_file_str).set_index('datetime')

    def set_battery_specs(self, properties: dict):
        self.battery_properties = properties

    def set_initial_state_of_energy(self, initial_soc: float):
        self.battery_initial_soc = initial_soc

    def get_granularity(self):
        return self.dt[0]

    def get_battery_plan(self):
        plan_dict = {'soc_schedule': self.battery_soc_schedule, 'power_schedule': self.battery_power_schedule}
        return plan_dict

    def optimize(self, peak_demand_cost: float = 15):
        if self.load_df is not None and bool(self.battery_properties):
            bat = BatteryEnhanced(
                rated_energy=self.battery_properties['rated_energy'],
                p_max_charge=self.battery_properties['p_max_charge'],
                initial_soc=self.battery_initial_soc,
                charging_efficiency=self.battery_properties['charging_efficiency'],
                discharging_efficiency=self.battery_properties['discharging_efficiency'],
                dt=self.dt
            )

            constraints = bat.constraints()

            load_df_month = self.load_df[24*4:24*4*2]

            objective = cvx.Minimize(cvx.max(np.array(load_df_month['actual_kwh'].values) - bat.power_state) * peak_demand_cost)

            p = cvx.Problem(objective=objective, constraints=constraints)

            p.solve()

            self.battery_soc_schedule = bat.soc
            self.battery_power_schedule = bat.power_state

            return p.status
        else:
            return


if __name__ == '__main__':
    optimizer = DCMOptimizer()
    optimizer.set_load_data("../test_data/load_data.csv")
    battery_specs = {
        'rated_energy': 100,
        'p_max_charge': 50,
        'initial_soc': 0.2,
        'charging_efficiency': 0.98,
        'discharging_efficiency': 0.95
    }
    optimizer.set_battery_specs(properties=battery_specs)
    status = optimizer.optimize()

    print(f"status: {status}")
    print(f"battery soc plan: {optimizer.get_battery_plan()['soc_schedule'].value}")
    print(f"battery power plan: {optimizer.get_battery_plan()['power_schedule'].value}")
