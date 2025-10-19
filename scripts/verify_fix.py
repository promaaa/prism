#!/usr/bin/env python3

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from prism.api.stock_api import StockAPI

if __name__ == "__main__":
    api = StockAPI()
    print("--- Testing LVMH.PA ---")
    lvmh_price = api.get_price("LVMH.PA")
    print(f"LVMH stock price: €{lvmh_price}")

    print("--- Testing AAPL ---")
    aapl_price = api.get_price("AAPL")
    print(f"Apple stock price: ${aapl_price}")
