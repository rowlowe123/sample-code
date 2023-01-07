import itertools
import random
from typing import List

import numpy as np
import pandas as pd


# Given 4 legs of a bet, create a list of all the combinations and the total return of each combination in a lucky 15 bet
# Returns are equal to the odds multiplied by each other



# To Store outcomes, create a dataframe binary columns for each leg, a column for the probability of that outcome
# and the return multi for that outcome



class EVLeg:
    def __init__(self, ev, given_odds):
        self.ev = ev
        self.given_odds = given_odds
        self.underlying_odds = given_odds / self.ev
        self.prob = 1 / self.underlying_odds

    def __repr__(self):
        return f'EVLeg(ev={self.ev}, given_odds={self.given_odds}, underlying_odds={self.underlying_odds}, prob={self.prob})'


class Lucky:
    def __init__(self, legs: List[EVLeg], single_win_multi=1, total_win_multi=1):
        self.legs = legs
        self.single_win_multi = single_win_multi
        self.total_win_multi = total_win_multi

    def get_bets(self):
        # Create a dataframe of the combinations and total returns
        self.combinations = []

        for i in range(1, len(self.legs) + 1):
            # Add the combinations of the legs to the list
            self.combinations.extend(list(itertools.combinations(self.legs, i)))
        return self.combinations

    def calc_bets(self):
        # Create a dataframe of all the combinations of the legs, with columns for ev, odds, and total return
        df_combos = pd.DataFrame(columns=['ev', 'prob', 'total_return'])
        for combo in self.combinations:
            multi = 1
            ev = 1
            prob = 1

            for leg in combo:
                # Create a list of all the combinations of the legs
                ev *= leg.ev
                prob *= leg.prob
                multi *= leg.given_odds
            df_combos.loc[len(df_combos)] = [ev, prob, multi]



        # Return the dataframe
        return df_combos

    def stagger_bets(self):
        # Find the probability of each combo being the only one to win
        # Starting with the longest combo, work backwards

        df_combos = self.calc_bets()
        # Reverse the dataframe so that the longest combo is first
        df_combos = df_combos.sort_values(by=['prob'], ascending=False)

        for i in df_combos:
            combos = df_combos.loc[df_combos['legs'].isin(i.legs)]
            [combo['prob'] == combo['prob'] - i['prob'] for combo in combos if (i['legs'][0] == combo['legs'][0] and len(combo.legs) != 1)]
        return df_combos


        # Get all records where prob is either 0.1, 0.2 or 0.3


                # vals.prob - combo.prob for each val in vals




            # Find all combos left that have any of the legs in the combo
            # And subtract the prob of the combo from the prob of the other combos





        return




    def get_total_stats(self):
        df_combos = self.calc_bets()
        expected_value = df_combos['ev'].sum()
        edge = expected_value / len(df_combos)
        # Store the values of total return - expected value in a numpy array
        total_returns = df_combos['total_return'].values
        total_returns = total_returns - expected_value
        # Get the variance of total returns
        variance = np.var(total_returns)
        return expected_value, variance, edge


def optimise_lucky(legs, single_win_multi=1, total_win_multi=1):
    pass
    # lucky_list = [range(len(legs)/4)]
    # # Create the model
    # model = LpProblem('Lucky Solver', LpMaximize)
    #
    # # The function to be maximised is the luckified return of the combinations
    #
    #
    #
    #
    #
    # model += sum([lucky_15[] * legs[i] for i in range(len(legs))])
    #
    #
    # x = LpVariable.dicts('x', lucky_list, lowBound=0, upBound=1, cat='Integer')

    # Create a model that uses machine learning to formulate the best combinations of legs to bet on
    # This means that it will try to combine legs that are likely to create high ev returns
    # The model will be constrained by a maximum and minumum total odds or variance for the bet
    # The model will be constrained by a maximum and minumum total odds or variance for the bet


ITEMS_NAME = [
    "Mixed Fruit", "French Fries", "Side Salad",
    "Hot Wings", "Mozzarella Sticks", "Sampler Plate"
]
ITEMS_PRICE = [2.15, 2.75, 3.35, 3.55, 4.2, 5.8]

LEG_LIST = [
    EVLeg(1.05, 2.5),
    EVLeg(1, 2.5),
    EVLeg(1.1, 12.5),
    EVLeg(1.2, 22.5),
    EVLeg(1.05, 52.5),
    EVLeg(1.1, 7.5),
    EVLeg(1.22, 82.5),
    EVLeg(1.05, 72.5),
    EVLeg(1.13, 62.5),
    EVLeg(1.244, 52.5),
    EVLeg(1.035, 32.5),
    EVLeg(1.1123, 42.5)
    ]


# solution = selection
# of
# items

def init():
    # return 4 random items from LEG_LIST
    def random_item():
        return random.choice(LEG_LIST)

    return set(random_item() for _ in range(4))

def fitness(solution):
    # return the product of the evs of the legs
    return np.prod([leg.ev for leg in solution])

def selection(population):
    # return the best 4 items from the population
    return sorted(population, key=fitness, reverse=True)[:10]

def crossover(parent1, parent2):
    # return a new set of items by combining the items from the parents
    return set(parent1).union(parent2)

def mutation(solution):
    # return a new set of items by adding a random item to the solution
    new_solution = set(solution)
    new_solution.add(random.choice(LEG_LIST))
    return new_solution

