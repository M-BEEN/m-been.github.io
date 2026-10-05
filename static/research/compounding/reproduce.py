"""Fictional price paths, not market observations. Python 3.10+, no dependencies."""
import json
from math import prod


def calculate(returns):
    growth = prod(1 + r for r in returns)
    return dict(arithmetic_daily_pct=100 * sum(returns) / len(returns),
                geometric_daily_pct=100 * (growth ** (1 / len(returns)) - 1),
                cumulative_pct=100 * (growth - 1),
                ideal_daily_2x_pct=100 * (prod(1 + 2 * r for r in returns) - 1))


paths = {'down_then_up': [-.1, .1], 'two_up_days': [.1, .1],
         'back_to_start': [-.1, 1 / 9]}
if __name__ == '__main__':
    results = {k: {field: round(v, 6) for field, v in calculate(rs).items()} for k, rs in paths.items()}
    assert results['down_then_up']['cumulative_pct'] == -1.0
    assert results['down_then_up']['ideal_daily_2x_pct'] == -4.0
    assert results['two_up_days']['cumulative_pct'] == 21.0
    assert results['two_up_days']['ideal_daily_2x_pct'] == 44.0
    assert results['back_to_start']['cumulative_pct'] == 0.0
    print(json.dumps(results, indent=2))
