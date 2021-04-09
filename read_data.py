import pandas as pd
from datetime import datetime
from yahoo_fin import stock_info as si


def read_data(ticker, start_date='2000-01-01', end_date='2100-01-01', only_fresh_data=True):
    # load it from yahoo_fin library
    read_end_date = datetime.now().strftime("%Y-%m-%d")
    data_file_name = f'data/{ticker}_{read_end_date}.csv'

    try:
        if not only_fresh_data:
            df = pd.read_csv(data_file_name, index_col=0)
            df.index = df.index.map(lambda x: datetime.strptime(x, "%Y-%m-%d"))
        if len(df) <= 0:
            raise Exception("No such file")
    except:
        for i in range(0, 10):  # Retry in case of network error
            try:
                df = si.get_data(ticker)
                if len(df) <= 0:
                    raise Exception("No data")
                break
            except:
                if i >= 9:
                    return
        df.to_csv(data_file_name)

    df = df[df.index <= end_date]
    df = df[df.index >= start_date]
    return df


if __name__ == '__main__':
    print(read_data('NOKIA.HE', start_date='2012-01-01',
                    end_date='2012-02-01', only_fresh_data=False))
    print(read_data('NOKIA.HE', start_date='2012-01-01',
                    end_date='2012-02-01'))
