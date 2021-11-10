import pandas as pd
import numpy as np
# from stockstats import StockDataFrame
from read_data import read_data
from datetime import date, datetime
from symbol_dict import symbol_dict

# tickers = "TELIA1.HE SSABBH.HE OUT1V.HE NDA-FI.HE LYMS.DE GC2U.DE 18MF.DE".split(
#     " ")

# tickers = ["ELISA.HE", "FORTUM.HE", "KEMIRA.HE", "KESKOB.HE", "KNEBV.HE",
#            "MOCORP.HE", "NESTE.HE", "NOKIA.HE", "TYRES.HE",
#            "ORNBV.HE", "SAMPO.HE", "STERV.HE", "UPM.HE", "WRT1V.HE"]

tickers = [
    "EFNL",  # Finland
    "GXF",  # Nordic
    "INDA",  # India
    "MCHI",  # China
    "500E.AS",  # SP500
    "EUNL.DE",  # World
    "EZU",  # Eurozone
    "X026.DE",  # Euro small cap
    "FIW",  # Water ETF
    "EEM",  # Emerging markets
    "EEMS",  # Emerging markets small cap
    "WOSC.SW",  # World small cap
    "PEZ",  # Consumer cyclicals momentum
    "PBD",  # Global clean energy ETF
    "USRT",  # REIT ETF
    # "SAMPO.HE"
]

# tickers = [
#     "EFNL", "XDN0.DE"]
# tickers = [x['symbol'] for x in symbol_dict][-20:]

companies = ["Volvo", "ABB", "Securitas", "Telia", "Hennes",
             "Investor", "Alfa", "Skanska", "Sandvik", "TELENOR", "YARA",
             "SAS",
             "Stora", "Skandinaviska", "Atlas", "Trelleborg",
             "ORKLA", "Electrolux", "ICA", "NORSK"]
# tickers = [x['symbol'] for x in symbol_dict if x['company'] in companies]

WEEK = 5
MONTH = 21
QUARTER_YEAR = 63
HALF_YEAR = 129
YEAR = 258
STEP = 5

TICKERS = 2
M1 = 0

start_year = '2013'

end_date = '2021-11-22'


def downside_risk(returns, risk_free=0, samples_per_year=YEAR):
    adj_returns = returns - risk_free
    sqr_downside = np.square(np.clip(adj_returns, np.NINF, 0))
    return np.sqrt(np.nanmean(sqr_downside) * samples_per_year)


def sortino(returns, risk_free=0, samples_per_year=YEAR):
    adj_returns = returns - risk_free
    drisk = downside_risk(adj_returns)
    if drisk == 0:
        return np.nan
    return (np.nanmean(adj_returns) * np.sqrt(samples_per_year)) / drisk


def sharpe(returns, samples_per_year):
    return returns.mean()/returns.std() * np.sqrt(YEAR/STEP)


def yearly_profit(gain, days):
    years = days/YEAR
    profit = (gain + 1)**(1/years) - 1
    return profit


def str_date(str):
    return datetime.strptime(str, "%Y-%m-%d")


def date_str(date):
    return date.strftime("%Y-%m-%d")


def get_datas(tickers, start_date, end_date):
    datas = {}
    for ticker in tickers:
        data = read_data(ticker, start_date=start_date,
                         end_date=end_date, only_fresh_data=False)

        datas[ticker] = data['adjclose']

    indexes = tuple([datas[x].index for x in datas])
    indexes = list(set(np.concatenate(indexes)))
    indexes = sorted(indexes)
    df = pd.DataFrame([], columns=tickers, index=indexes)
    for ticker in tickers:
        for index, row in datas[ticker].items():
            date = index
            df[ticker].loc[date] = row
    return df.fillna(method='bfill')


