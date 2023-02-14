import cvxpy as cvx


class Core:

    def __init__(self, name="unnamed"):
        """
        Core dynamical model
        """

        self.name = name

    def constraints(self):
        constraints = []
        return constraints

    def objective(self):
        return None


class CoreTimeSeries(Core):
    """
    Core dynamical model model that integrates timing engine
    """

    def __init__(self, dt, **kwargs):
        super().__init__(**kwargs)

        self.dt = dt
        self.n = len(dt)

    def cumulative_sum(self, expression):
        return expression if self.n <= 1 else cvx.cumsum(expression)
