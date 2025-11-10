"""
EMA Crossover Strategy

A trend-following strategy using exponential moving average crossovers.

Entry Rules:
- Buy when fast EMA crosses above slow EMA (golden cross)
- Sell when fast EMA crosses below slow EMA (death cross)

Parameters:
- Fast EMA: 12 periods
- Slow EMA: 26 periods

Exit Rules:
- 3% stop loss
- 6% take profit
"""

from typing import Optional


class EMACrossover:
    """Trend following strategy using EMA crossovers."""

    def __init__(self):
        """Initialize strategy state."""
        self.prev_fast_ema = None
        self.prev_slow_ema = None

    @property
    def name(self) -> str:
        """Strategy name."""
        return "ema_crossover"

    @property
    def version(self) -> str:
        """Strategy version."""
        return "v1"

    def on_bar(self, bar) -> Optional[str]:
        """Process each bar and generate trading signals.

        Args:
            bar: OHLCV bar with time, open, high, low, close, volume

        Returns:
            "long" for buy signal (golden cross)
            "short" for sell signal (death cross)
            None for no signal
        """
        # Calculate EMAs
        fast_ema = self.indicators.ema(period=12)
        slow_ema = self.indicators.ema(period=26)

        # Need previous values to detect crossover
        if self.prev_fast_ema is None or self.prev_slow_ema is None:
            self.prev_fast_ema = fast_ema
            self.prev_slow_ema = slow_ema
            return None

        signal = None

        # Golden cross: fast EMA crosses above slow EMA
        if self.prev_fast_ema <= self.prev_slow_ema and fast_ema > slow_ema:
            signal = "long"

        # Death cross: fast EMA crosses below slow EMA
        elif self.prev_fast_ema >= self.prev_slow_ema and fast_ema < slow_ema:
            signal = "short"

        # Update previous values
        self.prev_fast_ema = fast_ema
        self.prev_slow_ema = slow_ema

        return signal

    def stop_loss(self, entry_price: float) -> float:
        """Calculate stop loss price.

        Args:
            entry_price: Price at which position was entered

        Returns:
            Stop loss price (3% below entry)
        """
        return entry_price * 0.97

    def take_profit(self, entry_price: float) -> float:
        """Calculate take profit price.

        Args:
            entry_price: Price at which position was entered

        Returns:
            Take profit price (6% above entry)
        """
        return entry_price * 1.06
