
import numpy as np
# Create range which is range of 1,5 squared in.1 steps
import pandas as pd
from matplotlib import pyplot as plt
from scipy import stats

import itertools
from util.acca_optimiser import EVLeg, Lucky



LUCKY_LENGTH = 4
SIMULATION_LENGTH = 10000
ALL_WINNER_MULTI = 1.15
SINGLE_WINNER_MULTI = 2
SINGLE_LOSER_MULTI = 1
MAX_UNIT_PAYOUT = 250000


def calc_var(samples):
    """Returns the variance of the samples"""
    # Each sample contains a value and a probability
    # Get the mean

    return np.var(samples)

def recursive_solve_lucky(leg_results, single_win_multi=1, total_win_multi=1, lucky_length=LUCKY_LENGTH, bonus_on_winnings=True):
    """Returns the payout for a lucky bet
    The legs_results are binary 0 or 1
    They determine if the leg is a winner or not
    The payout is the combination of all winners mutiplied by each other
    """

    if lucky_length == 0:
        return 0
    subs = list(itertools.combinations(leg_results, lucky_length))
    # Get subs where all values are not 0
    subs = [sub for sub in subs if 0 not in sub]
    # Get the total payout
    total_payout = 0
    for sub in subs:
        # Get the payout for the sub
        payout = 1
        for val in sub:
            payout *= val
        total_payout += payout
    if lucky_length == 1:
        total_payout *= single_win_multi
    if lucky_length == 4:
        total_payout *= total_win_multi

    if bonus_on_winnings:
        # Leg results equal profit
        # Add one back on for each sub
        total_payout += len(subs)
    # Add total payout to dict

    return total_payout + recursive_solve_lucky(leg_results, single_win_multi, total_win_multi, lucky_length - 1, bonus_on_winnings)
    #

    # The formula to calculate the returns at this stage of the lucky is ncr(x,4) for winners in x
    ncr_form = lambda winners: (np.math.factorial(4) / (np.math.factorial(4 - winners) * np.math.factorial(winners)))
    # Get all permutations at size of leg results
    # Get all subgroups of leg results

def solve_lucky(leg_results, single_win_multi=1, total_win_multi=1, single_loser_multi=SINGLE_LOSER_MULTI, lucky_length=LUCKY_LENGTH, bonus_on_winnings=True):
    win_list = {}
    payout = 0
    for i in range(1, len(leg_results ) +1):
        combinations = list(itertools.combinations(leg_results, i))
        for combination in combinations:
            if 0 in combination:
                continue
            else:
                if win_list.get(i):
                    win_list[i].append(combination)
                else:
                    win_list[i] = [combination]
                payout += np.prod(combination)

# if no ids in win_list then return 0
    if not win_list:
        return 0
    if len(win_list) == 1:
        # SINGLE WINNER
        # Get the total payout
        if bonus_on_winnings:
            # win_list[0] = win_list[0][0] *  single_win_multi
            win_list[1] = np.prod(win_list[1]) *  single_win_multi
            return win_list
        else:
            win_list[1] = (np.prod(win_list[1]) -1) * single_win_multi + 1
            return win_list
    else:

        for key, win_group in win_list.items():

            total = 0
            for winning_line in win_group:
                line_payout = np.prod(winning_line)
                if len(win_group) == 1 and key == lucky_length:
                    # THIS IS ALL WINNERS
                    if bonus_on_winnings:
                        line_payout = (line_payout - 1) * total_win_multi + 1
                    else:
                        line_payout = line_payout * total_win_multi

                if key == lucky_length-1:
                    if bonus_on_winnings:
                        line_payout = (line_payout - 1) * single_loser_multi + 1
                    else:
                        line_payout = line_payout * single_loser_multi

                total += line_payout
                # if len(winning_line) == 1:
                #     # ALL WINNERS
                #     # Get the product on win_group

            win_list[key] = total
    return win_list


