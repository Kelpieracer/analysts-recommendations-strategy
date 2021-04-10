from pandas import pandas as pd
import numpy as np
from datetime import date
import codecs

recommendations_in_finnish = {'Osta': 'BUY',
                              'Lisää': 'ADD', 'Vähennä': 'REDUCE', 'Myy': 'SELL'}


def parse_date(raw_date):
    if '.' in raw_date:
        raw_date_split = raw_date.split('.')
    elif '/' in raw_date:
        raw_date_split = raw_date.split('/')
    else:
        raise ValueError('Date value is not of form mm/dd/yyyy or mm.dd.yyyy')
    (day, month, year) = map(lambda x: int(x), raw_date_split)
    d = date(year, month, day)
    return d.strftime('%Y-%m-%d')


def parse_recommendation_text(raw_recommendation, recommendations_dict):
    recommendation = recommendations_in_finnish[
        raw_recommendation] if raw_recommendation in recommendations_in_finnish else raw_recommendation
    return recommendations_dict[recommendation]


def parse_recommendations(raw_data, recommendations_dict):
    columns = ['date_str', 'recommendation', 'ticker']
    df = pd.DataFrame(columns=columns)
    ticker = ''
    for data in raw_data['data']:
        if '\t' in data:
            data_splitted = data.split('\t')
            date_str = parse_date(data_splitted[0])
            if(ticker == ''):
                raise SyntaxError(
                    f'Ticker must be defined before recommendation row, line "{data}"".')
            recommendation = parse_recommendation_text(
                data_splitted[1], recommendations_dict)
            row = pd.DataFrame(
                np.array([[date_str, recommendation, ticker]]), columns=columns)
            if len(df) == 0:
                df = df.append(row)
            else:
                last_row = df.tail(1).iloc[0]
                if last_row['ticker'] == ticker and last_row['date_str'] >= date_str:
                    raise ValueError(
                        f'Ticker {ticker} has suspicious order of dates, line "{data}", previous date {last_row["date_str"]}')
                if last_row['ticker'] != ticker or last_row['recommendation'] != recommendation:
                    df = df.append(row)
        else:
            if data == '-END-':
                return df
            if data != '':
                ticker = data
    return df


def get_recommendations(filename, recommendations_dict):
    # open for reading with "universal" type set
    doc = codecs.open(filename=filename, mode='rU',
                      encoding='UTF-8')
    raw_data = pd.read_csv(doc, sep='\r')

    return parse_recommendations(raw_data, recommendations_dict)


if __name__ == "__main__":
    print(parse_date('1.2.2021'))
    print(parse_date('1/5/2019'))
    # print(parse_date('2020-01-01'))

    df = get_recommendations("recomm-inderes-nordea-osakekorit.csv")
    print(df)
