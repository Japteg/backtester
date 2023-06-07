from base import ShortStraddleBase


class ShortStraddle(ShortStraddleBase):

    def __init__(self, data, today_date, instrument='BANKNIFTY', entry_time='9,20',
                 exit_time='15,10', sl=0.2):
        super().__init__(data, today_date, instrument, entry_time, exit_time)

        self.sl_percentage = sl  # 0.2 for 20%
        self.ce_sl_price = 0
        self.pe_sl_price = 0
        self.futures_entry_price = 0
        self.ce_entry_price = 0
        self.pe_entry_price = 0
        self.ce_stop_loss_counter = 0
        self.pe_stop_loss_counter = 0
        self.ce_exit_datetime = ''
        self.pe_exit_datetime = ''
        self.ce_exit_price = 0
        self.pe_exit_price = 0
        self.ce_pnl = 0
        self.pe_pnl = 0
        self.max_profit = 0
        self.max_loss = 0
        self.pnl = 0

        self.set_entry_and_sl()

    def set_entry_and_sl(self):
        traded_prices = self.intraday_data[self.intraday_data['datetime'] ==
                                           self.entry_datetime]

        self.futures_entry_price = traded_prices['futures_close'].iloc[0]
        self.ce_entry_price = traded_prices['ce_close'].iloc[0]
        self.pe_entry_price = traded_prices['pe_close'].iloc[0]

        self.ce_sl_price = self.ce_entry_price + self.ce_entry_price * self.sl_percentage
        self.pe_sl_price = self.pe_entry_price + self.pe_entry_price * self.sl_percentage

        entry_time_index = self.intraday_data[self.intraday_data['datetime'] ==
                                              self.entry_datetime].index[0]

        exit_time_index = self.intraday_data[self.intraday_data['datetime'] ==
                                             self.exit_datetime].index[0]

        self.intraday_data = self.intraday_data[entry_time_index:exit_time_index + 1]

        self.intraday_data['ce_pnl'] = 0
        self.intraday_data['pe_pnl'] = 0

        self.intraday_data.reset_index(drop=True, inplace=True)

    def exit_ce_leg(self, index, row):
        self.ce_pnl = self.ce_entry_price - self.ce_exit_price
        self.ce_exit_datetime = row['datetime']
        self.ce_stop_loss_counter = 1
        self.ce_exit_datetime = row['datetime']
        self.intraday_data.loc[index, 'ce_pnl'] = self.ce_pnl

    def exit_pe_leg(self, index, row):
        self.pe_pnl = self.pe_entry_price - self.pe_exit_price
        self.pe_exit_datetime = row['datetime']
        self.pe_stop_loss_counter = 1
        self.pe_exit_datetime = row['datetime']
        self.intraday_data.loc[index, 'pe_pnl'] = self.pe_pnl

    def update_pnl(self, index):
        self.intraday_data.loc[index, 'ce_pnl'] = self.ce_pnl
        self.intraday_data.loc[index, 'pe_pnl'] = self.pe_pnl
        self.pnl = self.ce_pnl + self.pe_pnl
        self.max_profit = max(self.max_profit, self.pnl)
        self.max_loss = min(self.max_loss, self.pnl)

    def simulate(self):

        for index, row in self.intraday_data.iterrows():
            ce_ltp = row['ce_close']
            pe_ltp = row['pe_close']

            # criteria for exit
            if row["datetime"] >= self.exit_datetime:
                if self.ce_stop_loss_counter == 0:
                    self.ce_exit_price = ce_ltp
                    self.exit_ce_leg(index, row)
                if self.pe_stop_loss_counter == 0:
                    self.pe_exit_price = pe_ltp
                    self.exit_pe_leg(index, row)

                self.update_pnl(index)
                break

            if self.ce_stop_loss_counter == 0 and ce_ltp >= self.ce_sl_price:
                self.ce_exit_price = self.ce_sl_price
                self.exit_ce_leg(index, row)

            if self.pe_stop_loss_counter == 0 and pe_ltp >= self.pe_sl_price:
                self.pe_exit_price = self.pe_sl_price
                self.exit_pe_leg(index, row)

            if self.ce_stop_loss_counter == 1 and self.pe_stop_loss_counter == 1:
                self.update_pnl(index)
                break

            if self.ce_stop_loss_counter == 0:
                self.ce_pnl = self.ce_entry_price - ce_ltp
            if self.pe_stop_loss_counter == 0:
                self.pe_pnl = self.pe_entry_price - pe_ltp
            self.update_pnl(index)

        intraday_trade_log = {
                                'Entry_Datetime': self.entry_datetime,
                                'Future_Traded_Price': self.futures_entry_price,
                                'ATM': self.atm_strike,
                                'Days_to_Expiry': (
                                        self.nearest_expiry -
                                        self.entry_datetime.date()).days,
                                'CE_Symbol': self.ce_symbol,
                                'CE_Entry_Price': self.ce_entry_price,
                                'CE_Exit_Price': self.ce_exit_price,
                                'CE_Exit_Datetime': self.ce_exit_datetime,
                                'PE_Symbol': self.pe_symbol,
                                'PE_Entry_Price': self.pe_entry_price,
                                'PE_Exit_Price': self.pe_exit_price,
                                'PE_Exit_Datetime': self.pe_exit_datetime,
                                'Max_Profit': self.max_profit,
                                'Max_Loss': self.max_loss,
                                'PnL': self.pnl
                            }

        # print(intraday_trade_log.T)
        return intraday_trade_log
