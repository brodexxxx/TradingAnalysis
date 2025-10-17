def position_size(account_balance, risk_per_trade_percent, stop_loss_distance):
    """
    Calculate position size.
    """
    risk_amount = account_balance * (risk_per_trade_percent / 100)
    position_size = risk_amount / stop_loss_distance
    return position_size

def risk_management_strategies():
    """
    General strategies: Diversify, use stop losses, etc.
    """
    strategies = [
        "Diversify across assets",
        "Use stop-loss orders",
        "Risk no more than 1-2% per trade",
        "Adjust position size based on volatility"
    ]
    return strategies
