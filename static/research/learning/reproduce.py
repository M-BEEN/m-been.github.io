"""Fictional learning examples, Python 3.10+, no packages or network required.

These are arithmetic examples, not observed trading returns. Run `python reproduce.py`.
All percentages in the output are percent units, not fractional returns.
"""
import json
import math
from pathlib import Path
from statistics import mean, median


def calculate():
    returns = [1] * 8 + [-2, -10]
    capital, risk, entry, stop, fee, cap = 10_000_000, .01, 50_000, 47_500, .002, .20
    shares = min(math.floor(capital * risk / (entry - stop + entry * fee)),
                 math.floor(capital * cap / (entry * (1 + fee))))
    return {
        'fictional_win_rate': {'input_pct': returns, 'win_pct': 80,
            'mean_pct': mean(returns), 'median_pct': median(returns),
            'sequential_final': 100_000 * math.prod(1 + r / 100 for r in returns)},
        'independent_comparisons': {str(n): (1 - .95 ** n) * 100 for n in (1, 6, 20)},
        'fixed_costs': {'initial': 1_000_000, 'gross_pct': .3, 'cost_pct': .2, 'rounds': 100,
            'before': 1_000_000 * 1.003 ** 100, 'after': 1_000_000 * 1.001 ** 100},
        'position': {'shares': shares, 'amount': shares * entry,
            'reserved_cost': shares * entry * fee, 'planned_loss': shares * (entry - stop + entry * fee),
            'gap_exit_loss': shares * (entry - 45_000 + entry * fee)},
        'etf': {'premium_pct': (10_200 / 10_000 - 1) * 100,
            'premium_unwind_pct': (10_000 / 10_200 - 1) * 100,
            'fx_down_pct': (1.10 * .92 - 1) * 100, 'fx_up_pct': (1.10 * 1.08 - 1) * 100},
        'valuation': {'eps': 1_000, 'bps': 5_000, 'per': 10, 'pbr': 2,
            'end_equity_return_pct': 20, 'average_equity_return_pct': 25},
    }


def rounded(value):
    if isinstance(value, dict): return {k: rounded(v) for k, v in value.items()}
    if isinstance(value, list): return [rounded(v) for v in value]
    return round(value, 6) if isinstance(value, float) else value


if __name__ == '__main__':
    result = rounded(calculate())
    expected = Path(__file__).with_name('expected.json')
    if expected.is_file() and result != json.loads(expected.read_text(encoding='utf-8')):
        raise SystemExit('Results differ from expected.json; investigate before changing the expected file.')
    print(json.dumps(result, ensure_ascii=False, indent=2))