df_tot = pd.DataFrame([], columns=['step', 'start_date', 'day_add', 'tickers', 'W1', 'M1', 'M3', 'M12', 'M36', 'slip', 'sharpe_rebal', 'sharpe_dipper', 'sharpe_benefit',
                                   'sor_rebal', 'sor_dipper', 'sor_benefit', 'buy_and_hold_gain',
                                   'rebal_gain', 'dipper_gain', 'rebal_max_drawdown', 'dipper_max_drawdown', 'max_loosing_weeks',
                                   'benefit_over_bh', 'benefit_over_rebal', 'yearly_gain_bh', 'yearly_gain_rebal', 'yearly_gain_dipper'
                                   ])

start_dates = {'2011': ['2011-01-03'],
               '2012': ['2011-01-02'],
               '2013': ['2013-01-02', f'2013-01-03',
                        f'2013-01-04', f'2013-01-07', f'2013-01-08'],
               '2014': ['2013-01-02', f'2013-01-03',
                        f'2013-01-07', f'2013-01-08', f'2013-01-09'],
               '2016': ['2013-01-04', f'2013-01-05',
                        f'2013-01-07', f'2013-01-08', f'2013-01-09'],
               }


df_collection = pd.DataFrame([])


def calculate_day_per_ticker(MONTH, QUARTER_YEAR, YEAR, STEP, M1, datas, M36, M12, M3, W1, SLIP, ticker, index, scores, rebal):
    datas_list = list(datas[ticker])
    price_now = datas_list[max(0, index-SLIP)]
    price_1w = datas_list[max(0, index-5)]
    price_1m = datas_list[max(0, index-MONTH)]
    price_3m = datas_list[index - QUARTER_YEAR]
    price_12m = datas_list[max(
        0, index-YEAR)]
    price_36m = datas_list[max(
        0, index-3*YEAR)]

    score = 0
    score += ((price_now /
               price_1w) ** 1) * W1
    score += (price_now /
              price_1m)**1 * M1
    score += price_now/price_3m * M3
    score += price_now/price_12m * M12
    score += price_now/price_36m * M36

    rebal += datas_list[index +
                        STEP] / datas_list[index]
    scores[ticker] = score
    return scores, rebal


def calculate_scores_all_tickers(tickers, MONTH, QUARTER_YEAR, YEAR, STEP, M1, datas, M36, M12, M3, W1, SLIP, index):
    scores = {}
    rebal = 0
    for ticker in tickers:
        scores, rebal = calculate_day_per_ticker(
            MONTH, QUARTER_YEAR, YEAR, STEP, M1, datas, M36, M12, M3, W1, SLIP, ticker, index, scores, rebal)
    return scores, rebal


def calculate_rebal_gains(tickers, hold_rebal_gain, rebal):
    rebal_gain = rebal / \
        len(tickers)
    hold_rebal_gain *= rebal_gain
    return rebal_gain, hold_rebal_gain


def get_best_tickers_from_scores(STEP, TICKERS, datas, index, scores):
    scores = dict(
        sorted(scores.items(), key=lambda item: -item[1]))
    best_tickers = list(scores.items())[
        :TICKERS]
    method_gain = 0
    for best_ticker in best_tickers:
        datas_list = list(
            datas[best_ticker[0]])
        price_prev = datas_list[index]
        price_next = datas_list[index+STEP]
        method_gain += price_next / price_prev
    return best_tickers, method_gain


def eunl_gain(datas, index):
    datas_list = list(datas["EUNL.DE"])
    price_prev = datas_list[index]
    price_next = datas_list[index+STEP]
    gain = price_next / price_prev
    return gain


def calculate_parameters(
        method, hold_rebal_gain, loosing_weeks, rebal_gain, best_tickers, method_gain, max_loosing_weeks, highest_gain, max_draw_down, highest_gain_rebal, max_draw_down_rebal):
    method_gain /= len(best_tickers)
    method *= method_gain
    if method_gain < rebal_gain:
        loosing_weeks += 1
    else:
        loosing_weeks = 0
    max_loosing_weeks = max(
        max_loosing_weeks, loosing_weeks)
    highest_gain = max(
        highest_gain, method)
    draw_down = method / highest_gain - 1
    max_draw_down = min(
        draw_down, max_draw_down)

    highest_gain_rebal = max(
        highest_gain_rebal, hold_rebal_gain)
    draw_down_rebal = hold_rebal_gain / highest_gain_rebal - 1
    max_draw_down_rebal = min(
        draw_down_rebal, max_draw_down_rebal, highest_gain_rebal)

    return max_draw_down, max_draw_down_rebal, max_loosing_weeks, highest_gain, max_draw_down, highest_gain_rebal, max_draw_down_rebal, method, loosing_weeks


