# spendwise-analytics

Reusable finance analytics for Spendwise (projection & budget status).

```python
from spendwise_analytics import BudgetInsights
bi = BudgetInsights(window=4, warn_threshold=0.1)
proj = bi.projected_monthly_spend(month_to_date=220.0, days_elapsed=7, days_in_month=30)
print(bi.budget_status(budget=800.0, projected=proj))
