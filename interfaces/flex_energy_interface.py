from model.portfolio import Portfolio
import numpy as np


class FlexEnergyInterface:

    def __init__(
            self,
            pv_forecast_e,
            load_forecast_e,
            baseline_da,
            final_soe_list,
            num_sites
    ):
        dt = np.zeros(24)
        for i in range(24):
            dt[i] = 3600

        self.portfolio = Portfolio(
            sites_capacity=num_sites,
            final_soe_list=final_soe_list,
            pv_forecast=pv_forecast_e,
            load_forecast=load_forecast_e,
            baseline_da=baseline_da,
            dt=dt
        )

    def get_max_flex_energy(self):
        max_flex = self.portfolio.solve()
        return max_flex

    def get_max_flex_energy_with_error(self, error_margin_load_forecast, error_margin_solar_forecast):
        max_flex = self.portfolio.solve(
            error_margin_load_forecast=error_margin_load_forecast,
            error_margin_solar_forecast=error_margin_solar_forecast
        )
        return max_flex


if __name__ == '__main__':
    final_soe_list = [50, 60, 70, 80, 90]
    interface = FlexEnergyInterface(
        pv_forecast_e=1000,
        load_forecast_e=700,
        baseline_da=2000,
        final_soe_list=final_soe_list,
        num_sites=5
    )
    print("max energy no error: " + str(interface.get_max_flex_energy()))

    print("max energy with 5% error: " + str(interface.get_max_flex_energy_with_error(0.05, 0.05)))
