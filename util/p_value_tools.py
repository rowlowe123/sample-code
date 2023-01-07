# Create a tool that takes a sample of binominal results and returns the range of values for 1% significance
import math

import pytest as pytest
from scipy import stats




def bin_from_sample(sample, significance=0.01):
    # Get the sample size
    n = len(sample)
    # Get the number of successes
    k = sum(sample)
    # Get the probability of success
    p = k / n
    # Get the standard deviation
    std = math.sqrt(p * (1 - p) / n)
    # Get the z score
    z = stats.norm.ppf(1 - significance / 2)
    # Get the range of values
    lower = p - z * std
    upper = p + z * std
    # Return the range of values
    return (lower, upper)

def bin_from_agg(success, sample_size, significance):
    # Get the probability of success
    p = success / sample_size
    # Get the standard deviation
    std = math.sqrt(p * (1 - p) / sample_size)
    # Get the z score
    z = stats.norm.ppf(1 - significance / 2)
    # Get the range of values
    lower = p - z * std
    upper = p + z * std

    # Must be between 0 and 1
    if lower < 0:
        return long_bin_calc(success, sample_size, significance, upper_bound=upper)
    if upper > 1:
        return long_bin_calc(success, sample_size, significance, lower_bound=lower)
    # Return the range of values
    return (lower, upper)

def long_bin_calc(success, sample_size, significance, upper_bound=1, lower_bound=0):
    # Find the lowest value that is significant
    lower = lower_bound
    upper = upper_bound
    # Use a binominal distribution to find the lower bound where the probability of success is significant
    rate = success / sample_size


    # Use a binominal distribution to find the upper bound where the probability of success is significant
    while significance/2 > stats.binom.cdf(success, sample_size, upper):
        upper -= 0.00001
    # repeat with lowe bound
    while 1 - significance/2 < stats.binom.cdf(success, sample_size, lower):
        lower += 0.00001

    return lower, upper

# use prebuilt library to do above routine
def short_bin_calc(success, sample_size, significance):
    # Find the lowest value that is significant
    lower = 0
    upper = 1
    # Use a binominal distribution to find the lower bound where the probability of success is significant
    rate = success / sample_size
    lower = stats.binom.ppf(significance, sample_size, rate)
    # Use a binominal distribution to find the upper bound where the probability of success is significant
    upper = stats.binom.ppf(1 - significance, sample_size, rate)
    return (lower, upper)
# Test the function

# Create a sample

sample = [0, 0, 0, 0, 0,
          0, 0, 0, 0, 0,
          0, 0, 0, 0, 0,
          0, 0, 0, 0, 0,
          1, 1, 1, 1, 1,
          1, 1, 1, 1, 1,
          1, 1, 1, 1, 1,
          1, 1, 1, 1, 1,
          1, 1, 1, 1, 1]

# Get the range of values

# Create unit tests

# Using pytest

# Create sample data success rates
made_nums = [0, 15, 76, 124, 128, 235, 354, 657]
sample_nums = [0, 6, 34, 100, 200, 235, 300, 400, 500, 600]
sigs = [0.01, 0.05, 0.1, 0.2, 0.3]
# Create a set of marks from the above arrays
# @pytest.mark.parametrize("made", made_nums)
# @pytest.mark.parametrize("sample", sample_nums)
# @pytest.mark.parametrize("sig", sigs)
# Create sets where made_num is less than sample num for each sig
sample_sets = [(made, sample, sig) for made in made_nums for sample in sample_nums for sig in sigs if made < sample]
@pytest.mark.parametrize("made, sample, sig", sample_sets)



def test_bin_from_agg_equals_long_calc(made, sample, sig):
    # assert to 2 sig fig
    assert round(bin_from_agg(made, sample, sig)[1], 2) == round(long_bin_calc(made, sample, sig)[1], 2)


def test_bin_from_sample(sample, significance, expected):
    assert bin_from_sample(sample, significance) == expected



def test_bin_from_agg(success, sample_size, significance, expected):
    assert bin_from_agg(success, sample_size, significance) == expected


def test_bin_from_agg_equals_long_calc():
    # assert to 3 sig fig
    assert round(bin_from_agg(2000, 4000, 0.01)[1], 2) == round(long_bin_calc(2000, 4000, 0.01)[1], 2)


# Run tests
if __name__ == "__main__":
    pytest.main()