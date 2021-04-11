from numpy.core.numeric import count_nonzero

# Buy and Hold table


def simulate_buy_and_hold(df_day_gain, df_analyzed):
    df_buy_and_hold = df_day_gain.copy()
    for row_index, row in df_buy_and_hold.iterrows():
        analyzed_row = df_analyzed.loc[row_index]
        number_of_invested = count_nonzero(analyzed_row)
        money_invested = previous_row.sum(
        ) if row_index != df_buy_and_hold.index[0] else 1
        for key, value in row.iteritems():
            if row_index == df_buy_and_hold.index[0]:
                row[key] = money_invested / \
                    number_of_invested if analyzed_row[key] else 0
            else:
                if previous_row_invested == number_of_invested:
                    row[key] = (1 + value) * \
                        previous_row[key] if analyzed_row[key] else 0
                else:
                    row[key] = (1 + value) * (money_invested /
                                              number_of_invested) if analyzed_row[key] else 0
        previous_row = row
        previous_row_invested = number_of_invested
    return df_buy_and_hold


# Buy and Hold Rebalanced table
def simulate_buy_and_hold_rebalanced(df_day_gain, df_analyzed):
    df_buy_and_hold_rebalanced = df_day_gain.copy()
    for row_index, row in df_buy_and_hold_rebalanced.iterrows():
        analyzed_row = df_analyzed.loc[row_index]
        number_of_invested = count_nonzero(analyzed_row)
        money_invested = previous_row.sum(
        ) if row_index != df_buy_and_hold_rebalanced.index[0] else 1
        if row_index == df_buy_and_hold_rebalanced.index[0]:
            for key, value in row.iteritems():
                row[key] = money_invested / \
                    number_of_invested if analyzed_row[key] else 0
        else:
            for key, value in row.iteritems():
                if previous_month == row_index.month:
                    # rebalance
                    row[key] = (1 + value) * \
                        previous_row[key] if analyzed_row[key] else 0
                else:  # rebalance
                    row[key] = (1 + value) * (money_invested /
                                              number_of_invested) if analyzed_row[key] else 0
        previous_row = row
        previous_month = row_index.month
    return df_buy_and_hold_rebalanced


def simulate_by_recommendations(df_day_gain, df_positions, df_recommendations):
    df_by_recommendations = df_day_gain.copy()
    money_invested = 1
    for row_index, row in df_by_recommendations.iterrows():
        positions_row = df_positions[df_positions.index == row_index]
        no_of_invested = positions_row.sum(axis=1)[0]
        if row_index == df_by_recommendations.index[0]:  # First day
            for key, value in row.iteritems():
                row[key] = (money_invested/no_of_invested) * \
                    positions_row[key][0]
        else:
            if not df_recommendations[df_recommendations['date_str'] == str(row_index)[:10]].empty:
                if no_of_invested == 0:
                    raise ValueError(
                        f'There are no investments today {str(row_index)[:10]}')
                for key, value in row.iteritems():
                    row[key] = (1 + value) * (money_invested /
                                              no_of_invested) * positions_row[key][0]
            else:
                for key, value in row.iteritems():
                    row[key] = (1 + value) * previous_row[key]
        previous_row = row
        money_invested = row.sum()
    return df_by_recommendations


def simulate_by_recommendations_rebalanced(df_day_gain, df_positions, df_recommendations):
    df_by_recommendations_rebalanced = df_day_gain.copy()
    money_invested = 1
    for row_index, row in df_by_recommendations_rebalanced.iterrows():
        positions_row = df_positions[df_positions.index == row_index]
        no_of_invested = positions_row.sum(axis=1)[0]
        if row_index == df_by_recommendations_rebalanced.index[0]:
            for key, value in row.iteritems():
                row[key] = (money_invested/no_of_invested) * \
                    positions_row[key][0]
        else:
            if previous_month == row_index.month or not df_recommendations[df_recommendations['date_str'] == str(row_index)[:10]].empty:
                for key, value in row.iteritems():
                    row[key] = (1 + value) * (money_invested /
                                              no_of_invested) * positions_row[key][0]
            else:
                for key, value in row.iteritems():
                    row[key] = (1 + value) * previous_row[key]
        previous_row = row
        money_invested = row.sum()
        previous_month = row_index.month
    return df_by_recommendations_rebalanced
