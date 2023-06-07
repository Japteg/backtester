import pandas as pd
import datetime

from glob import glob
from logic import ShortStraddle


def write_parameters(**params):
    f = open('results/parameters.txt', 'w')
    for key in params:
        f.write(f"{key} : {params[key]} \n")
    f.close()


class ShortStraddleManager:

    def __init__(self, **parameters):
        self.instrument = parameters.get('instrument', 'BANKNIFTY')
        self.entry_time = parameters.get('entry_time', '9,20')
        self.exit_time = parameters.get('exit_time', '3,10')
        self.sl = float(parameters.get('sl', '0.2'))
        write_parameters(**parameters)

        self.intraday_trade_log = pd.DataFrame(columns=['Entry_Datetime',
                                                        'Future_Traded_Price',
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
        path = pd.DataFrame(glob(base_path), columns=['location'])
        path['data_date'] = path['location'].apply(
            lambda x: x.split('_')[-1].split('.')[0])
        path['data_date'] = path['data_date'].apply(
            lambda x: datetime.datetime.strptime(x, '%Y-%m-%d'))
        path = path.sort_values(['data_date'])
        path.reset_index(drop=True, inplace=True)

        for index, row in path.iterrows():
            print(index)
            data = pd.read_pickle(row['location'])
            short_straddle = ShortStraddle(data, row['data_date'], self.instrument,
                                           self.entry_time, self.exit_time, self.sl)
            result = short_straddle.simulate()
            self.intraday_trade_log = self.intraday_trade_log.append(result,
                                                                     ignore_index=True)

        self.intraday_trade_log.to_csv('results/intraday_trade_log.csv')
        return self.intraday_trade_log


default_params = {
    "instrument": "BANKNIFTY",
    "entry_time": "9,20",
    "exit_time": "15,10",
    "sl": "0.2"
}

manger = ShortStraddleManager(**default_params)
manger.execute()
