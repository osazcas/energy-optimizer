import random

from model.fleet import Fleet
import pandas as pd
import numpy as np

"""
This example calculates the optimal schedules for an ev fleet for the next 30 days starting from today.
The dt vector starts from today and ranges for 30 days with 1 hour time steps.
"""

if __name__ == '__main__':

    time_now = pd.Timestamp.now(tz='US/Pacific')
    end_time = time_now + pd.Timedelta(days=1)
    date_range = pd.period_range(start=time_now, end=end_time, freq="15min")
    dt = np.zeros(24 * 4)

    for i in range(24 * 4):
        dt[i] = 15 * 60

    ev_capacity = 10
    initial_soc_list = []
    for i in range(ev_capacity):
        initial_soc_list.append(random.random())

    fleet = Fleet(ev_capacity=ev_capacity, dt=dt, initial_soc_list=initial_soc_list, date_range=date_range)
    status, ev_list, price_vector = fleet.solve()

    if status == "optimal":
        print("Was able to find optimal solution")
    else:
        print("Was not able to find optimal solution")