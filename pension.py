import pandas as pd
import numpy as np
from read_data import read_data
from datetime import date, datetime
from symbol_dict import symbol_dict

tickers = ["ELISA.HE", "FORTUM.HE", "KEMIRA.HE", "KESKOB.HE", "KNEBV.HE",
           "MOCORP.HE", "NESTE.HE", "NOKIA.HE", "TYRES.HE",
           "ORNBV.HE", "SAMPO.HE", "STERV.HE", "UPM.HE", "WRT1V.HE"]

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
    "SPYM.DE",  # Emerging markets
    "WOSC.SW",  # World small cap
    "PEZ",  # Consumer cyclicals momentum
    "PBD",  # Global clean energy ETF
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

MONTH = 21
QUARTER_YEAR = 63
HALF_YEAR = 129
YEAR = 258
STEP = 5

TICKERS = 2
M1 = 0

start_year = '2016'

end_date = '2021-07-16'


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


df_tot = pd.DataFrame([], columns=['step', 'start_date', 'day_add', 'tickers', 'M1', 'M3', 'M36', 'M12', 'slip', 'buy_and_hold_gain',
                                   'rebal_gain', 'dipper_gain', 'rebal_max_drawdown', 'dipper_max_drawdown', 'max_loosing_weeks',
                                   'benefit_over_bh', 'yearly_gain_bh', 'yearly_gain_rebal', 'yearly_gain_dipper'
                                   ])

writer = pd.ExcelWriter('results/dipper_sheets.xlsx', engine='xlsxwriter')

start_dates = {'2013': ['2013-01-02', f'2013-01-03',
                        f'2013-01-04', f'2013-01-07', f'2013-01-08'],
               '2014': ['2013-01-02', f'2013-01-03',
                        f'2013-01-07', f'2013-01-08', f'2013-01-09'],
               '2016': ['2013-01-04', f'2013-01-05',
                        f'2013-01-07', f'2013-01-08', f'2013-01-09'],
               }
