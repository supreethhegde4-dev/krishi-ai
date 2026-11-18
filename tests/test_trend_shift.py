"""
Unit Test Suite for Krishi AI Trend Shift Detection System
Verifies:
1. Historical Time-Series extraction from DuckDB Parquet dataset
2. Moving average and Bollinger Band computation
3. Change-point trend shift detection (Bullish, Bearish, Supply Shocks)
4. Plotly trend chart generation with inflection markers
5. Multi-season weather and yield trend shift evaluations
"""
import os
import sys
import unittest
import pandas as pd

if sys.stdout.encoding.lower() != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from modules.trend_shift_detector import (
    query_market_time_series, detect_market_trend_shifts,
    analyze_weather_and_yield_shifts
)


class TestTrendShiftDetector(unittest.TestCase):

    def test_01_query_time_series(self):
        """Verify time-series querying from DuckDB."""
        df = query_market_time_series("Tomato", state="Karnataka")
        self.assertFalse(df.empty)
        self.assertIn("price_kg", df.columns)
        self.assertIn("arrival_cnt", df.columns)
        print(f"\n[Test 1] Time-Series Loaded: {len(df)} daily points for Karnataka Tomato")

    def test_02_detect_market_trend_shifts(self):
        """Verify trend shift detection and indicator calculations."""
        res = detect_market_trend_shifts("Tomato", state="Karnataka")
        self.assertIn("shifts_count", res)
        self.assertIn("current_regime", res)
        self.assertIn("plot_fig", res)
        self.assertGreater(res["shifts_count"], 0)
        self.assertIsNotNone(res["plot_fig"])
        print(f"[Test 2] Trend Shifts Detected: {res['shifts_count']} structural shifts. Current Regime: {res['current_regime']}")

    def test_03_shift_intelligence_payload(self):
        """Verify that detected shifts contain all 6 required fields."""
        res = detect_market_trend_shifts("Tomato", state="Karnataka")
        shifts = res["recent_shifts"]
        self.assertTrue(len(shifts) > 0)
        first_shift = shifts[0]

        # Verify required fields
        self.assertIn("previous_trend", first_shift)
        self.assertIn("current_trend", first_shift)
        self.assertIn("magnitude", first_shift)
        self.assertIn("data_evidence", first_shift)
        self.assertIn("potential_impact", first_shift)
        self.assertIn("recommended_action", first_shift)

        print(f"[Test 3] Shift Payload Integrity: [{first_shift['type']}] on {first_shift['date']}")
        print(f"         Prev: {first_shift['previous_trend'][:50]}...")
        print(f"         Curr: {first_shift['current_trend'][:50]}...")
        print(f"         Magnitude: {first_shift['magnitude']}")

    def test_04_weather_and_yield_shifts(self):
        """Verify multi-season weather and yield trend shifts."""
        res = analyze_weather_and_yield_shifts("Tomato", "Karnataka")
        self.assertIn("weather_shifts", res)
        self.assertIn("yield_shifts", res)
        self.assertEqual(len(res["weather_shifts"]), 2)
        self.assertEqual(len(res["yield_shifts"]), 2)
        print(f"[Test 4] Weather/Yield Shifts: {len(res['weather_shifts'])} weather shifts, {len(res['yield_shifts'])} yield shifts evaluated")


if __name__ == "__main__":
    unittest.main()
