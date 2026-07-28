import unittest

import pandas as pd

from indian_index_algo import (
    DataQualityError,
    PaperBroker,
    PerformanceMonitor,
    RiskController,
    StrategyRegistry,
    backtest_long_only,
    validate_ohlcv_data,
)


class IndianIndexAlgoTests(unittest.TestCase):
    def setUp(self):
        self.data = pd.DataFrame(
            {
                "Open": [100, 101, 102, 103, 104],
                "High": [101, 102, 103, 104, 105],
                "Low": [99, 100, 101, 102, 103],
                "Close": [100, 102, 101, 104, 105],
                "Volume": [1000, 1200, 1100, 1300, 1400],
            },
            index=pd.date_range("2024-01-01", periods=5, freq="D"),
        )

    def test_validate_ohlcv_data_rejects_bad_volume(self):
        bad_data = self.data.copy()
        bad_data.loc[bad_data.index[0], "Volume"] = -1
        with self.assertRaises(DataQualityError):
            validate_ohlcv_data(bad_data)

    def test_backtest_contains_core_metrics_and_costs_impact_returns(self):
        signal = pd.Series([0, 1, 1, 0, 1], index=self.data.index)
        low_cost = backtest_long_only(self.data, signal, transaction_cost_bps=0, slippage_bps=0)
        high_cost = backtest_long_only(self.data, signal, transaction_cost_bps=20, slippage_bps=10)

        for key in ["equity_curve", "returns", "total_return", "max_drawdown", "sharpe", "win_rate", "trades"]:
            self.assertIn(key, low_cost)

        self.assertLess(high_cost["total_return"], low_cost["total_return"])

    def test_risk_controller_blocks_after_daily_loss_limit(self):
        risk = RiskController(max_notional=50000, max_daily_loss=1000, max_positions=1)
        self.assertTrue(risk.can_place_order(price=100, quantity=10, side="BUY"))
        risk.update_daily_pnl(-1200)
        self.assertFalse(risk.can_place_order(price=100, quantity=10, side="BUY"))

    def test_paper_broker_executes_and_updates_positions(self):
        broker = PaperBroker(starting_cash=10000)
        broker.place_order("NIFTYBEES", "BUY", 10, 100)
        broker.place_order("NIFTYBEES", "SELL", 5, 120)

        self.assertEqual(broker.positions["NIFTYBEES"], 5)
        self.assertEqual(len(broker.trades), 2)
        self.assertEqual(broker.cash, 9600)

    def test_strategy_promotion_gating(self):
        registry = StrategyRegistry()
        monitor = PerformanceMonitor(min_sharpe=1.0, max_drawdown=-0.2, min_win_rate=0.5)

        good_metrics = {"sharpe": 1.2, "max_drawdown": -0.1, "win_rate": 0.6}
        bad_metrics = {"sharpe": 0.4, "max_drawdown": -0.3, "win_rate": 0.4}

        self.assertTrue(registry.can_promote(good_metrics, monitor=monitor))
        self.assertFalse(registry.can_promote(bad_metrics, monitor=monitor))


if __name__ == "__main__":
    unittest.main()
