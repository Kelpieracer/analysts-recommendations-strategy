import pandas as pd
from read_data import read_data


def get_day_gain(tickers, start_date, end_date):

    df = pd.DataFrame(columns=tickers)
    for ticker in tickers:
        data = read_data(ticker, start_date=start_date,
                         end_date=end_date, only_fresh_data=False)
        data.fillna(method='backfill')
        df[ticker] = data['adjclose']
    df_day_gain = df.copy()
    for row_index, row in df_day_gain.iterrows():
        if row_index == df_day_gain.index[0]:
            previous_row = row.copy()
            for key, value in row.iteritems():
                row[key] = 0
        else:
            this_row = row.copy()
            for key, value in row.iteritems():
                previous_value = previous_row[key]
                row[key] = (value - previous_value) / previous_value
            previous_row = this_row
    return df_day_gain
