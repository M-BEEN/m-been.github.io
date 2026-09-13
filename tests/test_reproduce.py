"""Hand-calculated regression cases for the public research download."""
import importlib.util
import math
from pathlib import Path
import tempfile
import unittest
import sys

sys.dont_write_bytecode = True

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / 'static/research/gap-overnight'
spec = importlib.util.spec_from_file_location('reproduce', DATA / 'reproduce.py')
reproduce = importlib.util.module_from_spec(spec)
spec.loader.exec_module(reproduce)


class ReproductionTests(unittest.TestCase):
    def test_hand_calculated_compounding_and_log_units(self):
        summary, daily = reproduce.calculate(reproduce.read_prices(DATA / 'sample.csv'))
        self.assertEqual(len(daily), 3)
        self.assertAlmostEqual(summary['gap']['compound_pct'], 10)
        self.assertAlmostEqual(summary['intraday']['compound_pct'], -10)
        self.assertAlmostEqual(summary['close_to_close']['compound_pct'], -1)
        self.assertAlmostEqual(summary['close_to_close']['cumulative_log_pct'], 100 * math.log(.99))
        self.assertLess(summary['max_compounding_identity_error'], 1e-12)

    def test_start_date_retains_previous_close(self):
        rows = reproduce.read_prices(DATA / 'sample.csv')
        summary, daily = reproduce.calculate(rows, reproduce.date(2026, 8, 26), reproduce.date(2026, 8, 26))
        self.assertEqual(daily[0]['PreviousDate'], '2026-08-25')
        self.assertAlmostEqual(summary['intraday']['mean_pct'], -10)
        self.assertIsNone(summary['intraday']['naive_t'])

    def test_bad_prices_and_duplicate_dates_are_rejected(self):
        for bad in ('2026-08-25,nan,100', '2026-08-25,0,100', '2026-08-24,100,100'):
            with self.subTest(row=bad), tempfile.TemporaryDirectory() as tmp:
                path = Path(tmp) / 'bad.csv'
                path.write_text('Date,Open,Close\n2026-08-24,100,100\n' + bad)
                with self.assertRaises(ValueError):
                    reproduce.read_prices(path)


if __name__ == '__main__':
    unittest.main()
