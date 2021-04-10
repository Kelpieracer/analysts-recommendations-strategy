def get_analyzed(df_day_gain, df_recommendations):
    df_analyzed = df_day_gain.copy()
    tickers = df_analyzed.columns
    for ticker in tickers:
        df_ticker_recommendations = df_recommendations[df_recommendations['ticker'] == ticker]
        for row_index, row in df_analyzed.iterrows():
            previous_recommendations = df_ticker_recommendations[
                df_ticker_recommendations['date_str'] <= str(row_index)[:10]]
            df_analyzed.at[row_index, ticker] = int(
                not previous_recommendations.empty)
    return df_analyzed
