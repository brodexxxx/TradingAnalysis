from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, datetime
from enum import Enum
from math import sqrt
from typing import Dict, List, Optional, Tuple

import pandas as pd
import pytz

from data_fetcher import get_fo_data, get_historical_data, get_realtime_data


class TradingMode(str, Enum):
    SIGNALS_ONLY = "signals_only"
    PAPER = "paper"
    LIVE = "live"


@dataclass
class TradingScope:
    instruments: Tuple[str, ...] = ("NIFTY50", "SENSEX")
    include_options: bool = True
    include_futures: bool = True
    include_cash: bool = True
    timeframe: str = "intraday"
    mode: TradingMode = TradingMode.PAPER


@dataclass
class BrokerConfig:
    name: str = "paper"
    max_order_retries: int = 3
    allow_live_orders: bool = False


@dataclass
class DataQualityReport:
    symbol: str
    passed: bool
    row_count: int
    missing_ratio: float
    duplicate_timestamps: int
    monotonic_index: bool
    issues: List[str] = field(default_factory=list)


class IndianMarketCompliance:
    """Simple NSE/BSE session checks and holiday support."""

    def __init__(self, holidays: Optional[List[date]] = None):
        self.ist = pytz.timezone("Asia/Kolkata")
        self.holidays = set(holidays or [])

    def is_trading_day(self, ts: Optional[datetime] = None) -> bool:
        now = ts.astimezone(self.ist) if ts else datetime.now(self.ist)
        return now.weekday() < 5 and now.date() not in self.holidays

    def is_market_open(self, ts: Optional[datetime] = None) -> bool:
        now = ts.astimezone(self.ist) if ts else datetime.now(self.ist)
        if not self.is_trading_day(now):
            return False
        market_open = now.replace(hour=9, minute=15, second=0, microsecond=0)
        market_close = now.replace(hour=15, minute=30, second=0, microsecond=0)
        return market_open <= now <= market_close


class SymbolMapper:
    SYMBOLS = {
        "NIFTY50": "NIFTY50.NS",
        "SENSEX": "SENSEX.NS",
        "BANKNIFTY": "BANKNIFTY.NS",
    }

    DERIVATIVE_ROOTS = {
        "NIFTY50": "NIFTY",
        "SENSEX": "SENSEX",
        "BANKNIFTY": "BANKNIFTY",
    }

    @classmethod
    def resolve_spot_symbol(cls, symbol: str) -> str:
        return cls.SYMBOLS.get(symbol.upper(), symbol)

    @classmethod
    def resolve_derivative_root(cls, symbol: str) -> str:
        return cls.DERIVATIVE_ROOTS.get(symbol.upper(), symbol.upper())


class DataLayer:
    REQUIRED_COLUMNS = {"Open", "High", "Low", "Close", "Volume"}

    def fetch_spot_data(
        self,
        symbol: str,
        intraday: bool = True,
        period: str = "1d",
        interval: str = "5m",
        years: int = 1,
    ) -> pd.DataFrame:
        mapped_symbol = SymbolMapper.resolve_spot_symbol(symbol)
        if intraday:
            return get_realtime_data(mapped_symbol, period=period, interval=interval)
        return get_historical_data(mapped_symbol, years=years)

    def fetch_derivatives_data(self, symbol: str) -> pd.DataFrame:
        root = SymbolMapper.resolve_derivative_root(symbol)
        return get_fo_data(root)

    def validate_ohlcv(self, symbol: str, data: pd.DataFrame) -> DataQualityReport:
        issues: List[str] = []

        if data.empty:
            return DataQualityReport(
                symbol=symbol,
                passed=False,
                row_count=0,
                missing_ratio=1.0,
                duplicate_timestamps=0,
                monotonic_index=True,
                issues=["No rows returned"],
            )

        missing_columns = self.REQUIRED_COLUMNS - set(data.columns)
        if missing_columns:
            issues.append(f"Missing columns: {sorted(missing_columns)}")

        working = data[[c for c in self.REQUIRED_COLUMNS if c in data.columns]].copy()
        missing_ratio = float(working.isnull().mean().mean()) if not working.empty else 1.0
        duplicate_timestamps = int(data.index.duplicated().sum()) if isinstance(data.index, pd.Index) else 0
        monotonic_index = bool(data.index.is_monotonic_increasing) if isinstance(data.index, pd.Index) else False

        if missing_ratio > 0.05:
            issues.append(f"High null ratio: {missing_ratio:.2%}")
        if duplicate_timestamps > 0:
            issues.append(f"Duplicate timestamps: {duplicate_timestamps}")
        if not monotonic_index:
            issues.append("Index is not monotonic increasing")

        if "Low" in data and "High" in data and (data["Low"] > data["High"]).any():
            issues.append("Detected rows where Low > High")
        if "Close" in data and (data["Close"] <= 0).any():
            issues.append("Detected non-positive Close prices")

        return DataQualityReport(
            symbol=symbol,
            passed=len(issues) == 0,
            row_count=len(data),
            missing_ratio=missing_ratio,
            duplicate_timestamps=duplicate_timestamps,
            monotonic_index=monotonic_index,
            issues=issues,
        )


