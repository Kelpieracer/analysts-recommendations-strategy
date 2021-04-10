# Position table by recommendations
def get_recommended_positions(df_day_gain, df_recommendations):
    df_positions = df_day_gain.copy()
    tickers = df_day_gain.columns

    for ticker in tickers:
        df_ticker_recommendations = df_recommendations[df_recommendations['ticker'] == ticker]
        for row_index, row in df_positions.iterrows():
            previous_recommendations = df_ticker_recommendations[
                df_ticker_recommendations['date_str'] <= str(row_index)[:10]]
            row[ticker] = 0 if len(
                previous_recommendations) == 0 else previous_recommendations['recommendation'].tail(1).iloc[0]
    return df_positions