def calculate_hold_gain(tickers, STEP, datas, hold_gain, start_index, end_index):
    for ticker in tickers:
        datas_list = list(
            datas[ticker])
        hold_gain += datas_list[end_index - end_index % STEP + STEP] / \
            datas_list[start_index]
    hold_gain /= len(tickers)
    return hold_gain


def calculate_sharpe_sordino(YEAR, STEP, df):
    r_rebal = df['rebal'].diff()
    r_dipper = df['method'].diff()
    r_benefit = df['benefit'].diff()
    sr_rebal = sharpe(r_rebal, YEAR/STEP)
    sr_dipper = sharpe(r_dipper, YEAR/STEP)
    sr_benefit = sharpe(
        r_benefit, YEAR/STEP)
    sor_rebal = sortino(
        r_rebal, 0, YEAR/STEP)
    sor_dipper = sortino(
        r_dipper, 0, YEAR/STEP)
    sor_benefit = sortino(
        r_benefit, 0, YEAR/STEP)

    return sr_rebal, sr_dipper, sr_benefit, sor_rebal, sor_dipper, sor_benefit


last_dipper_gain, previous_dipper_gain = 1.0, 1.0
last_trend_gain, previous_trend_gain = 1.0, 1.0
STEP = MONTH
start_date = start_year
datas = get_datas(tickers, start_date, end_date)


def dipper_multipliers():
    M36, M12, M3, M1, W1 = 0.0, -1.5, 0.7, 0.2, 0.3
    return M36, M12, M3, M1, W1


def trend_multipliers():
    M36, M12, M3, M1, W1 = 0.0, 1.0, 0.0, 0.0, 0.0
    return M36, M12, M3, M1, W1


# CHANGE NAME
fname = 'combo with reit'
writer = pd.ExcelWriter(
    f'results/{fname}.xlsx', engine='xlsxwriter')
# CHANGE NAME