@dataclass
class TransactionCostModel:
    brokerage_rate: float = 0.0003
    exchange_txn_rate: float = 0.000035
    sebi_rate: float = 0.000001
    stt_rate: float = 0.000625
    stamp_duty_rate: float = 0.00003
    gst_rate: float = 0.18
    slippage_bps: float = 2.0
    latency_bps: float = 0.5

    def estimate_side_cost(self, notional: float) -> float:
        brokerage = notional * self.brokerage_rate
        exchange = notional * self.exchange_txn_rate
        sebi = notional * self.sebi_rate
        stt = notional * self.stt_rate
        stamp = notional * self.stamp_duty_rate
        gst = self.gst_rate * (brokerage + exchange)
        impact = notional * ((self.slippage_bps + self.latency_bps) / 10_000)
        return brokerage + exchange + sebi + stt + stamp + gst + impact

    def estimate_round_trip(self, notional: float) -> float:
        return self.estimate_side_cost(notional) * 2


@dataclass
class BacktestTrade:
    entry_time: pd.Timestamp
    entry_price: float
    side: str
    quantity: int
    exit_time: Optional[pd.Timestamp] = None
    exit_price: Optional[float] = None
    pnl: float = 0.0
    costs: float = 0.0


@dataclass
class BacktestResult:
    trades: List[BacktestTrade]
    equity_curve: pd.Series
    metrics: Dict[str, float]


