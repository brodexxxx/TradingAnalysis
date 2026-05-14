import unittest

import pandas as pd

from indian_index_algo import (
    BacktestEngine,
    DataLayer,
    Monitor,
    PaperBroker,
    RiskController,
    RiskLimits,
    StrategyEvaluation,
    StrategyRegistry,
    TransactionCostModel,
)


class TestIndianIndexAlgoToolkit(unittest.TestCase):
    def test_data_quality_validation(self):
        idx = pd.date_range("2026-01-01", periods=3, freq="5min")
        data = pd.DataFrame(
            {
                "Open": [100, 101, 102],
                "High": [101, 102, 103],
                "Low": [99, 100, 101],
                "Close": [100.5, 101.2, 102.7],
                "Volume": [1000, 1200, 1100],
            },
            index=idx,
        )
        report = DataLayer().validate_ohlcv("NIFTY50", data)
        self.assertTrue(report.passed)
        self.assertEqual(report.row_count, 3)

    def test_backtest_generates_metrics(self):
        idx = pd.date_range("2026-01-01", periods=6, freq="5min")
        prices = pd.Series([100, 102, 103, 101, 99, 98], index=idx)
        signals = pd.Series(["buy", "hold", "sell", "sell", "hold", "buy"], index=idx)

        engine = BacktestEngine(cost_model=TransactionCostModel(slippage_bps=0.0, latency_bps=0.0))
        result = engine.run(prices=prices, signals=signals, initial_capital=100000, quantity=10)

        self.assertGreaterEqual(result.metrics["trades"], 1)
        self.assertIn("cagr", result.metrics)
        self.assertIn("max_drawdown", result.metrics)

    def test_risk_controller_blocks_high_risk_trade(self):
        controller = RiskController(RiskLimits(max_risk_per_trade=0.01))
        allowed, reason = controller.evaluate_trade(
            account_balance=100000,
            entry_price=100,
            stop_loss=90,
            quantity=200,
            current_exposure=0.1,
            open_positions=0,
        )
        self.assertFalse(allowed)
        self.assertEqual(reason, "Risk per trade exceeded")

    def test_paper_broker_and_monitor(self):
        broker = PaperBroker(opening_capital=100000)
        order = broker.place_order("NIFTY50", "buy", 1, 100)
        self.assertEqual(order.status, "filled")
        snapshot = broker.reconcile()
        self.assertEqual(snapshot["orders"], 1)

    def test_strategy_registry_promotes_only_when_validated(self):
        registry = StrategyRegistry()
        registry.register("breakout", "v1")

        ok = registry.promote(StrategyEvaluation("breakout", "v1", True, True))
        self.assertTrue(ok)
        self.assertEqual(registry.promoted_version("breakout"), "v1")

        not_ok = registry.promote(StrategyEvaluation("mean_reversion", "v2", True, False))
        self.assertFalse(not_ok)
        self.assertIsNone(registry.promoted_version("mean_reversion"))


if __name__ == "__main__":
    unittest.main()
