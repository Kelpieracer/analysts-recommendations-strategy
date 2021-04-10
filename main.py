from datetime import datetime
import os
from read_data import read_data
from pandas import pandas as pd
from get_recommendations import get_recommendations
from get_recommended_positions import get_recommended_positions
from simulation import simulate_buy_and_hold, simulate_buy_and_hold_rebalanced, simulate_by_recommendations, simulate_by_recommendations_rebalanced
from get_analyzed import get_analyzed
from get_day_gain import get_day_gain

for dir in ['results', 'data']:
    if not os.path.isdir(dir):
        os.mkdir(dir)

start_date = '2018-01-01'
end_date = '2021-04-07'
filename = 'recomm-inderes-nordea-osakekorit.csv'
sum_col = '-SUM-'

recommendations_dict = {
    'BUY': 1.0,
    'ADD': 0.7,
    'REDUCE': 0.2,
    'SELL': 0.0
}
df_recommendations = get_recommendations(
    filename, recommendations_dict).sort_values(by='date_str')
tickers = df_recommendations['ticker'].unique()

df = pd.DataFrame(columns=tickers)
for ticker in tickers:
    data = read_data(ticker, start_date=start_date,
                     end_date=end_date, only_fresh_data=False)
    data.fillna(method='backfill')
    df[ticker] = data['adjclose']

df_day_gain = get_day_gain(df)
df_analyzed = get_analyzed(df_day_gain, df_recommendations)
df_buy_and_hold = simulate_buy_and_hold(df_day_gain, df_analyzed)
df_buy_and_hold_rebalanced = simulate_buy_and_hold_rebalanced(
    df_day_gain, df_analyzed)
buy_and_hold_gain = df_buy_and_hold.tail(1).sum(axis=1)[0]
buy_and_hold_rebalanced_gain = df_buy_and_hold_rebalanced.tail(1).sum(axis=1)[
    0]
df_buy_and_hold.loc[:, sum_col] = df_buy_and_hold.sum(
    numeric_only=True, axis=1)
df_buy_and_hold_rebalanced.loc[:, sum_col] = df_buy_and_hold_rebalanced.sum(
    numeric_only=True, axis=1)

df_gains_result = pd.DataFrame(
    columns=['add', 'reduce', 'buy-hold', 'buy-hold-rebal', 'recomm', 'recomm-rebal'])
divider = 50.0
for add in [x / divider for x in range(1, int(divider/5), 1)]:
    for reduce in [x / divider for x in range(0, int(add*divider)+1, 1)]:
        recommendations_dict = {
            'BUY': 1.0,
            'ADD': add,
            'REDUCE': reduce,
            'SELL': 0.0
        }
        df_recommendations = get_recommendations(
            filename, recommendations_dict).sort_values(by='date_str')
        df_positions = get_recommended_positions(
            df_day_gain, df_recommendations)
        df_by_recommendations = simulate_by_recommendations(
            df_day_gain, df_positions, df_recommendations)
        df_by_recommendations_rebalanced = simulate_by_recommendations_rebalanced(
            df_day_gain, df_positions, df_recommendations)

        params = f"add-{add} reduce-{reduce}"
        print(f"Start date: {start_date}")
        print(f"End date: {end_date}")
        print(params)
        by_recommendations_gain = df_by_recommendations.tail(1).sum(axis=1)[0]
        by_recommendations_rebalanced_gain = df_by_recommendations_rebalanced.tail(
            1).sum(axis=1)[0]
        print(f"Buy&Hold gain: {buy_and_hold_gain:.2f}")
        print(
            f"Buy&Hold monthly rebalanced gain: {buy_and_hold_rebalanced_gain:.2f}")
        print(
            f"By recommendations gain: {by_recommendations_gain:.2f}")
        print(
            f"By recommendations monthly rebalanced gain: {by_recommendations_rebalanced_gain:.2f}")

        df_gains_result_row = pd.DataFrame([[add, reduce, buy_and_hold_gain, buy_and_hold_rebalanced_gain,
                                             by_recommendations_gain, by_recommendations_rebalanced_gain]], columns=df_gains_result.columns)
        df_gains_result = df_gains_result.append(df_gains_result_row)

        df_by_recommendations.loc[:, sum_col] = df_by_recommendations.sum(
            numeric_only=True, axis=1)
        df_by_recommendations_rebalanced.loc[:, sum_col] = df_by_recommendations_rebalanced.sum(
            numeric_only=True, axis=1)

        with pd.ExcelWriter(
                f'results/results {params} {datetime.now().strftime("%Y-%m-%d %H.%M")}.xlsx') as writer:
            df_buy_and_hold.to_excel(writer, sheet_name='buy-and-hold'[:30])
            df_buy_and_hold_rebalanced.to_excel(
                writer, sheet_name='buy-and-hold-monthly-rebalanced'[:30])
            df_by_recommendations.to_excel(
                writer, sheet_name='recommendations'[:30])
            df_by_recommendations_rebalanced.to_excel(
                writer, sheet_name='recommendations-monthly-rebalanced'[:30])
            df_positions.to_excel(
                writer, sheet_name='recommended-positions'[:30])
            df_analyzed.to_excel(
                writer, sheet_name='analyzed'[:30])

df_gains_result.to_excel('results/results summary.xlsx')