def sum_lucky(leg_dict, winners=4):
    if not leg_dict:
        return 0
    total = 0
    # Get records up to winners
    for i in range(1, winners + 1):
        if leg_dict.get(i):
            total += leg_dict[i]
    return total


def calc_curve(x_vals, y_vals):
    """Returns the curve of the x and y vals"""
    # Get the curve
    curve = np.polyfit(x_vals, y_vals, 3)
    return curve

def plot_lucky_ev_curve(leg_length=LUCKY_LENGTH,
                        single_winner=SINGLE_WINNER_MULTI,
                        single_loser=SINGLE_LOSER_MULTI,
                        all_winner=ALL_WINNER_MULTI,
                        max_unit_payout=MAX_UNIT_PAYOUT):
    values = np.arange(1.25, 25, 0.25)
    values = np.round(values, 2)
    y = []
    for i in values:
        p = stats.binom.pmf(1, leg_length, i/100)
        single_ev = p * single_winner
        p = stats.binom.pmf(leg_length-1, leg_length, i/100)
        single_loser_ev = p * single_loser
        p = stats.binom.pmf(leg_length, leg_length, i/100)
        all_winner_ev = p * all_winner
        ev = single_ev + single_loser_ev + all_winner_ev
        # cap is 250,000
        cap_ev =  i ** leg_length / max_unit_payout -1
        if cap_ev < 1:
            ev += cap_ev
        y = np.append(y, ev)
    # plot curve of values and y
    plt.plot(values, y)
    # Add the parameters to title
    plt.title(f"EV Curve for Lucky 15 with {leg_length} legs, single winner multi: {single_winner}, single loser multi: {single_loser}, all winners multi: {all_winner}")

    # Label the graph
    plt.xlabel('Odds')
    plt.ylabel('EV')
    plt.show()

    # Plot a log of val and y
    #plt.plot(values, np.log(y))
    return values, y

# TO DO - PLOT THE CUMULATIVE FREQUENCY CURVES AS ODDS CHANGES

def plot_cumulative_frequency_curve(leg_length=LUCKY_LENGTH,
                                    single_winner=SINGLE_WINNER_MULTI,
                                    single_loser=SINGLE_LOSER_MULTI,
                                    all_winner=ALL_WINNER_MULTI,
                                    max_unit_payout=MAX_UNIT_PAYOUT):
    values = np.arange(1.25, 25, 0.25)
    values = np.round(values, 2)
    y = []
    # Plot the P of 1 winner as odds changes
    for i in values:
        p = stats.binom.pmf(1, leg_length, i/100)
        y = np.append(y, p)

    # plot curve of values and y
    plt.plot(values, y)




