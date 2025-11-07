import numba
import numpy as np


@numba.njit
def simulate(
    sim_data: np.ndarray,
    timeout: int,
    take_profit: float,
    stop_loss: float,
    fee: float,
    init_cash=10e3,
    min_cash=10,
    alloc_ratio=0.01,
    min_pos=0.5,
):
    worth = cash_left = init_cash
    open_trades = {}
    done_trades = []

    TIME, SYMBOL, FIELD = sim_data.shape
    sim_data[:, :, 2] = np.round(sim_data[:, :, 2], 2)

    for t in range(TIME):

        for id, trade in list(open_trades.items()):
            t1, s1, pos1, price1, cash1 = trade[:5]
            time2, price2, _ = sim_data[t, int(s1)]
            dt = t - t1
            pr = np.sign(pos1) * (price2 / price1 - 1) - fee
            if dt >= timeout or pr >= take_profit or pr <= stop_loss:
                cash_left += cash1 * (1 + pr)
                worth += cash1 * pr
                del open_trades[id]
                trade[-3:] = dt, pr, worth
                done_trades.append(trade)

        for s in range(SYMBOL):
            time, price, pos = sim_data[t, s]
            if abs(pos) >= min_pos:
                cash = int(min(cash_left, worth * alloc_ratio * abs(pos)))
                id = int((s + 1) * np.sign(pos))
                if cash >= min_cash and id not in open_trades:
                    cash_left -= cash
                    open_trades[id] = np.array([t, s, pos, price, cash, 0.0, 0.0, 0.0])

    return done_trades
