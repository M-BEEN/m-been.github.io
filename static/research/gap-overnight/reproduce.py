#!/usr/bin/env python3
"""Reproduce the index gap/intraday calculations from a local daily-price CSV.

Python 3.10+, standard library only. No network, credentials, or trading actions.
The supplied sample.csv is synthetic, not the original study's market data.
"""
import argparse
import csv
from datetime import date
import hashlib
import json
import math
from pathlib import Path
import statistics


def read_prices(path):
    rows = []
    with path.open(encoding='utf-8-sig', newline='') as stream:
        reader = csv.DictReader(stream)
        if not {'Date', 'Open', 'Close'}.issubset(reader.fieldnames or []):
            raise ValueError('CSV requires Date,Open,Close columns')
        for number, row in enumerate(reader, 2):
            day = date.fromisoformat(row['Date'])
            if day.isoformat() != row['Date']:
                raise ValueError(f'Row {number}: date must use YYYY-MM-DD')
            opening, closing = float(row['Open']), float(row['Close'])
            if any(not math.isfinite(x) or x <= 0 for x in (opening, closing)):
                raise ValueError(f'Row {number}: prices must be finite and positive')
            if rows and day <= rows[-1][0]:
                raise ValueError(f'Row {number}: dates must be unique and ascending')
            rows.append((day, opening, closing))
    if len(rows) < 2:
        raise ValueError('At least two rows required, including the prior close')
    return rows


def describe(values):
    n = len(values)
    mean = statistics.mean(values)
    std = statistics.stdev(values) if n > 1 else 0
    return {'n': n, 'mean_pct': mean * 100,
            'sample_std_pct': std * 100 if n > 1 else None,
            'naive_t': mean / (std / math.sqrt(n)) if std else None,
            'positive_fraction': sum(x > 0 for x in values) / n,
            'cumulative_log_pct': sum(math.log1p(x) for x in values) * 100,
            'compound_pct': math.expm1(sum(math.log1p(x) for x in values)) * 100}


def correlation(x, y):
    if len(x) < 2 or not statistics.pstdev(x) or not statistics.pstdev(y):
        return None
    mx, my = statistics.mean(x), statistics.mean(y)
    return sum((a-mx)*(b-my) for a, b in zip(x, y)) / math.sqrt(
        sum((a-mx)**2 for a in x) * sum((b-my)**2 for b in y))


def calculate(rows, start=None, end=None):
    if start and end and start > end:
        raise ValueError('start must not be after end')
    daily = []
    for previous, current in zip(rows, rows[1:]):
        day, opening, closing = current
        if (start and day < start) or (end and day > end):
            continue
        gap, intraday = opening / previous[2] - 1, closing / opening - 1
        total = closing / previous[2] - 1
        daily.append({'Date': day.isoformat(), 'PreviousDate': previous[0].isoformat(),
                      'gap_pct': gap * 100, 'intraday_pct': intraday * 100,
                      'close_to_close_pct': total * 100})
    if not daily:
        raise ValueError('No returns within the requested period')
    gap = [r['gap_pct'] / 100 for r in daily]
    intraday = [r['intraday_pct'] / 100 for r in daily]
    total = [r['close_to_close_pct'] / 100 for r in daily]
    summary = {'first_return_date': daily[0]['Date'], 'last_return_date': daily[-1]['Date'],
               'gap': describe(gap), 'intraday': describe(intraday),
               'close_to_close': describe(total), 'pearson_gap_intraday': correlation(gap, intraday),
               'max_compounding_identity_error': max(abs((1+g)*(1+i)-1-t)
                   for g, i, t in zip(gap, intraday, total)),
               'assumptions': ['Costs excluded; index returns are not tradable strategy returns.',
                               'naive_t assumes independent observations; not a significance verdict.',
                               'PreviousDate is the previous supplied row, not a verified exchange session.',
                               'No intraday gap-fill probability, futures matching or stock verdict analysis.']}
    return summary, daily


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('csv', type=Path)
    parser.add_argument('--start', type=date.fromisoformat)
    parser.add_argument('--end', type=date.fromisoformat)
    parser.add_argument('--daily-output', type=Path, help='New CSV path; existing files are never overwritten')
    args = parser.parse_args()
    try:
        summary, daily = calculate(read_prices(args.csv), args.start, args.end)
        summary['input_sha256'] = hashlib.sha256(args.csv.read_bytes()).hexdigest()
        summary['input_file'] = args.csv.name
        summary['requested_start'] = args.start.isoformat() if args.start else None
        summary['requested_end'] = args.end.isoformat() if args.end else None
        if args.daily_output:
            with args.daily_output.open('x', encoding='utf-8', newline='') as stream:
                writer = csv.DictWriter(stream, fieldnames=daily[0].keys())
                writer.writeheader()
                writer.writerows(daily)
        print(json.dumps(summary, ensure_ascii=False, indent=2, allow_nan=False))
    except (ValueError, OSError, KeyError, OverflowError) as exc:
        parser.exit(1, f'Input/calculation error: {exc}\n')


if __name__ == '__main__':
    main()