def main():
    # Get a range of betting odds
    low_range = np.arange(1.1, 3, 0.05)
    med_range = np.arange(3, 8, 0.1)
    high_range = np.arange(8, 20, 0.5)
    odds_range = np.concatenate((low_range, med_range, high_range))

    # round to 2 decimal places
    odds_range = np.round(odds_range, 2)

    ev_dict = {}
    prob_dict = {}
    for i in odds_range:
        # single is prob 1/4 come in from range
        # Do binomial distribution for 1 succes from 4 trials
        # where prob of succes is 1/i
        p = stats.binom.pmf(1, LUCKY_LENGTH, 1 / i)
        single_ev = p * (i - 1)
        # collective is i^4 - 1
        collective_ev = 0.15 - (1 / (i ** LUCKY_LENGTH))
        # Add
        ev_dict[i] = (single_ev + collective_ev) / 100
        # Get the prob of each val of successes
        probs = stats.binom.pmf([0, 1, 2, 3, 4], 4, 1 / i)
        prob_dict[i] = probs

    # PLot ev dict
    import matplotlib.pyplot as plt

    plt.plot(ev_dict.keys(), ev_dict.values())
    # LAbel
    plt.xlabel('Odds')
    plt.ylabel('EV')
    plt.title('EV of Lucky')
    # Get the regression line
    # it is a curved line
    for i in range(1, 5):
        # Get the curve
        a = np.polyfit(list(ev_dict.keys()), list(ev_dict.values()), 5)
        # plot the curve
    plt.plot(ev_dict.keys(), np.polyval(a, list(ev_dict.keys())))
    # Lable with i
    plt.text(1, 0.1, f'Curve of degree {i}')

    plt.show()

    med_dict = {}
    # get the median from prob dict
    for key, value in prob_dict.items():
        prob = 0
        i = 0
        iq_l = 0
        iq_r = 0
        med = 0
        if key == 6.2:
            print('here')
        while (i != LUCKY_LENGTH):
            i += 1
            prob += value[i]
            if prob > 0.25 and not iq_l:
                iq_l = i-1
            if prob > 0.5 and not med:
                med = i-1
            if prob > 0.75 and not iq_r:
                iq_r = i-1


        med_dict[key] = [iq_l, med, iq_r]

    # Plot the median dict
    plt.plot(med_dict.keys(), med_dict.values())
    # LAbel
    plt.xlabel('Odds')
    plt.ylabel('Median')
    plt.title('Median of Lucky')
    plt.show()

    median_dict = {}
    for key, val in med_dict.items():
        # Get the median payout
        median_payout = sum_lucky(
            solve_lucky([key for x in range(LUCKY_LENGTH)], single_win_multi=2, total_win_multi=1.15), val[1])
        lower_quartile = sum_lucky(            solve_lucky([key for x in range(LUCKY_LENGTH)], single_win_multi=2, total_win_multi=1.15), val[0])
        upper_quartile = sum_lucky(            solve_lucky([key for x in range(LUCKY_LENGTH)], single_win_multi=2, total_win_multi=1.15), val[2])
        median_dict[key] = [lower_quartile, median_payout, upper_quartile]

    # Plot the median, lower and upper quartile
    # PLot dcit vlaue[0
    plt.plot(median_dict.keys(), [x[0] for x in median_dict.values()])
    # Plot dcit vlaue[1
    plt.plot(median_dict.keys(), [x[1] for x in median_dict.values()])
    # Plot dcit vlaue[2
    plt.plot(median_dict.keys(), [x[2] for x in median_dict.values()])

    plt.legend(['Lower Quartile', 'Median', 'Upper Quartile'])
    # LAbel
    plt.xlabel('Odds')
    plt.ylabel('Median Payout')
    plt.title('Median Payout of Lucky')
    plt.show()

    # plot the median dict
    #plt.plot(median_dict.keys(), median_dict.values())
    # LAbel




    # Simulate 1000 times for each prob set in porb dict
    # Get the average of the 1000 runs
    # Plot the average of the 1000 runs

    total_dict = {}
    i = 0

    for key, val in prob_dict.items():
        # Get random number between 0 and 1 with 6 digits
        sim = np.random.random_sample((SIMULATION_LENGTH, 4))
        # Get the number of successes
        sim = sim < 1 / key
        for simul in sim:

            legs = [key if x else 0 for x in simul]
            lucky_sum = sum_lucky(solve_lucky(legs, single_win_multi=2, total_win_multi=1.15))
            # Add lucky sum to var_dict
            if total_dict.get(key):
                total_dict[key].append(lucky_sum)
            else:
                total_dict[key] = [lucky_sum]

    # Get the variance and mean of each key
    var_dict = {}
    for key, val in total_dict.items():
        var_dict[key] = np.var(val)
    # Plot the variance
    plt.plot(var_dict.keys(), var_dict.values())
    # Label
    plt.xlabel('Odds')
    plt.ylabel('Variance')
    plt.show()


    {key: (solve_lucky([key for x in range(LUCKY_LENGTH)], single_win_multi=2, total_win_multi=1.15)[
        val + 1]) if val < 4 else 0 for key, val in med_dict.items()}




    # Group the results by the following categories for each key
    # 0-15
    # 15-40
    # 40-100
    # 100-200
    # 200-500
    # 500-1000
    # 1000-2000
    # 2000-5000
    # 5000+
    groups = {
        0: [],
        1: [],
        2: [],
        3: [],
        4: [],
        5: [],
        6: [],
        7: [],
        8: []
    }
    for key, val in total_dict.items():
        for result in val:
            # Store key
            if result < 15:
                groups[0].append(key)
            elif result < 40:
                groups[1].append(key)
            elif result < 100:
                groups[2].append(key)
            elif result < 200:
                groups[3].append(key)
            elif result < 500:
                groups[4].append(key)
            elif result < 1000:
                groups[5].append(key)
            elif result < 2000:
                groups[6].append(key)
            elif result < 5000:
                groups[7].append(key)
            else:
                groups[8].append(key)

    # Plot the results

    # Get the mean values in total_dict
    mean_dict = {}
    for key, val in total_dict.items():
        mean_dict[key] = np.mean(val) / 15

    # print 10 keys with greatest mean
    print(sorted(mean_dict.items(), key=lambda x: x[1], reverse=True)[:10])

    # Get the count of each value in each group
    for key, val in groups.items():
        # Get the num of each value
        unique, counts = np.unique(val, return_counts=True)
        # plot x as unique and y as counts
        #
        plt.plot(unique, counts)
        plt.xlabel('Odds')
        plt.ylabel('Count')
        # Title
        plt.title('Group {}'.format(key))
        plt.show()

        # Store
    # Plot a line of proportion of each group against key

    # Get the proportion of each group

    plt.show()

    # Plot the average of the 1000 runs
    plt.plot(total_dict.keys(), total_dict.values())
    plt.show()

    return total_dict, ev_dict, prob_dict


