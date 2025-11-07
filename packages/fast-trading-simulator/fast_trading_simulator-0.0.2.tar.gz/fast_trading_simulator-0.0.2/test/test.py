from typing import Dict

import numpy as np
from crypto_data_downloader.utils import load_pkl
from trading_models.utils import plot_general

from fast_trading_simulator.simulate import simulate

data: Dict = load_pkl("futures_sim_data_2025-07-01_2025-08-01.pkl", gz=True)
sim_data: Dict[str, Dict[str, np.ndarray]] = data["sim_data"]
# for sym, x in sim_data.items():
#     x["position"] = custom_strategy(x["close"])
symbols = list(sim_data.keys())
fields = list(sim_data["BTCUSDT"].keys())
arr = np.array([list(x.values()) for x in sim_data.values()])
arr = arr.transpose((2, 0, 1))

print(f"data keys: {list(data.keys())}")
print(f"arr.shape: {arr.shape} (time, symbols, fields)")
print(f"{len(symbols)} symbols: {symbols[:3]}...")
print(f"{len(fields)} fields: {fields}")
"""
timeout: int, number of time steps
take_profit: float, e.g. 0.01 (1%)
stop_loss: float, e.g. -0.3 (-30%)
fee: float, buy+sell total, e.g. 7e-4 (0.07%)
"""

data["sim_data"] = arr
trades = np.array(simulate(**data, init_cash=10e3, alloc_ratio=0.005))
plots = {
    f"worth ({len(trades)} trades)": trades[:, -1],
    "position_hist": trades[:, 2],
    "duration_hist": trades[:, -3],
    "profit_hist": trades[:, -2],
}
plot_general(plots, "simulate")
