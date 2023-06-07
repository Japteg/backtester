import pandas as pd
import matplotlib.pyplot as plot
from strategies.constants import INSTRUMENTS, LOT_SIZE

"""
Metrics:
1. Overall profit
2. Avg expiry profit
3. Avg day profit
4. Max profit
5. Max loss
6. Total expiries
7. Win % (Days)
8. Loss % (Days)
9. Avg profit on win days
10. Avg loss on loss days
11. Lot size
12. Max drawdown (MDD recovery period)
13. Return to MDD ratio
14. Max wining streak
15. Max lossing streak
16. Expectancy
"""


day_end_log = pd.read_csv("../strategies/short_straddle/"
                                 "results/intraday_trade_log.csv")

# print(intraday_trade_log.info())
# intraday_trade_log['PnL'].cumsum().plot()
# plot.show()

# TODO: include slippages


def filter_na_rows(data):
    return data.dropna()


total_trading_days = 0
lots = 1
quantity = lots * LOT_SIZE[INSTRUMENTS.BANKNIFTY]
total_profit = 0
max_profit = 0
total_expiries = 0
max_loss = 0
avg_day_profit = 0
avg_expiry_profit = 0
win_days = 0
win_day_profits = 0
win_percentage = 0
loss_days = 0
loss_day_losses = 0
loss_percentage = 0
avg_profit_on_win_days = 0
avg_loss_on_loss_day = 0
max_wining_streak = 0
max_losing_streak = 0

win_streak = 0
loss_streak = 0
for index, row in day_end_log.iterrows():
    pnl = row["PnL"] * quantity
    total_trading_days += 1
    total_profit += pnl
    max_profit = max(max_profit, pnl)
    max_loss = min(max_loss, pnl)

    if pnl >= 0:
        win_days += 1
        win_day_profits += pnl
        win_streak += 1
        max_wining_streak = max(max_wining_streak, win_streak)
        loss_streak = 0
    else:
        loss_days += 1
        loss_day_losses += pnl
        loss_streak += 1
        max_losing_streak = max(max_losing_streak, loss_streak)
        win_streak = 0

avg_day_profit = round(total_profit / total_trading_days, 2)
avg_profit_on_win_days = round(win_day_profits / win_days, 2)
avg_loss_on_loss_day = round(loss_day_losses / loss_days, 2)
win_rate = win_days / total_trading_days
win_percentage = round((win_days / total_trading_days) * 100, 2)
loss_percentage = round((loss_days / total_trading_days) * 100, 2)

risk_reward = abs(avg_profit_on_win_days / avg_loss_on_loss_day)
expectancy = round((win_rate*risk_reward) - ((1-win_rate)*1), 2)


# Print metrics
print(f'total trading days: {total_trading_days}')
print(f'lots: {lots}')
print(f'quantity: {quantity}')
print(f'total_profit: {round(total_profit,2)}')
print(f'Avg profit: {avg_day_profit}')
print(f'max profit: {max_profit}')
print(f'max loss: {max_loss}')
print(f'win days: {win_days}')
print(f'avg profit on win days: {avg_profit_on_win_days}')
print(f'win percentage: {win_percentage}%')
print(f'loss days: {loss_days}')
print(f'avg loss on loss days: {avg_loss_on_loss_day}')
print(f'loss percentage: {loss_percentage}%')
print(f'max wining streak: {max_wining_streak}')
print(f'max lossing streak: {max_losing_streak}')
print(f'expectancy: {expectancy}')

day_end_log['PnL_Cumulative_Sum'] = day_end_log['PnL'].cumsum()
day_end_log['Drawdown'] = day_end_log['PnL_Cumulative_Sum'] - \
                          day_end_log['PnL_Cumulative_Sum'].cummax()
max_drawdown = round(day_end_log['Drawdown'].min(), 2) * quantity
print(f'Max Drawdown [Rs.] :{max_drawdown}')