class BacktestEngine:
    """Vector-light backtester with Indian market transaction cost assumptions."""

    def __init__(self, cost_model: Optional[TransactionCostModel] = None):
        self.cost_model = cost_model or TransactionCostModel()

    def run(
        self,
        prices: pd.Series,
        signals: pd.Series,
        initial_capital: float = 1_000_000.0,
        quantity: int = 1,
    ) -> BacktestResult:
        if prices.empty:
            return BacktestResult([], pd.Series(dtype=float), self._empty_metrics())

        prices = prices.dropna()
        signals = signals.reindex(prices.index).fillna("hold").str.lower()

        equity = initial_capital
        equity_points = []
        trades: List[BacktestTrade] = []
        open_trade: Optional[BacktestTrade] = None

        for ts, price in prices.items():
            signal = signals.loc[ts]

            if open_trade is None and signal in {"buy", "sell"}:
                open_trade = BacktestTrade(entry_time=ts, entry_price=float(price), side=signal, quantity=quantity)
                entry_notional = float(price) * quantity
                open_trade.costs += self.cost_model.estimate_side_cost(entry_notional)

            elif open_trade is not None and signal in {"buy", "sell"} and signal != open_trade.side:
                self._close_trade(open_trade, ts, float(price))
                trades.append(open_trade)
                equity += open_trade.pnl - open_trade.costs
                open_trade = BacktestTrade(entry_time=ts, entry_price=float(price), side=signal, quantity=quantity)
                open_trade.costs += self.cost_model.estimate_side_cost(float(price) * quantity)

            mtm = equity
            if open_trade is not None:
                mtm += self._floating_pnl(open_trade, float(price))
            equity_points.append((ts, mtm))

        if open_trade is not None:
            last_ts = prices.index[-1]
            self._close_trade(open_trade, last_ts, float(prices.iloc[-1]))
            trades.append(open_trade)
            equity += open_trade.pnl - open_trade.costs

        equity_curve = pd.Series({ts: v for ts, v in equity_points}, dtype=float).sort_index()
        metrics = self._compute_metrics(initial_capital, equity_curve, trades)
        return BacktestResult(trades=trades, equity_curve=equity_curve, metrics=metrics)

    def _floating_pnl(self, trade: BacktestTrade, current_price: float) -> float:
        delta = current_price - trade.entry_price
        if trade.side == "sell":
            delta *= -1
        return delta * trade.quantity

    def _close_trade(self, trade: BacktestTrade, ts: pd.Timestamp, price: float) -> None:
        trade.exit_time = ts
        trade.exit_price = price
        delta = price - trade.entry_price
        if trade.side == "sell":
            delta *= -1
        trade.pnl = delta * trade.quantity
        trade.costs += self.cost_model.estimate_side_cost(price * trade.quantity)

    def _compute_metrics(
        self,
        initial_capital: float,
        equity_curve: pd.Series,
        trades: List[BacktestTrade],
    ) -> Dict[str, float]:
        if equity_curve.empty:
            return self._empty_metrics()

        final_equity = float(equity_curve.iloc[-1])
        periods = max(len(equity_curve), 2)
        years = periods / (252 * 75)
        cagr = ((final_equity / initial_capital) ** (1 / years) - 1) if years > 0 else 0.0

        rets = equity_curve.pct_change().dropna()
        sharpe = (rets.mean() / rets.std() * sqrt(252)) if not rets.empty and rets.std() > 0 else 0.0

        rolling_max = equity_curve.cummax()
        drawdowns = equity_curve / rolling_max - 1
        max_drawdown = float(drawdowns.min()) if not drawdowns.empty else 0.0

        wins = [t for t in trades if (t.pnl - t.costs) > 0]
        win_rate = len(wins) / len(trades) if trades else 0.0

        max_loss_streak = 0
        current_streak = 0
        for t in trades:
            if (t.pnl - t.costs) < 0:
                current_streak += 1
                max_loss_streak = max(max_loss_streak, current_streak)
            else:
                current_streak = 0

        return {
            "cagr": float(cagr),
            "sharpe": float(sharpe),
            "max_drawdown": float(max_drawdown),
            "win_rate": float(win_rate),
            "max_loss_streak": float(max_loss_streak),
            "final_equity": float(final_equity),
            "trades": float(len(trades)),
        }

    @staticmethod
    def _empty_metrics() -> Dict[str, float]:
        return {
            "cagr": 0.0,
            "sharpe": 0.0,
            "max_drawdown": 0.0,
            "win_rate": 0.0,
            "max_loss_streak": 0.0,
            "final_equity": 0.0,
            "trades": 0.0,
        }


@dataclass
class RiskLimits:
    max_risk_per_trade: float = 0.02
    max_daily_loss: float = 0.03
    max_exposure: float = 0.50
    max_open_positions: int = 3
    circuit_breaker_drawdown: float = 0.06


class RiskController:
    def __init__(self, limits: Optional[RiskLimits] = None):
        self.limits = limits or RiskLimits()
        self.daily_realized_pnl = 0.0
        self.kill_switch_active = False

    def update_realized_pnl(self, pnl: float, account_balance: float) -> None:
        self.daily_realized_pnl += pnl
        if account_balance > 0 and (self.daily_realized_pnl / account_balance) <= -self.limits.max_daily_loss:
            self.kill_switch_active = True

    def evaluate_trade(
        self,
        account_balance: float,
        entry_price: float,
        stop_loss: float,
        quantity: int,
        current_exposure: float,
        open_positions: int,
    ) -> Tuple[bool, str]:
        if self.kill_switch_active:
            return False, "Kill switch active"

        if open_positions >= self.limits.max_open_positions:
            return False, "Max open positions reached"

        if current_exposure >= self.limits.max_exposure:
            return False, "Max exposure reached"

        risk_per_unit = abs(entry_price - stop_loss)
        risk_notional = risk_per_unit * quantity
        if account_balance <= 0:
            return False, "Invalid account balance"

        if (risk_notional / account_balance) > self.limits.max_risk_per_trade:
            return False, "Risk per trade exceeded"

        return True, "OK"


