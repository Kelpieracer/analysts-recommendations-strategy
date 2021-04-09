from datetime import datetime
import os
from read_data import read_data
from pandas import pandas as pd

for dir in ['results', 'data']:
    if not os.path.isdir(dir):
        os.mkdir(dir)

BUY = 1
SELL = 0

start_date = '2018-01-01'
end_date = '2021-04-07'

sum_col = '-SUM-'

df_recommendations = pd.read_csv(
    'recommendations.csv').sort_values(by='date_str')
tickers = df_recommendations['ticker'].unique()

buys = [{'SAMPO.HE': [start_date]}]
sells = [{'SAMPO.HE': [end_date]}]
df = pd.DataFrame(columns=tickers)
for ticker in tickers:
    data = read_data(ticker, start_date=start_date,
                     end_date=end_date, only_fresh_data=False)
    data.fillna(method='backfill')
    df[ticker] = data['adjclose']
df_day_gain = df.copy()
df_inderes = df.copy()
df_inderes_map = df.copy()

#  Day Gain table
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

# Buy and Hold table
df_buy_and_hold = df_day_gain.copy()
for row_index, row in df_buy_and_hold.iterrows():
    if row_index == df_buy_and_hold.index[0]:
        for key, value in row.iteritems():
            row[key] = 1/len(tickers)
        previous_row = row
    else:
        for key, value in row.iteritems():
            row[key] = (1 + value) * previous_row[key]
        previous_row = row

# Buy and Hold Rebalanced table
df_buy_and_hold_rebalanced = df_day_gain.copy()
for row_index, row in df_buy_and_hold_rebalanced.iterrows():
    if row_index == df_buy_and_hold_rebalanced.index[0]:
        for key, value in row.iteritems():
            row[key] = 1/len(tickers)
        previous_row = row
    else:
        average = previous_row.mean()
        for key, value in row.iteritems():
            row[key] = (1 + value) * average
        previous_row = row

# Position table by recommendations
df_positions = df_day_gain.copy()
for ticker in tickers:
    df_ticker_recommendations = df_recommendations[df_recommendations['ticker'] == ticker]
    for row_index, row in df_positions.iterrows():
        previous_recommendations = df_ticker_recommendations[
            df_ticker_recommendations['date_str'] <= str(row_index)[:10]]
        if len(previous_recommendations) > 0:
            recommendation_now = BUY if previous_recommendations[
                'recommendation'].tail(1).iloc[0] == 'BUY' else SELL
        else:
            recommendation_now = SELL
        row[ticker] = recommendation_now
        pass

# Gain table by recommendations, rebalanced only when recommendation changes
df_by_recommendations = df_day_gain.copy()
for row_index, row in df_by_recommendations.iterrows():
    positions_row = df_positions[df_positions.index == row_index]
    no_of_invested = positions_row.sum(axis=1)[0]
    if row_index == df_by_recommendations.index[0]:  # First day
        for key, value in row.iteritems():
            row[key] = 1/no_of_invested if positions_row[key][0] == BUY else 0
        previous_row = row
    else:
        if len(df_recommendations[df_recommendations['date_str'] == str(row_index)[:10]]):
            row_profit = previous_row.sum()
            for key, value in row.iteritems():
                row[key] = (1 + value) * row_profit / \
                    no_of_invested if positions_row[key][0] == BUY else 0
        else:
            for key, value in row.iteritems():
                row[key] = (1 + value) * previous_row[key]
        previous_row = row


# Gain table by recommendations daily rebalanced
df_by_recommendations_rebalanced = df_day_gain.copy()
for row_index, row in df_by_recommendations_rebalanced.iterrows():
    positions_row = df_positions[df_positions.index == row_index]
    no_of_invested = positions_row.sum(axis=1)[0]
    if row_index == df_by_recommendations_rebalanced.index[0]:
        for key, value in row.iteritems():
            row[key] = 1/no_of_invested if positions_row[key][0] == BUY else 0
        previous_row = row
    else:
        row_profit = previous_row.sum()
        for key, value in row.iteritems():
            row[key] = (1 + value) * row_profit / \
                no_of_invested if positions_row[key][0] == BUY else 0
        previous_row = row

print(f"Start date: {start_date}")
print(f"End date: {end_date}")
print(f"Buy&Hold gain: {df_buy_and_hold.tail(1).sum(axis=1)[0]:.2f}")
print(
    f"Buy&Hold daily rebalanced gain: {df_buy_and_hold_rebalanced.tail(1).sum(axis=1)[0]:.2f}")
print(
    f"By recommendations rebalanced when recommendations change gain: {df_by_recommendations.tail(1).sum(axis=1)[0]:.2f}")
print(
    f"By recommendations daily rebalanced gain: {df_by_recommendations_rebalanced.tail(1).sum(axis=1)[0]:.2f}")

df_buy_and_hold.loc[:, sum_col] = df_buy_and_hold.sum(
    numeric_only=True, axis=1)
df_buy_and_hold_rebalanced.loc[:, sum_col] = df_buy_and_hold_rebalanced.sum(
    numeric_only=True, axis=1)
df_by_recommendations.loc[:, sum_col] = df_by_recommendations.sum(
    numeric_only=True, axis=1)
df_by_recommendations_rebalanced.loc[:, sum_col] = df_by_recommendations_rebalanced.sum(
    numeric_only=True, axis=1)

with pd.ExcelWriter(
        f'results/results {datetime.now().strftime("%Y-%m-%d %H.%M")}.xlsx') as writer:
    df_buy_and_hold.to_excel(writer, sheet_name='buy-and-hold'[:30])
    df_buy_and_hold_rebalanced.to_excel(
        writer, sheet_name='buy-and-hold-daily-rebalanced'[:30])
    df_by_recommendations.to_excel(
        writer, sheet_name='by-recommendations-balanced-when-changed'[:30])
    df_by_recommendations_rebalanced.to_excel(
        writer, sheet_name='by-recommendations-daily-rebalanced'[:30])

pass
