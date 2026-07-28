from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Callable, Dict, List, Optional

import numpy as np
import pandas as pd


REQUIRED_OHLCV_COLUMNS = ("Open", "High", "Low", "Close", "Volume")


class DataQualityError(ValueError):
    """Raised when market data fails validation checks."""


def validate_ohlcv_data(
    data: pd.DataFrame,
    required_columns: tuple[str, ...] = REQUIRED_OHLCV_COLUMNS,
    max_missing_ratio: float = 0.01,
) -> Dict[str, float]:
    """Validate OHLCV data quality before backtesting or live simulation."""
    if data is None or data.empty:
        raise DataQualityError("Input data is empty.")

    missing_columns = [col for col in required_columns if col not in data.columns]
    if missing_columns:
        raise DataQualityError(f"Missing required columns: {missing_columns}")

    if not data.index.is_monotonic_increasing:
        raise DataQualityError("Index must be sorted in ascending time order.")

    if data.index.has_duplicates:
        raise DataQualityError("Index contains duplicate timestamps.")

    metrics: Dict[str, float] = {}
    for col in required_columns:
        missing_ratio = float(data[col].isna().mean())
        metrics[f"missing_{col.lower()}_ratio"] = missing_ratio
        if missing_ratio > max_missing_ratio:
            raise DataQualityError(
                f"Column '{col}' missing ratio {missing_ratio:.2%} exceeds limit {max_missing_ratio:.2%}."
            )

    if (data["Volume"] < 0).any():
        raise DataQualityError("Volume must be non-negative.")

    high_ok = data["High"] >= data[["Open", "Low", "Close"]].max(axis=1)
    low_ok = data["Low"] <= data[["Open", "High", "Close"]].min(axis=1)
    if not bool(high_ok.all() and low_ok.all()):
        raise DataQualityError("OHLC consistency check failed for one or more rows.")

    return metrics


def backtest_long_only(
    data: pd.DataFrame,
    signal: pd.Series,
    initial_capital: float = 100000.0,
    transaction_cost_bps: float = 5.0,
    slippage_bps: float = 2.0,
) -> Dict[str, object]:
    """Run a simple transaction-cost-aware long-only backtest."""
    validate_ohlcv_data(data)

    if len(signal) != len(data):
        raise ValueError("Signal length must match data length.")

    close_returns = data["Close"].pct_change().fillna(0.0)
    position = signal.reindex(data.index).fillna(0.0).clip(lower=0.0, upper=1.0)
    executed_position = position.shift(1).fillna(0.0)
    turnover = executed_position.diff().abs().fillna(executed_position.abs())

    cost_rate = (transaction_cost_bps + slippage_bps) / 10000.0
    strategy_returns = executed_position * close_returns
    net_returns = strategy_returns - turnover * cost_rate

    equity_curve = initial_capital * (1.0 + net_returns).cumprod()
    running_peak = equity_curve.cummax()
    drawdown = equity_curve / running_peak - 1.0

    mean_return = float(net_returns.mean())
    std_return = float(net_returns.std(ddof=0))
    sharpe = (np.sqrt(252.0) * mean_return / std_return) if std_return > 0 else 0.0

    win_rate = float((net_returns > 0).sum() / max((net_returns != 0).sum(), 1))

    return {
        "equity_curve": equity_curve,
        "returns": net_returns,
        "total_return": float(equity_curve.iloc[-1] / initial_capital - 1.0),
        "max_drawdown": float(drawdown.min()),
        "sharpe": float(sharpe),
        "win_rate": win_rate,
        "trades": int(turnover.sum()),
        "cost_rate": cost_rate,
    }


@dataclass
class RiskController:
    max_notional: float
    max_daily_loss: float
    max_positions: int = 1
    current_positions: int = 0
    daily_pnl: float = 0.0

    def breached_daily_loss(self) -> bool:
        return self.daily_pnl <= -abs(self.max_daily_loss)

    def can_place_order(self, price: float, quantity: int, side: str = "BUY") -> bool:
        if quantity <= 0 or price <= 0:
            return False
        if self.breached_daily_loss():
            return False

        side = side.upper()
        if side == "BUY" and self.current_positions >= self.max_positions:
            return False

        notional = price * quantity
        return notional <= self.max_notional

    def register_fill(self, quantity: int, side: str) -> None:
        side = side.upper()
        if side == "BUY":
            self.current_positions += quantity
        elif side == "SELL":
            self.current_positions = max(0, self.current_positions - quantity)

    def update_daily_pnl(self, pnl: float) -> None:
        self.daily_pnl += pnl


@dataclass
class PaperBroker:
    starting_cash: float = 100000.0
    cash: float = field(init=False)
    positions: Dict[str, int] = field(default_factory=dict)
    trades: List[Dict[str, object]] = field(default_factory=list)

    def __post_init__(self) -> None:
        self.cash = self.starting_cash

    def place_order(
        self,
        symbol: str,
        side: str,
        quantity: int,
        price: float,
        timestamp: Optional[datetime] = None,
    ) -> Dict[str, object]:
        if quantity <= 0 or price <= 0:
            raise ValueError("Quantity and price must be positive.")

        side = side.upper()
        symbol = symbol.upper()
        notional = quantity * price

        if side == "BUY":
            if notional > self.cash:
                raise ValueError("Insufficient cash for buy order.")
            self.cash -= notional
            self.positions[symbol] = self.positions.get(symbol, 0) + quantity
        elif side == "SELL":
            held = self.positions.get(symbol, 0)
            if quantity > held:
                raise ValueError("Insufficient quantity for sell order.")
            self.cash += notional
            remaining = held - quantity
            if remaining:
                self.positions[symbol] = remaining
            else:
                self.positions.pop(symbol, None)
        else:
            raise ValueError("Side must be BUY or SELL.")

        trade = {
            "timestamp": timestamp or datetime.now(timezone.utc),
            "symbol": symbol,
            "side": side,
            "quantity": quantity,
            "price": price,
            "notional": notional,
            "cash_after": self.cash,
        }
        self.trades.append(trade)
        return trade

    def portfolio_value(self, latest_prices: Dict[str, float]) -> float:
        holdings = sum(
            quantity * latest_prices.get(symbol, 0.0)
            for symbol, quantity in self.positions.items()
        )
        return self.cash + holdings


@dataclass
class PerformanceMonitor:
    min_sharpe: float = 0.8
    max_drawdown: float = -0.15
    min_win_rate: float = 0.45

    def evaluate(self, metrics: Dict[str, float]) -> Dict[str, object]:
        checks = {
            "sharpe_ok": metrics.get("sharpe", 0.0) >= self.min_sharpe,
            "drawdown_ok": metrics.get("max_drawdown", -1.0) >= self.max_drawdown,
            "win_rate_ok": metrics.get("win_rate", 0.0) >= self.min_win_rate,
        }
        return {
            "checks": checks,
            "promotable": all(checks.values()),
        }


@dataclass
class StrategyRegistry:
    strategies: Dict[str, Callable[[pd.DataFrame], pd.Series]] = field(default_factory=dict)

    def register(self, name: str, strategy: Callable[[pd.DataFrame], pd.Series]) -> None:
        self.strategies[name] = strategy

    def run(self, name: str, data: pd.DataFrame) -> pd.Series:
        if name not in self.strategies:
            raise KeyError(f"Unknown strategy: {name}")
        return self.strategies[name](data)

    def can_promote(
        self,
        metrics: Dict[str, float],
        monitor: Optional[PerformanceMonitor] = None,
    ) -> bool:
        monitor = monitor or PerformanceMonitor()
        return bool(monitor.evaluate(metrics)["promotable"])
