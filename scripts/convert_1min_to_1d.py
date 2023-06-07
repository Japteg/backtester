import pandas as pd
import datetime

from glob import glob
from strategies.utils import clean_time

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

columns = ['date', 'ticker', 'instrument_name', 'open', 'high',
           'low', 'close', 'agg_close']
eod_data = pd.DataFrame(columns=columns)

for index, row in path.iterrows():
    print(index)
    three_pm = datetime.datetime.combine(row['data_date'].date(), clean_time('15,00'))
    three_thirty_pm = datetime.datetime.combine(row['data_date'].date(),
                                                clean_time('15,30'))
    data = pd.read_pickle(row['location'])
    data = data[((data['instrument_name'] == 'NIFTY') |
                (data["instrument_name"] == 'BANKNIFTY'))]
                # & (data["instrument_type"] == "FUT")]
    tickers = data['ticker'].unique()
    # print(data)
    for ticker in tickers:
        ticker_data = data[data['ticker'] == ticker]
        last_30m_data = ticker_data[(ticker_data['datetime'] >= three_pm) &
                                    (ticker_data['datetime'] <= three_thirty_pm)]

        open = ticker_data['open'].iloc[0]
        high = ticker_data['high'].max()
        low = ticker_data['low'].min()
        close = ticker_data['close'].iloc[-1]
        agg_close = round(last_30m_data['close'].mean(skipna=True), 2)
        # print(f"{open}, {high}, {low}, {close}, {agg_close}")

        entry = {
            # 'datetime': ticker_data['datetime'].iloc[0],
            'date': row['data_date'],
            'ticker': ticker,
            'instrument_name': ticker_data['instrument_name'].iloc[0],
            'open': open,
            'high': high,
            'low': low,
            'close': close,
            'agg_close': agg_close
        }
        eod_data = eod_data.append(entry, ignore_index=True)
    # print(eod_data)
    # break

path = "/Users/japtegsingh/Personal/Projects/Backtesting/backtester/" \
       "data/sample_nifty_bn_1day_data/sample_nifty_bn_1d_data_2.csv"
eod_data.to_csv(path)
