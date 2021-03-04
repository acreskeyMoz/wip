import argparse
import matplotlib.pyplot as plt
import numpy as np
import os
import seaborn as sns
import pandas as pd
from scipy import stats


def filter(input, threshold):
    print('Removing outliers over ' + str(threshold))
    output = [ x for x in input if x <= threshold ]
    return output

def print_summary(name, input):
    print ('------------------\n' +  name)
    print (pd.DataFrame(input).describe(percentiles=[.10, .25, .50, .75, .90, .95] ))
    print ('------------------\n\n')

def list_from_file(filename):
    with open(filename) as f:
        content = f.readlines()

    content = [x.strip() for x in content]
    as_float = [float(i) for i in content]
    return as_float



global options
parser = argparse.ArgumentParser(
    description="",
    prog="plot_cache_time",
)

parser.add_argument(
    "--baseline",
    help="baseline input file",
)

parser.add_argument(
    "--filter",
    help="filter results over given value",
)

parser.add_argument(
    "--test",
    help="test input file",
)

parser.add_argument(
    "--xaxis",
    help="x axis label",
)

options = parser.parse_args()
base = os.path.dirname(os.path.realpath(__file__))

x_axis = 'asyncOpen to onStopRequest, ms'
if options.xaxis != None:
    x_axis = options.xaxis

if options.baseline != None:
    filename = options.baseline
else:
    filename = os.path.join(base, 'data.txt')

with open(filename) as f:
    content = f.readlines()

baseline_results = list_from_file(filename)

if options.filter != None:
    baseline_results = filter(baseline_results, float(options.filter))

print_summary('baseline', baseline_results)

# If test results are provided, load them and run statistical comparison
test_results = None
if options.test != None:

    test_results = list_from_file(options.test)

    if options.filter != None:
        test_results = filter(test_results, float(options.filter))

    print_summary('test', test_results)

    t_test = stats.ttest_ind(baseline_results,test_results)
    print(t_test)

    mannwhitneyu = stats.mannwhitneyu(baseline_results,test_results, use_continuity=True, alternative='two-sided')
    print(mannwhitneyu)

# Build the dataframe
labels = ["baseline", "test"]
df = df_baseline = pd.DataFrame(data=baseline_results, columns=[labels[0]])

if test_results != None:
    df_test = pd.DataFrame(data=test_results, columns=[labels[1]])
    df = pd.concat([df_baseline,df_test], axis=1)

# Plot the data

# Histogram
plt.hist(df, bins=30, label=labels)
plt.legend(prop={'size': 10})
plt.legend(loc='upper right')
plt.gca().set(title=x_axis, ylabel='Frequency');

# kernel density estimate
kde = sns.displot(data=df, kind="kde", bw_adjust=.15)
kde.set(xlabel=x_axis)

# empirical cumulative distribution function
ecdf = sns.displot(data=df, kind="ecdf")
ecdf.set(xlabel=x_axis)

plt.show()