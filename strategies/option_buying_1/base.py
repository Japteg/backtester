import pandas as pd
import datetime
import numpy as np

from dateutil.relativedelta import relativedelta, TH
from strategies.constants import STRIKE_OFFSET
from strategies.utils import clean_time


class OB1Base:
    def __init__(self, data, today_date, prev_day_data, instrument='BANKNIFTY'):
        self.data = data  # entire dataset of fno stocks
        self.today = today_date
        self.intraday_data = pd.DataFrame()
        self.prev_day_data = prev_day_data

        self.atm_strike = 0
        self.instrument = instrument
        self.instrument_base = STRIKE_OFFSET[self.instrument]
        self.future_expiry_offset = 'I'
        self.pe_symbol = ''
        self.ce_symbol = ''
        self.monthly_expiry = ''
        self.ce_gap_percent = 0
        self.pe_gap_percent = 0

        self.prepare_data()

    def clean_and_validate_data(self):
        pass

    def get_last_thurs_of_month(self):
        cmon = self.today.month
        last_thurs = None
        for i in range(1, 7):
            t = self.today + relativedelta(weekday=TH(i))
            if t.month != cmon:
                t = t + relativedelta(weekday=TH(-2))
                last_thurs = t
                break
        return last_thurs

    def prepare_data(self):
        """
        for short straddle we just need atm call and put strike and their prices
        for the entire day
        """

        # adding a column of expiry_type with ('' or I or II or III)
        # I-CurrentMonth
        # II-NextMonth
        # III-NextToNextMonth

        self.data['expiry_type'] = np.where((self.data['instrument_type'] == 'FUT'),
                                            self.data['ticker'].apply(
                                                lambda x: x.split('-')[-1].split('.')[0]),
                                            '')

        futures_data = self.data[(self.data['instrument_type'] == 'FUT') &
                                 (self.data['instrument_name'] == self.instrument) &
                                 (self.data['expiry_type'] == self.future_expiry_offset)]
        futures_data.reset_index(drop=True, inplace=True)

        # ---Find ATM strike at 9:30---
        nine_thirty = datetime.datetime.combine(self.today.date(),
                                                clean_time('9,30'))
        # futures_data_f15 = futures_data[(futures_data["datetime"] <= nine_thirty)]
        # print(futures_data_f15.T)
        futures_data_a930 = futures_data[(futures_data["datetime"] == nine_thirty)]
        close_at_930 = futures_data_a930['close'].iloc[0]
        self.atm_strike = self.instrument_base * round(
            close_at_930 / self.instrument_base)
        print(self.atm_strike)

        last_thurs = self.get_last_thurs_of_month()

        # filter for CE data
        ce_data = self.data[(self.data['instrument_type'] == 'CE') &
                            (self.data['instrument_name'] == self.instrument) &
                            ((self.data['expiry_date'] == last_thurs) |
                             (self.data['expiry_date'] ==
                              last_thurs - datetime.timedelta(days=1)) |
                             (self.data['expiry_date'] ==
                              last_thurs - datetime.timedelta(days=2))) &
                            (self.data['strike_price'] == self.atm_strike)]
        ce_data.reset_index(drop=True, inplace=True)

        # filter for PE data
        pe_data = self.data[(self.data['instrument_type'] == 'PE') &
                            (self.data['instrument_name'] == self.instrument) &
                            ((self.data['expiry_date'] == last_thurs) |
                             (self.data['expiry_date'] ==
                              last_thurs - datetime.timedelta(days=1)) |
                             (self.data['expiry_date'] ==
                              last_thurs - datetime.timedelta(days=2))) &
                            (self.data['strike_price'] == self.atm_strike)]
        pe_data.reset_index(drop=True, inplace=True)

        self.ce_symbol = ce_data['ticker'].iloc[0]
        self.monthly_expiry = ce_data['expiry_date'].iloc[0]
        self.pe_symbol = pe_data['ticker'].iloc[0]

        futures_data = futures_data[['datetime', 'open', 'close', 'high', 'low']].\
            set_index('datetime')
        ce_data = ce_data[['datetime', 'open', 'close', 'high', 'low']].\
            set_index('datetime')
        pe_data = pe_data[['datetime', 'open', 'close', 'high', 'low']].\
            set_index('datetime')

        self.intraday_data = pd.concat([futures_data, ce_data, pe_data], axis=1)
        self.intraday_data.columns = ['futures_open', 'futures_close', 'futures_high',
                                      'futures_low', 'ce_open', 'ce_close', 'ce_high',
                                      'ce_low', 'pe_open', 'pe_close','pe_high', 'pe_low']
        # if gaps are large, forward fill is not a good way to go
        self.intraday_data = self.intraday_data.ffill()
        self.intraday_data.reset_index(inplace=True)
        self.check_gap()

    def check_gap(self):

        # For CE
        today_open = self.intraday_data['ce_open'].iloc[0]
        prev_data_ce = self.prev_day_data[self.prev_day_data['ticker'] == self.ce_symbol]
        pdc = prev_data_ce['agg_close'].iloc[0]
        gap_pts = today_open - pdc
        gap_percent = round((gap_pts / pdc) * 100, 2)
        print(f"ce_gap: {gap_percent}%")
        self.ce_gap_percent = gap_percent

        # For PE
        today_open = self.intraday_data['pe_open'].iloc[0]
        prev_data_ce = self.prev_day_data[self.prev_day_data['ticker'] == self.pe_symbol]
        pdc = prev_data_ce['agg_close'].iloc[0]
        gap_pts = today_open - pdc
        gap_percent = round((gap_pts / pdc) * 100, 2)
        print(f"pe_gap: {gap_percent}%")
        self.pe_gap_percent = gap_percent
