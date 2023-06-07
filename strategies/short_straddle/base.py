import pandas as pd
import datetime
import numpy as np

from dateutil.relativedelta import relativedelta, TH
from strategies.constants import STRIKE_OFFSET
from strategies.utils import clean_time


class ShortStraddleBase:
    def __init__(self, data, today_date, instrument='BANKNIFTY', entry_time='9,20',
                 exit_time='15,10'):
        self.data = data  # entire dataset of fno stocks
        self.today = today_date
        self.intraday_data = pd.DataFrame()

        # atm strike changes depending on stock movement.
        # Here we store atm strike at time of taking entry
        self.atm_strike = 0
        self.instrument = instrument
        self.instrument_base = STRIKE_OFFSET[self.instrument]
        self.future_expiry_offset = 'I'
        self.entry_datetime = datetime.datetime.combine(self.today.date(),
                                                        clean_time(entry_time))
        self.exit_datetime = datetime.datetime.combine(self.today.date(),
                                                       clean_time(exit_time))
        self.pe_symbol = ''
        self.ce_symbol = ''
        self.nearest_expiry = ''

        self.prepare_data()

    def clean_and_validate_data(self):
        pass

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

        # atm strike at entry time (9:20)
        self.atm_strike = futures_data[futures_data['datetime'] ==
                                       self.entry_datetime]['open'].iloc[0]
        self.atm_strike = self.instrument_base * round(
            self.atm_strike / self.instrument_base)

        self.nearest_expiry = self.today.date() + relativedelta(weekday=TH(+1))

        # filter for CE data
        ce_data = self.data[(self.data['instrument_type'] == 'CE') &
                            (self.data['instrument_name'] == self.instrument) &
                            ((self.data['expiry_date'] == self.nearest_expiry) |
                             (self.data['expiry_date'] ==
                              self.nearest_expiry - datetime.timedelta(days=1)) |
                             (self.data['expiry_date'] ==
                              self.nearest_expiry - datetime.timedelta(days=2))) &
                            (self.data['strike_price'] == self.atm_strike)]
        ce_data.reset_index(drop=True, inplace=True)

        # filter for PE data
        pe_data = self.data[(self.data['instrument_type'] == 'PE') &
                            (self.data['instrument_name'] == self.instrument) &
                            ((self.data['expiry_date'] == self.nearest_expiry) |
                             (self.data['expiry_date'] ==
                              self.nearest_expiry - datetime.timedelta(days=1)) |
                             (self.data['expiry_date'] ==
                              self.nearest_expiry - datetime.timedelta(days=2))) &
                            (self.data['strike_price'] == self.atm_strike)]
        pe_data.reset_index(drop=True, inplace=True)

        self.ce_symbol = ce_data['ticker'].iloc[0]
        self.pe_symbol = pe_data['ticker'].iloc[0]

        futures_data = futures_data[['datetime', 'close']].set_index('datetime')
        ce_data = ce_data[['datetime', 'close']].set_index('datetime')
        pe_data = pe_data[['datetime', 'close']].set_index('datetime')

        self.intraday_data = pd.concat([futures_data, ce_data, pe_data], axis=1)
        self.intraday_data.columns = ['futures_close', 'ce_close', 'pe_close']
        # if gaps are large, forward fill is not a good way to go
        self.intraday_data = self.intraday_data.ffill()
        self.intraday_data.reset_index(inplace=True)