for day_add in range(0, MONTH, 1):
    for TICKERS in [1]:
        for SLIP in [1]:
            gains = []
            print(f'STEP {STEP} start_date {start_date} slip {SLIP}')
            method, loosing_weeks, hold_gain, hold_rebal_gain, max_loosing_weeks = 1, 0, 0, 1, 0
            highest_gain, max_draw_down, highest_gain_rebal, max_draw_down_rebal = 0, 0, 0, 0
            dipper, trend = 1, 1

            df = pd.DataFrame([], columns=['date', 'tickers', 'rebal', 'method',
                                           'rebal_gain', 'method_gain', 'rebal_max_drawdown', 'dipper_max_drawdown', 'benefit'] +
                              tickers + [f'I_{t}' for t in tickers])
            start_index = day_add + 1 * YEAR
            end_index = len(
                datas[tickers[0]]) - STEP - 1

            hold_gain = calculate_hold_gain(
                tickers, STEP, datas, hold_gain, start_index, end_index)

            for index in range(start_index, end_index, STEP):
                # Dipper
                M36, M12, M3, M1, W1 = dipper_multipliers()
                dipper_scores, _ = calculate_scores_all_tickers(
                    tickers, MONTH, QUARTER_YEAR, YEAR, STEP, M1, datas, M36, M12, M3, W1, SLIP, index)
                dipper_best_tickers, dipper_gain = get_best_tickers_from_scores(
                    STEP, TICKERS, datas, index, dipper_scores)
                # Trend
                M36, M12, M3, M1, W1 = trend_multipliers()
                trend_scores, rebal = calculate_scores_all_tickers(
                    tickers, MONTH, QUARTER_YEAR, YEAR, STEP, M1, datas, M36, M12, M3, W1, SLIP, index)
                trend_best_tickers, trend_gain = get_best_tickers_from_scores(
                    STEP, TICKERS, datas, index, trend_scores)

                rebal_gain, hold_rebal_gain = calculate_rebal_gains(
                    tickers, hold_rebal_gain, rebal)

                # Select strategy
                eunl_de_gain = eunl_gain(datas, index)
                if last_dipper_gain > last_trend_gain and last_dipper_gain > eunl_de_gain:
                    # if last_dipper_gain > last_trend_gain:
                    best_tickers, method_gain = dipper_best_tickers, dipper_gain
                    selected_method = "D"
                # elif last_trend_gain > eunl_de_gain or True:
                elif last_trend_gain > eunl_de_gain:
                    best_tickers, method_gain = trend_best_tickers, trend_gain
                    selected_method = "T"
                else:
                    best_tickers, method_gain = [
                        ("EUNL.DE", 1.0)], eunl_de_gain
                    selected_method = "W"
                previous_dipper_gain, previous_trend_gain = last_dipper_gain, last_trend_gain
                last_dipper_gain, last_trend_gain = dipper_gain, trend_gain

                dipper *= dipper_gain
                trend *= trend_gain

                max_draw_down, max_draw_down_rebal, max_loosing_weeks, highest_gain, \
                    max_draw_down, highest_gain_rebal, max_draw_down_rebal, method, loosing_weeks = calculate_parameters(
                        method, hold_rebal_gain, loosing_weeks, rebal_gain, best_tickers, method_gain, max_loosing_weeks, highest_gain,
                        max_draw_down, highest_gain_rebal, max_draw_down_rebal)
                date = str(datas[best_tickers[0][0]].index[index+STEP])[:10]
                gains.append(
                    [date, hold_gain, hold_rebal_gain, method, trend, dipper])

                ticker_str = ','.join(
                    [x[0] for x in best_tickers])
                ticker_str = f'{selected_method}:{ticker_str}'

                best_tickers_tickers = [
                    t[0] for t in best_tickers]

                df = df.append(pd.DataFrame(
                    [[date, ticker_str, hold_rebal_gain, method, rebal/len(tickers), method_gain, max_draw_down_rebal,
                        max_draw_down, method/hold_rebal_gain] +
                        list(datas.iloc[index]) + [(datas[t][index + STEP] / datas[t][index] if t in best_tickers_tickers else "") for t in tickers]], columns=df.columns))
                pass
            sheet_name = f't{TICKERS}d{day_add}s{SLIP}-{",".join([str(W1), str(M1), str(M3), str(M12), str(M36)])}'
            df.to_excel(
                writer, sheet_name=sheet_name)
            sr_rebal, sr_dipper, sr_benefit, sor_rebal, sor_dipper, sor_benefit = calculate_sharpe_sordino(
                YEAR, STEP, df)
            df_row = pd.DataFrame([[STEP, start_date, day_add, TICKERS, W1, M1, M3, M12, M36, SLIP, sr_rebal, sr_dipper, sr_benefit, sor_rebal, sor_dipper, sor_benefit, hold_gain, hold_rebal_gain, method, max_draw_down_rebal, max_draw_down, max_loosing_weeks,
                                    method/hold_gain, method/hold_rebal_gain,  yearly_profit(hold_gain, end_index-start_index), yearly_profit(hold_rebal_gain, end_index-start_index), yearly_profit(method, end_index-start_index)]], columns=df_tot.columns)
            df_tot = df_tot.append(df_row)
            if df_collection.size == 0:
                df_collection['date'] = df['date']
            benefit_list = list(
                df['benefit'])
            benefit_list = benefit_list + \
                (benefit_list[-1:] *
                    (len(df_collection) - len(benefit_list)))
            df_collection[sheet_name] = benefit_list[0:len(
                df_collection)]
            print(df_row)
            pass
df_collection = df_collection.assign(
    mean=df_collection.mean(axis=1))
df_collection.to_excel(f'results/{fname} collection.xlsx')
writer.save()
df_tot.to_excel(f'results/{fname} tot.xlsx')
datas.to_excel(f'results/datas.xlsx')