def genetic_algorithm():
    # initialise the population
    population = [init() for _ in range(100)]

    # keep track of the best solution
    best_solution = None
    best_fitness = 0

    # keep track of the average fitness
    avg_fitness = 0

    # keep track of the number of iterations
    iterations = 0

    # keep going until we reach a solution
    while best_fitness < 3:
        # select the best solutions from the population
        population = selection(population)

        # keep track of the best solution
        if fitness(population[0]) > best_fitness:
            best_fitness = fitness(population[0])
            best_solution = population[0]

        # keep track of the average fitness
        avg_fitness = sum(fitness(solution) for solution in population) / len(population)

        # create a new population
        new_population = []

        # add the best solution to the new population
        new_population.append(best_solution)

        # add the children to the new population
        for _ in range(len(population) - 1):
            # select two parents
            parent1 = random.choice(population)
            parent2 = random.choice(population)

            # create a child by crossing over the parents
            child = crossover(parent1, parent2)

            # mutate the child
            child = mutation(child)

            # add the child to the new population
            new_population.append(child)

        # replace the old population with the new population
        population = new_population

        # keep track of the number of iterations
        iterations += 1

        # print the best solution
        print("Best solution: {}, Fitness: {}, Avg. Fitness: {}, Iterations: {}".format(
            best_solution, best_fitness, avg_fitness, iterations
        ))

    return best_solution, best_fitness, avg_fitness, iterations




def optimise(df_legs):
    # Using deap, create a model that uses machine learning to formulate the best combinations of legs to bet on
    # This means that it will try to combine legs that are likely to create high ev returns
    # The model will be constrained by a maximum and minumum total odds or variance for the bet

    # sample algo goals
    average_lucky_ev = 1.1
    average_lucky_variance = 0.1
    average_lucky_single_win_odds = 3.5
    average_lucky_total_win_odds = 5000

    # set S is a group of 100 individual legs
    # set Q is a group of 4 legs from S
    # set P is a group of 25 legs from Q, such that each leg in Q only appears once in P

    # Optimise the sum of the product of the ev of each leg in P and the probability of each leg in P

    # Use genetic algorithm to find the best combinations for leg_splits

    leg_splits = [[df_legs[x-1], df_legs[2*x -1], df_legs[3*x-1], df_legs[4*x-1]] for x in range(0, len(df_legs), 4)]

    # optimisation_function = sum([Lucky(leg_list).EV for leg_list in leg_splits])




    # Python combinatorial optimisation
    # Create a list of all the combinations of the legs, from 1 to 4
    combinations = []
    for i in range(1, 4):
        # Add the combinations of the legs to the list
        combinations.extend(list(itertools.combinations(legs, i)))


    pass

def lucky_15(legs):
    combinations = []
    # Create a list of all the combinations of the legs, from 1 to 4
    for i in range(1, 4):
        # Add the combinations of the legs to the list
        combinations.extend(list(itertools.combinations(legs, i)))

    # Create a list of all the combinations of the legs
    combinations_return = []
    for combination in combinations:
        # Create a list of all the combinations of the legs
        combination_return = 1
        # Create a list of all the combinations of the legs
        for leg in combination:
            # Create a list of all the combinations of the legs
            combination_return *= leg
        # Create a list of all the combinations of the legs
        combinations_return.append(combination_return)
    # Create a dataframe of the combinations and total returns
    df = pd.DataFrame({
        'combinations': combinations,
        'return': combinations_return
    })
    # Return the dataframe
    return df


def luckyify(legs, single_win_multi=1, total_win_multi=1):
    # Create a dataframe of the combinations and total returns
    combinations = []

    for i in range(len(legs) + 1):
        # Add the combinations of the legs to the list
        combinations.extend(list(itertools.combinations(legs, i)))

    returns = []
    for combo in combinations:
        # Create a list of all the combinations of the legs
        combination_return = 1
        # Create a list of all the combinations of the legs
        for leg in combo:
            # Create a list of all the combinations of the legs
            combination_return *= leg

        if len(combo) == 1:
            combination_return *= single_win_multi
        elif len(combo) == len(legs):
            combination_return *= total_win_multi
        # Create a list of all the combinations of the legs
        returns.append(combination_return)

    df = pd.DataFrame({
        'combinations': combinations,
        'return': returns
    })
    # Return the dataframe
    return df


# if name is main
if __name__ == "__main__":

    print(genetic_algorithm())
    legs = [1.5, 15, 26, 34, 19, 54]
    df = luckyify(legs)
    print(df)

    total_return = df['return'].sum()
    print(total_return)

    # Input x amount of legs, which contain the event, the given odds, the true odds, the each way odds, the each way true odds
    # Algorithm should optimise the legs into the best combination of lucky 15s, 31s and 63s
    # It can do this by considering an appropriate variance for an entire combination, as well as balancing the evs in each combo
    # No two legs with the same event should be in the same combination
    # The algorithm should consider the amount to stake on each combination, using kelly criterion
    # The algorithm will use ML to optimise the bets according to the single_win multiplier and total_win multiplier
    # The best way to do this atm may be brute forcing every combination, then selecting according to ev and variance
    # The current best way to do this is to use a genetic algorithm to optimise the bets
    # The ranking for how good the bet is can just be ranked on its kelly criterion stake
    # As this considers the variance and edge of the bet