# Create sample legs lists for testing
# Use pytest
SAMPLE_LEGS = [
    [2, 2, 2, 2],
    [2, 2, 2, 3],
    [2, 2, 2, 4],
    [2, 2, 3, 3],
    [2, 0, 3, 4],
    [0, 5, 0, 5],
    [0, 0, 0, 0],
    [0, 0, 0, 5],
    [0, 0, 5, 5],
]


# Create solve_lucky test
def test_solve_lucky():
    for leg in SAMPLE_LEGS:
        # get count of 0s
        zero_count = leg.count(0)
        if zero_count == 4:

            assert sum_lucky(solve_lucky(leg)) == 0
        elif zero_count == 3:
            # assert solve_lucky(leg, single_win_multi=2) > solve_lucky(leg)
            assert sum_lucky(solve_lucky(leg, single_win_multi=2)) > sum_lucky(solve_lucky(leg))

        elif zero_count == 0:
            assert sum_lucky(solve_lucky(leg, total_win_multi=2)) > sum_lucky(solve_lucky(leg))
        else:
            assert sum_lucky(solve_lucky(leg, total_win_multi=2, single_win_multi=2)) == sum_lucky(solve_lucky(leg))


def test_main():
    total_dict, ev_dict, prob_dict = main()
    assert total_dict == ev_dict


if __name__ == '__main__':
    main()

    # for key, value in prob_dict.items():
    #     # ncr_formula = lambda x: (np.math.factorial(LUCKY_LENGTH) / (np.math.factorial(x) * np.math.factorial(LUCKY_LENGTH - x)))
    #     # form = lambda x: (ncr_formula(x) * (key ** x) * ((1 / key) ** (LUCKY_LENGTH - x)))
    #     # #apply form to x=5
    #     # one_four = range(1,5)
    #     # unit_win = sum([form(x) for x in one_four])
    #     # one_formula = lambda x: (key-1*2)+1 if x == 1 else 0
    #     # two_formula = lambda x: ncr_formula(2) * (key-1)**2 if x == 2 else 0
    #     # total = 0
    #     for j in range(1000):
    #         sample = np.random.choice([0, 1, 2, 3, 4], size=sample_lenth, p=value)
    #         counts = np.bincount(sample)
    #         one_count = counts[1]
    #
    #
    #     total_dict[key] = total/1000
