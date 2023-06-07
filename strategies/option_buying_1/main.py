import pandas as pd
import datetime

from glob import glob
from strategies.constants import MAX_SL_PTS
from logic import OB1

"""
Description:

Gap up opening
Entry above first 15 min candle
Sl : min(Below first 15 min candle, max risk per lot)
"""


class OB1Manager:
    def __init__(self, **parameters):
        self.instrument = parameters.get('instrument', 'BANKNIFTY')
        self.max_sl_pts = MAX_SL_PTS[self.instrument]
        # self.entry_time = parameters.get('entry_time', '9,20')
        # self.exit_time = parameters.get('exit_time', '3,10')
        # self.sl = float(parameters.get('sl', '0.2'))

        self.intraday_trade_log = pd.DataFrame(columns=['Date',
                                                        'ATM',
                                                        'Days_to_Expiry',
                                                        'CE_Symbol',
                                                        'CE_Entry_Price',
                                                        'CE_Exit_Price',
                                                        'CE_Exit_Datetime',
                                                        'PE_Symbol',
                                                        'PE_Entry_Price',
                                                        'PE_Exit_Price',
                                                        'PE_Exit_Datetime',
                                                        'Max_Profit',
                                                        'Max_Loss',
                                                        'PnL'])

    def execute(self):
        # fetch all the files from the diretory
        base_path = '/Users/japtegsingh/Personal/Projects/Backtesting/backtester/data/' \
                    'sample_nfo_2019-20_data/*'
        eod_data_path = "/Users/japtegsingh/Personal/Projects/Backtesting/backtester/" \
                        "data/sample_nifty_bn_1day_data/sample_nifty_bn_1d_data_2.csv"
        eod_data = pd.read_csv(eod_data_path)
        eod_data['date'] = eod_data['date'].apply(
            lambda x: datetime.datetime.strptime(x, '%Y-%m-%d %H:%M:%S'))
        path = pd.DataFrame(glob(base_path), columns=['location'])
        path['data_date'] = path['location'].apply(
            lambda x: x.split('_')[-1].split('.')[0])
        path['data_date'] = path['data_date'].apply(
            lambda x: datetime.datetime.strptime(x, '%Y-%m-%d'))
        path = path.sort_values(['data_date'])
        path.reset_index(drop=True, inplace=True)
        prev_day_data = eod_data['date'].iloc[0]
        for index, row in path.iterrows():
            if index == 0:
                prev_day_data = eod_data[(eod_data['date'] == row['data_date'])]
                continue
            print(index)
            data = pd.read_pickle(row['location'])
            ob_1 = OB1(data, row['data_date'], prev_day_data, self.instrument)
            result = ob_1.simulate()
            if result['success']:
                self.intraday_trade_log = self.intraday_trade_log.append(
                    result['intraday_trade_log'], ignore_index=True)
            prev_day_data = eod_data[(eod_data['date'] == row['data_date'])]
            # break
            # print(prev_day_data['date'].iloc[0].date())
        # self.intraday_trade_log.to_csv('results/intraday_trade_log.csv')
        return self.intraday_trade_log


manager = OB1Manager()
manager.execute()
