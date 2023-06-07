import datetime

from base import OB1Base
from strategies.utils import clean_time


class OB1(OB1Base):

    def __init__(self, data, today_date, prev_day_data, instrument='BANKNIFTY'):
        super().__init__(data, today_date, prev_day_data, instrument)

        self.ce_sl_price = 0
        self.pe_sl_price = 0
        self.futures_entry_price = 0
        self.ce_entry_price = 0
        self.pe_entry_price = 0
        self.ce_target_price = 0
        self.pe_target_price = 0
        self.ce_stop_loss_counter = 0
        self.pe_stop_loss_counter = 0
        self.ce_entry_datetime = ''
        self.pe_entry_datetime = ''
        self.ce_exit_datetime = ''
        self.pe_exit_datetime = ''
        self.ce_exit_price = 0
        self.pe_exit_price = 0
        self.ce_pnl = 0
        self.pe_pnl = 0
        self.max_profit = 0
        self.max_loss = 0
        self.pnl = 0

        self.ce_entered = False
        self.pe_entered = False

        self.ce_position = False  # indicates whether we have current ce position running
        self.pe_position = False

        self.set_entry_and_sl()

    def set_entry_and_sl(self):
        nine_thirty = datetime.datetime.combine(self.today.date(),
                                                clean_time('9,30'))
        data_f15 = self.intraday_data[self.intraday_data['datetime'] <= nine_thirty]
        ce_high_f15 = data_f15['ce_high'].max()
        ce_low_f15 = data_f15['ce_low'].min()
        pe_high_f15 = data_f15['pe_high'].max()
        pe_low_f15 = data_f15['pe_low'].min()

        if self.ce_gap_percent > 0:
            self.ce_entry_price = ce_high_f15
            # 100 for banknifty, # 50 for nifty
            self.ce_sl_price = min(ce_low_f15, ce_high_f15 - 100)
            self.ce_target_price = self.ce_entry_price + (self.ce_entry_price -
                                                          self.ce_sl_price)

        if self.pe_gap_percent > 0:
            self.pe_entry_price = pe_high_f15
            self.pe_sl_price = min(pe_low_f15, pe_high_f15 - 100)
            self.pe_target_price = self.pe_entry_price + (self.pe_entry_price -
                                                          self.pe_sl_price)

        print(f"{self.ce_entry_price}, {self.ce_sl_price}, {self.ce_target_price}")
        print(f"{self.pe_entry_price}, {self.pe_sl_price}, {self.pe_target_price}")

    def exit_ce_leg(self, index, row):
        self.ce_pnl = self.ce_exit_price - self.ce_entry_price
        self.ce_exit_datetime = row['datetime']
        self.ce_position = False
        self.intraday_data.loc[index, 'ce_pnl'] = self.ce_pnl

    def exit_pe_leg(self, index, row):
        self.pe_pnl = self.pe_exit_price - self.pe_entry_price
        self.pe_exit_datetime = row['datetime']
        self.pe_position = False
        self.intraday_data.loc[index, 'pe_pnl'] = self.pe_pnl

    def update_pnl(self, index):
        self.intraday_data.loc[index, 'ce_pnl'] = self.ce_pnl
        self.intraday_data.loc[index, 'pe_pnl'] = self.pe_pnl
        self.pnl = self.ce_pnl + self.pe_pnl
        self.max_profit = max(self.max_profit, self.pnl)
        self.max_loss = min(self.max_loss, self.pnl)

    def simulate(self):

        three_ten = datetime.datetime.combine(self.today.date(),
                                              clean_time('15,10'))

        for index, row in self.intraday_data.iterrows():
            ce_ltp = row['ce_close']
            pe_ltp = row['pe_close']

            # Entry conditions
            if ce_ltp >= self.ce_entry_price and not self.ce_entered and \
                    not self.ce_position and self.ce_gap_percent > 0:
                self.ce_entered = True
                self.ce_position = True
                # self.ce_entry_price = ce_ltp
                self.ce_entry_datetime = row["datetime"]

            if pe_ltp >= self.pe_entry_price and not self.pe_entered and \
                    not self.pe_position and self.pe_gap_percent > 0:
                self.pe_entered = True
                self.pe_position = True
                # self.pe_entry_price = pe_ltp
                self.pe_entry_datetime = row["datetime"]

            # SL conditions
            if ce_ltp <= self.ce_sl_price and self.ce_entered and \
                    self.ce_stop_loss_counter == 0 and self.ce_position:
                self.ce_stop_loss_counter = 1
                self.ce_exit_price = self.ce_sl_price
                self.exit_ce_leg(index, row)

            if pe_ltp <= self.pe_sl_price and self.pe_entered and \
                    self.pe_stop_loss_counter == 0 and self.pe_position:
                self.pe_stop_loss_counter = 1
                self.pe_exit_price = self.pe_sl_price
                self.exit_pe_leg(index, row)

            # Target conditions
            if ce_ltp >= self.ce_target_price and self.ce_position:
                self.ce_exit_price = self.ce_target_price
                self.exit_ce_leg(index, row)

            if pe_ltp >= self.pe_target_price and self.pe_position:
                self.pe_exit_price = self.pe_target_price
                self.exit_pe_leg(index, row)

            # If time is 3:10, exit running positions
            if row['datetime'] >= three_ten and self.ce_position:
                self.ce_exit_price = ce_ltp
                self.exit_ce_leg(index, row)

            if row['datetime'] >= three_ten and self.pe_position:
                self.pe_exit_price = pe_ltp
                self.exit_pe_leg(index, row)

            if self.ce_position:
                self.ce_pnl = ce_ltp - self.ce_entry_price
            if self.pe_position:
                self.pe_pnl = pe_ltp - self.pe_entry_price
            self.update_pnl(index)

            if ((self.ce_entered and not self.ce_position) or self.ce_gap_percent <= 0) \
                    and ((self.pe_entered and not self.pe_position) or
                         self.pe_gap_percent <= 0):
                break

        intraday_trade_log = {
                                'Date': self.today,
                                'ATM': self.atm_strike,
                                'Days_to_Expiry': (
                                        self.monthly_expiry -
                                        self.today.date()).days,
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

        resp = {
            'success': True,
            'intraday_trade_log': intraday_trade_log
        }

        if not self.ce_entered and not self.pe_entered:
            resp['success'] = False

        # print(intraday_trade_log)
        # print(self.intraday_data)
        # self.intraday_data.to_csv('data_1.csv')
        return resp
