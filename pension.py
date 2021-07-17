import pandas as pd
from read_data import read_data
from datetime import date, datetime
from symbol_dict import symbol_dict

tickers = ["ELISA.HE", "FORTUM.HE", "KEMIRA.HE", "KESKOB.HE", "KNEBV.HE",
           "MOCORP.HE", "NESTE.HE", "NOKIA.HE", "TYRES.HE",
           "ORNBV.HE", "SAMPO.HE", "STERV.HE", "UPM.HE", "WRT1V.HE"]

# tickers = ["^OMXH25", "XDN0.DE", "INDA", "IQQQ.DE", "500E.AS",
#            "EUNL.DE", "XDWD.DE", "DBX9.DE", "R2US.MI"]

# tickers = [x['symbol'] for x in symbol_dict][-20:]

companies = ["Volvo", "ABB", "Securitas", "Telia", "Hennes",
             "Investor", "Alfa", "Skanska", "Sandvik", "TELENOR", "YARA",
             #  "SAS",
             "Stora", "Skandinaviska", "Atlas", "Trelleborg",
             "ORKLA", "Electrolux", "ICA", "NORSK"]
# tickers = [x['symbol'] for x in symbol_dict if x['company'] in companies]

MONTH = 21
QUARTER_YEAR = 60
HALF_YEAR = 120
YEAR = 240
STEP = 5

TICKERS = 2
KNIVES = 0


start_date = '2015-01-01'
end_date = '2021-07-16'


def str_date(str):
    return datetime.strptime(str, "%Y-%m-%d")


def date_str(date):
    return date.strftime("%Y-%m-%d")


def get_datas(tickers):
    datas = {}
    for ticker in tickers:
        data = read_data(ticker, start_date=start_date,
                         end_date=end_date, only_fresh_data=False)

        datas[ticker] = data
    return datas


datas = get_datas(tickers)
dipper = 1
hold_rebal_gain = 1
hold_gain = 0
max_draw_down = 0
highest_gain = 0
max_draw_down_rebal = 0
highest_gain_rebal = 0

for ticker in tickers:
    hold_gain += datas[ticker].iloc[len(datas[tickers[0]])-STEP]['adjclose'] / \
        datas[ticker].iloc[240]['adjclose']
hold_gain /= len(tickers)

df = pd.DataFrame([], columns=['date', 'tickers', 'rebal', 'dipper',
                               'rebal_gain', 'dipper_gain', 'rebal_max_drawdown', 'dipper_max_drawdown'])

for index in range(240, len(datas[tickers[0]]) - STEP - 5, STEP):
    scores = {}
    rebal = 0

    for ticker in tickers:
        price_now = datas[ticker].iloc[index]['adjclose']
        price_1w = datas[ticker].iloc[index-5]['adjclose']
        price_2w = datas[ticker].iloc[index-10]['adjclose']
        price_1m = datas[ticker].iloc[index-MONTH]['adjclose']
        price_2m = datas[ticker].iloc[index-2*MONTH]['adjclose']
        price_3m = datas[ticker].iloc[index-QUARTER_YEAR]['adjclose']
        price_6m = datas[ticker].iloc[index-HALF_YEAR]['adjclose']
        price_12m = datas[ticker].iloc[index-YEAR]['adjclose']
        score = 0
        # 1W * 12 + 1M *12 BEST
        score += price_now/price_1w * 12
        # score += price_now/price_2w * 24
        score += price_now/price_1m * 12
        # score += price_now/price_2m * 6
        # score += price_now/price_3m * 4
        # score += price_now/price_6m * 2
        score -= price_now/price_12m * 0.0
        # score += 1000 if price_now/price_12m > 1.5 else 0
        # score += 1000 if price_3m/price_12m > 1.3 else 0
        if not score:
            break
        rebal += datas[ticker].iloc[index+STEP]['adjclose']/price_now
        scores[ticker] = score
    hold_rebal_gain *= rebal / len(tickers)
    scores = dict(sorted(scores.items(), key=lambda item: item[1]))
    best_tickers = list(scores.items())[KNIVES:TICKERS+KNIVES]
    dipper_gain = 0
    for best_ticker in best_tickers:
        price_prev = datas[best_ticker[0]].iloc[index]['adjclose']
        price_next = datas[best_ticker[0]].iloc[index+STEP]['adjclose']
        dipper_gain += price_next / price_prev
    dipper_gain /= len(best_tickers)
    dipper *= dipper_gain
    highest_gain = max(highest_gain, dipper)
    draw_down = dipper / highest_gain - 1
    max_draw_down = min(draw_down, max_draw_down)

    highest_gain_rebal = max(highest_gain_rebal, hold_rebal_gain)
    draw_down_rebal = hold_rebal_gain / highest_gain_rebal - 1
    max_draw_down_rebal = min(draw_down_rebal, max_draw_down_rebal)
    date = str(datas[best_tickers[0][0]].index[index+STEP])[:10]
    ticker_str = ','.join([x[0] for x in best_tickers])
    df = df.append(pd.DataFrame(
        [[date, ticker_str, hold_rebal_gain, dipper, rebal/len(tickers), dipper_gain, max_draw_down_rebal, max_draw_down]], columns=df.columns))
    print(
        f"{date}:  {ticker_str}  {dipper_gain:.2f}  dipper: {dipper:.2f}   rebal: {hold_rebal_gain:.2f}")
    pass
df.to_csv(f'data/dipper.csv')
print(f"Buy and hold  {hold_gain:.2f}    Dipper max draw_down {max_draw_down:.2f}   Rebal max draw_down {max_draw_down_rebal:.2f}")
pass
