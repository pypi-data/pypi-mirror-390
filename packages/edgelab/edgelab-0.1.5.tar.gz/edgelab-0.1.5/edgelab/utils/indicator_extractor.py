"""Extract required indicators from strategy code."""

import re
import json
from typing import Dict, List, Any


def extract_indicators_from_code(code: str) -> Dict[str, List[Dict[str, Any]]]:
    """Extract indicator calls from strategy code.

    Args:
        code: Strategy Python code as string

    Returns:
        Dict mapping indicator names to list of parameter dicts
        Example: {
            "rsi": [{"period": 14}],
            "ema": [{"period": 20}, {"period": 50}],
            "macd": [{"fast": 12, "slow": 26, "signal": 9}]
        }
    """
    # Regex to match self.indicators.indicator_name(params)
    pattern = r'self\.indicators\.(\w+)\((.*?)\)'
    matches = re.findall(pattern, code)

    indicators = {}

    for indicator_name, params_str in matches:
        # Parse parameters
        param_dict = _parse_params(params_str)

        # Add to indicators dict
        if indicator_name not in indicators:
            indicators[indicator_name] = []

        # Avoid duplicates (same indicator with same params)
        if param_dict not in indicators[indicator_name]:
            indicators[indicator_name].append(param_dict)

    return indicators


def _parse_params(params_str: str) -> Dict[str, Any]:
    """Parse parameter string into dict.

    Args:
        params_str: String like "period=14" or "fast=12, slow=26, signal=9"

    Returns:
        Dict like {"period": 14} or {"fast": 12, "slow": 26, "signal": 9}
    """
    param_dict = {}

    if not params_str.strip():
        return param_dict

    for param in params_str.split(','):
        param = param.strip()
        if '=' in param:
            key, val = param.split('=', 1)
            key = key.strip()
            val = val.strip()

            # Try to convert to int/float
            try:
                if '.' in val:
                    param_dict[key] = float(val)
                else:
                    param_dict[key] = int(val)
            except ValueError:
                # Keep as string if not numeric
                param_dict[key] = val.strip('"\'')
        else:
            # Positional argument (e.g., rsi(14) without period=)
            # Try to parse as number
            try:
                if '.' in param:
                    param_dict['_positional'] = float(param)
                else:
                    param_dict['_positional'] = int(param)
            except ValueError:
                # Skip if not parseable
                pass

    return param_dict


# Example usage
if __name__ == "__main__":
    example_code = """
    def on_bar(self, bar: Bar) -> Optional[SignalType]:
        rsi = self.indicators.rsi(period=14)
        ema_20 = self.indicators.ema(period=20)
        ema_50 = self.indicators.ema(period=50)
        macd = self.indicators.macd(fast=12, slow=26, signal=9)
        bb = self.indicators.bollinger_bands(period=20, std=2)

        if rsi < 30:
            return SignalType.LONG
        return None
    """

    result = extract_indicators_from_code(example_code)
    print(json.dumps(result, indent=2))

    # Output:
    # {
    #   "rsi": [{"period": 14}],
    #   "ema": [{"period": 20}, {"period": 50}],
    #   "macd": [{"fast": 12, "slow": 26, "signal": 9}],
    #   "bollinger_bands": [{"period": 20, "std": 2}]
    # }

