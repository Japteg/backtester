import pandas as pd

"""
Future strategy trade log:
sheet1 => date, pnl_point
sheet2 => date, ticker, entry_time, exit_time, entry_price, exit_price, quantity, 
          pnl_point, pnl, pnl_percent, max_profit, max_loss, equity, status
          
status : SL, Target, Neither
pnl_percent: calculated from previous day equity 
max_profit: max mtm seen in that day
max_loss: min mtm seen in that day

Options strategy trade log:
sheet1 => date, quantity, pnl_point, pnl, pnl_percent, equity
sheet2 => date, ce_ticker, pe_ticker, ce_entry_time, pe_entry_time, ce_exit_time, 
          pe_exit_time, ce_entry_price, pe_exit_price, quantity, 
          ce_pnl_point, pe_pnl_point, pnl, pnl_percent, max_profit, max_loss, equity, 
          status
          
status : SL, Target, Neither
pnl_percent: calculated from previous day equity 
max_profit: max mtm seen in that day
max_loss: min mtm seen in that day
"""


class BacktesterBase:

    def __init__(self):
        # self.initial_capital
        # self.equity
        # self.trade_log = pd.DataFrame(columns=columns)
        pass

    def position_sizing(self):
        """
        logic based on current equity, risk appetite, and
        capital allocation to this strategy

        advance: dynamically adjust based on recent performance.
        for example: if in continuous losses, reduce position size or something
        """
        pass

    def make_trade_log_entry(self, *kwargs):
        # self.trade_log.append()
        pass

    def save_trade_log(self):
        # write to file
        pass
