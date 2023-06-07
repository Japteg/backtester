import pandas as pd
import datetime

from glob import glob

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
    tickers = ['BANKNIFTY-I.NFO', 'NIFTY-I.NFO']
    data = data[(data['ticker'] == tickers[0]) | (data['ticker'] == tickers[1])]
    data.reset_index(drop=True, inplace=True)
    path = "/Users/japtegsingh/Personal/Projects/Backtesting/backtester/" \
           "data/sample_nifty_bn_fut_data/nifty_bn_fut_" + str(row['data_date']) + ".csv"
    data.to_csv(path)
