"""
Simple RSI Mean Reversion Strategy

A basic momentum strategy using the Relative Strength Index (RSI) to identify
oversold and overbought conditions.

Entry Rules:
- Buy when RSI < 30 (oversold)
- Sell when RSI > 70 (overbought)

Exit Rules:
- 2% stop loss
- 5% take profit
"""

from typing import Optional


class SimpleRSI:
    """Mean reversion strategy using RSI indicator."""

    def __init__(self):
        """Initialize strategy state."""
        pass

    @property
    def name(self) -> str:
        """Strategy name."""
        return "simple_rsi"

    @property
    def version(self) -> str:
        """Strategy version."""
        return "v1"

    def on_bar(self, bar) -> Optional[str]:
        """Process each bar and generate trading signals.

        Args:
            bar: OHLCV bar with time, open, high, low, close, volume

        Returns:
            "long" for buy signal
            "short" for sell signal
            None for no signal
        """
        # Calculate RSI using 14-period lookback
        rsi = self.indicators.rsi(period=14)

        # Trading logic
        if rsi < 30:
            return "long"  # Oversold - buy
        elif rsi > 70:
            return "short"  # Overbought - sell
        else:
            return None  # No signal - hold

    def stop_loss(self, entry_price: float) -> float:
        """Calculate stop loss price.

        Args:
            entry_price: Price at which position was entered

        Returns:
            Stop loss price (2% below entry)
        """
        return entry_price * 0.98

    def take_profit(self, entry_price: float) -> float:
        """Calculate take profit price.

        Args:
            entry_price: Price at which position was entered

        Returns:
            Take profit price (5% above entry)
        """
        return entry_price * 1.05
