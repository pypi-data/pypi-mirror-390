from __future__ import annotations
from statistics import mean

class BudgetInsights:
    """
    Core budgeting utilities:
    - moving_average: smooth a recent window of values
    - projected_monthly_spend: extrapolate current pace to month end
    - budget_status: compare projection to a budget with a warn threshold
    """
    def __init__(self, window:int=4, warn_threshold:float=0.1):
        if window <= 0:
            raise ValueError("window must be > 0")
        if warn_threshold < 0:
            raise ValueError("warn_threshold must be >= 0")
        self.window = window
        self.warn_threshold = warn_threshold

    def moving_average(self, values:list[float]) -> float:
        if not values:
            return 0.0
        w = min(self.window, len(values))
        return mean(values[-w:])

    def projected_monthly_spend(self, month_to_date:float, days_elapsed:int, days_in_month:int) -> float:
        if days_in_month <= 0:
            raise ValueError("days_in_month must be > 0")
        if days_elapsed < 0 or days_elapsed > days_in_month:
            raise ValueError("days_elapsed must be within [0, days_in_month]")
        if days_elapsed == 0:
            return 0.0
        daily_run = month_to_date / days_elapsed
        return daily_run * days_in_month

    def budget_status(self, budget:float, projected:float) -> dict:
        if budget < 0:
            raise ValueError("budget cannot be negative")
        delta = projected - budget
        pct = (delta / budget) if budget > 0 else 0.0
        warn = pct >= self.warn_threshold
        return {
            "projected": float(projected),
            "budget": float(budget),
            "delta": float(delta),
            "over_budget": warn,
            "pct_over": float(pct) if budget > 0 else 0.0
        }