for start_date in start_dates[start_year][:1]:
    datas = get_datas(tickers, start_date, end_date)
    for STEP in [5]:
        for day_add in range(0, STEP):
            for TICKERS in [2]:
                for M36 in [-0.2]:
                    for M12 in [-1.5]:
                        for M3 in [0.7]:
                            for M1 in [-0.2]:
                                for SLIP in [1, 2]:
                                    print(
                                        f'STEP {STEP} start_date {start_date} slip {SLIP} MULT {[M12,M3,M36]}')

                                    dipper = 1
                                    hold_rebal_gain = 1
                                    hold_gain = 0
                                    max_draw_down = 0
                                    highest_gain = 0
                                    max_draw_down_rebal = 0
                                    highest_gain_rebal = 0
                                    max_loosing_weeks = 0
                                    loosing_weeks = 0

                                    for ticker in tickers:
                                        datas_list = list(datas[ticker])
                                        hold_gain += datas_list[len(datas[tickers[0]]) -
                                                                STEP] / datas_list[240]
                                    hold_gain /= len(tickers)

                                    df = pd.DataFrame([], columns=['date', 'tickers', 'rebal', 'dipper',
                                                                   'rebal_gain', 'dipper_gain', 'rebal_max_drawdown', 'dipper_max_drawdown', 'benefit'])
                                    start_index = STEP + day_add
                                    end_index = len(
                                        datas[tickers[0]]) - STEP - 1
                                    for index in range(start_index, end_index, STEP):
                                        scores = {}
                                        rebal = 0

                                        for ticker in tickers:
                                            datas_list = list(datas[ticker])
                                            price_now = datas_list[index-SLIP]
                                            # NOTE NOTE!!
                                            # price_1STEP = datas_list[index-STEP]
                                            price_1w = datas_list[index-5]
                                            price_1m = datas_list[index-MONTH]
                                            # price_1m_pre = datas_list[index -
                                            #                           MONTH-5]
                                            # price_1m_aft = datas_list[index -
                                            #                           MONTH+5]
                                            price_2m = datas_list[index -
                                                                  2*MONTH]
                                            price_3m = datas_list[index -
                                                                  QUARTER_YEAR]
                                            price_6m = datas_list[index -
                                                                  HALF_YEAR]
                                            price_12m = datas_list[index-YEAR]
                                            price_36m = datas_list[index-3*YEAR]
                                            score = 0
                                            # 1W * 12 + 1M *12 BEST
                                            # score += price_now/price_1STEP * MULTI_A
                                            # score += price_now/price_2w * 24
                                            # score += price_now/price_12m * MULTI_B
                                            # score += price_now/price_1m_pre * 0
                                            # score += price_now/price_1m_aft * 0
                                            # score += price_now/price_2m * 6

                                            score += price_now/price_1w * 0
                                            score += price_now/price_1m * M1
                                            score += price_now/price_2m * 0
                                            score += price_now/price_3m * M3
                                            # score += price_now/price_6m * M6
                                            score += price_now/price_12m * M12
                                            score += price_now/price_36m * M36

                                            # score += 10 * \
                                            #     sum([1 for p in [
                                            #         price_1m, price_3m] if price_now/p > 1])

                                            # score += 1000 if price_now/price_12m > 1.5 else 0
                                            # score += 1000 if price_3m/price_12m > 1.3 else 0
                                            rebal += datas_list[index +
                                                                STEP] / datas_list[index]
                                            scores[ticker] = score
                                        rebal_gain = rebal / len(tickers)
                                        hold_rebal_gain *= rebal_gain
                                        scores = dict(
                                            sorted(scores.items(), key=lambda item: -item[1]))
                                        best_tickers = list(scores.items())[
                                            :TICKERS]
                                        dipper_gain = 0
                                        for best_ticker in best_tickers:
                                            datas_list = list(
                                                datas[best_ticker[0]])
                                            price_prev = datas_list[index]
                                            price_next = datas_list[index+STEP]
                                            dipper_gain += price_next / price_prev
                                        dipper_gain /= len(best_tickers)
                                        dipper *= dipper_gain
                                        if dipper_gain < rebal_gain:
                                            loosing_weeks += 1
                                        else:
                                            loosing_weeks = 0
                                        max_loosing_weeks = max(
                                            max_loosing_weeks, loosing_weeks)
                                        highest_gain = max(
                                            highest_gain, dipper)
                                        draw_down = dipper / highest_gain - 1
                                        max_draw_down = min(
                                            draw_down, max_draw_down)

                                        highest_gain_rebal = max(
                                            highest_gain_rebal, hold_rebal_gain)
                                        draw_down_rebal = hold_rebal_gain / highest_gain_rebal - 1
                                        max_draw_down_rebal = min(
                                            draw_down_rebal, max_draw_down_rebal)
                                        date = str(datas[best_tickers[0][0]
                                                         ].index[index+STEP])[:10]
                                        ticker_str = ','.join(
                                            [x[0] for x in best_tickers])
                                        df = df.append(pd.DataFrame(
                                            [[date, ticker_str, hold_rebal_gain, dipper, rebal/len(tickers), dipper_gain, max_draw_down_rebal,
                                                max_draw_down, dipper/hold_rebal_gain - 1]], columns=df.columns))
                                        # print(
                                        #     f"{date}:  {ticker_str}  {dipper_gain:.2f}  dipper: {dipper:.2f}   rebal: {hold_rebal_gain:.2f}")
                                        pass
                                    sheet_name = f't{TICKERS}d{day_add}s{SLIP}-{",".join([str(M1), str(M3), str(M12), str(M36)])}'
                                    df.to_excel(writer, sheet_name=sheet_name)
                                    # print(
                                    #     f"Buy and hold  {hold_gain:.2f}    Dipper max draw_down {max_draw_down:.2f}   Rebal max draw_down {max_draw_down_rebal:.2f}")
                                    df_row = pd.DataFrame(
                                        [[STEP, start_date, day_add, TICKERS, M1, M3, M36, M12, SLIP, hold_gain, hold_rebal_gain, dipper, max_draw_down_rebal, max_draw_down, max_loosing_weeks,
                                          dipper/hold_gain, yearly_profit(hold_gain, end_index-start_index), yearly_profit(hold_rebal_gain, end_index-start_index), yearly_profit(dipper, end_index-start_index)]], columns=df_tot.columns)
                                    df_tot = df_tot.append(df_row)
                                    print(df_row)
                                    pass
writer.save()
df_tot.to_excel('results/dipper_tot.xlsx')
datas.to_excel('results/datas.xlsx')