@dataclass
class Order:
    symbol: str
    side: str
    quantity: int
    price: float
    status: str = "filled"
    created_at: datetime = field(default_factory=lambda: datetime.now(pytz.UTC))


class PaperBroker:
    def __init__(self, opening_capital: float = 1_000_000.0):
        self.cash = opening_capital
        self.positions: Dict[str, int] = {}
        self.avg_price: Dict[str, float] = {}
        self.orders: List[Order] = []

    def place_order(self, symbol: str, side: str, quantity: int, price: float) -> Order:
        side = side.lower()
        if quantity <= 0 or price <= 0:
            return Order(symbol=symbol, side=side, quantity=quantity, price=price, status="rejected")

        signed_qty = quantity if side == "buy" else -quantity
        trade_value = quantity * price

        if side == "buy" and trade_value > self.cash:
            return Order(symbol=symbol, side=side, quantity=quantity, price=price, status="rejected")

        prev_qty = self.positions.get(symbol, 0)
        new_qty = prev_qty + signed_qty

        if side == "buy":
            self.cash -= trade_value
        else:
            self.cash += trade_value

        if new_qty == 0:
            self.positions.pop(symbol, None)
            self.avg_price.pop(symbol, None)
        else:
            if side == "buy":
                prev_value = prev_qty * self.avg_price.get(symbol, 0.0)
                self.avg_price[symbol] = (prev_value + trade_value) / max(new_qty, 1)
            self.positions[symbol] = new_qty

        order = Order(symbol=symbol, side=side, quantity=quantity, price=price, status="filled")
        self.orders.append(order)
        return order

    def mark_to_market(self, latest_prices: Dict[str, float]) -> float:
        value = self.cash
        for sym, qty in self.positions.items():
            value += qty * latest_prices.get(sym, self.avg_price.get(sym, 0.0))
        return value

    def reconcile(self) -> Dict[str, object]:
        return {
            "cash": self.cash,
            "positions": dict(self.positions),
            "orders": len(self.orders),
        }


@dataclass
class HealthSnapshot:
    timestamp: datetime
    market_open: bool
    data_ok: bool
    kill_switch: bool
    open_positions: int
    daily_realized_pnl: float
    notes: List[str]


class Monitor:
    def build_snapshot(
        self,
        compliance: IndianMarketCompliance,
        quality: DataQualityReport,
        risk: RiskController,
        broker: PaperBroker,
    ) -> HealthSnapshot:
        notes = list(quality.issues)
        return HealthSnapshot(
            timestamp=datetime.now(pytz.UTC),
            market_open=compliance.is_market_open(),
            data_ok=quality.passed,
            kill_switch=risk.kill_switch_active,
            open_positions=len(broker.positions),
            daily_realized_pnl=risk.daily_realized_pnl,
            notes=notes,
        )

    @staticmethod
    def daily_report(snapshot: HealthSnapshot) -> str:
        issues = ", ".join(snapshot.notes) if snapshot.notes else "None"
        return (
            f"Health @ {snapshot.timestamp.isoformat()} | market_open={snapshot.market_open} | "
            f"data_ok={snapshot.data_ok} | kill_switch={snapshot.kill_switch} | "
            f"open_positions={snapshot.open_positions} | daily_pnl={snapshot.daily_realized_pnl:.2f} | "
            f"issues={issues}"
        )


@dataclass
class StrategyEvaluation:
    strategy_name: str
    version: str
    out_of_sample_passed: bool
    walk_forward_passed: bool


class StrategyRegistry:
    def __init__(self):
        self._versions: Dict[str, str] = {}
        self._promoted: Dict[str, str] = {}

    def register(self, strategy_name: str, version: str) -> None:
        self._versions[strategy_name] = version

    def promote(self, evaluation: StrategyEvaluation) -> bool:
        if evaluation.out_of_sample_passed and evaluation.walk_forward_passed:
            self._promoted[evaluation.strategy_name] = evaluation.version
            return True
        return False

    def promoted_version(self, strategy_name: str) -> Optional[str]:
        return self._promoted.get(strategy_name)
