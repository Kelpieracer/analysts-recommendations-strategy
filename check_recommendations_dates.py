from datetime import datetime, timedelta


def better_recommendation_date(recommendation_date, df_trade_days):
    one_day = timedelta(days=1)
    last_trade_day = df_trade_days.tail(1).index
    while df_trade_days[df_trade_days.index == recommendation_date].empty:
        recommendation_date = recommendation_date + one_day
        if recommendation_date > last_trade_day:
            break
        # print(f"Adjusted date {recommendation_date.strftime('%Y-%m-%d')}")
    return recommendation_date.strftime('%Y-%m-%d')


def check_recommendations_dates(df_recommendations, df_trade_dates):
    df_days = df_trade_dates.sort_index()
    first_day = df_days.head(1).index[0]

    for index, recommendation in df_recommendations.iterrows():
        rec_date_str = recommendation['date_str']
        rec_datestamp = datetime(year=int(rec_date_str[0:4]),
                                 month=int(rec_date_str[5:7]), day=int(rec_date_str[8:10]))
        if rec_datestamp <= first_day:
            continue
        if df_trade_dates[df_trade_dates.index == rec_datestamp].empty:
            recommendation['date_str'] = better_recommendation_date(
                rec_datestamp, df_trade_dates)

    return df_recommendations
