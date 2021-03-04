import argparse
import glob
import json
import matplotlib.pyplot as plt
import numpy as np
import os
import pandas as pd
import pathlib as path
import seaborn as sns
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
    help="baseline path",
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

parser.add_argument(
    "--debug",
    action="store_true",
    default=False,
    help="enable printing of debugging details",
)

parser.add_argument(
    "--ignore",
    help="String of comma-separated PerfStats metrics to ignore, e.g. 'Compositing,Layer Transactions'"
)

options = parser.parse_args()
base = os.path.dirname(os.path.realpath(__file__))


x_axis = 'asyncOpen to onStopRequest, ms'
if options.xaxis is not None:
    x_axis = options.xaxis

ignore_list = []
if options.ignore is not None:
    ignore_list = options.ignore.split(',')
    print( "ignore_list:" + str(ignore_list) )

baseline_results = []


if options.baseline is None:
    options.baseline = '.'

# Load the browsertime values
browsertimeData = {}
browsertimeMetrics = ['loadEventEnd', 'timeToContentfulPaint']

browsertime_files = path.Path(options.baseline).rglob('browsertime.json')
for browsertime_file in browsertime_files:
    if options.debug: print('Processing browsertime: ' + str(path))
    with open(browsertime_file) as f:
        data = json.load(f)
        for script in data[0]['browserScripts']:
            for metric in browsertimeMetrics:
                if metric not in browsertimeData:
                    browsertimeData[metric] = []
                browsertimeData[metric].append(script['timings'][metric])

print (str(browsertimeData))

# Collect all the perfstats metrics.
perfStats = {}

# Load perfstats
files = path.Path(options.baseline).rglob('perfStats*.json')
for path in files:
    if options.debug: print('Processing perfstats: ' + str(path))
    with open(path) as f:
       data = json.load(f)

       # Find the correct content process
       for process in data['processes']:
           if (process['type'] == 'content'):
                for url in process['urls']:
                   if url.startswith('https'):
                     if options.debug: print( str(url) )

                     for metric in process['perfstats']['metrics']:
                        if str(metric['metric']) in ignore_list:
                            if options.debug: print ('Ignoring metric: ' + str(metric))
                        else:
                            value = metric['time']
                            baseline_results.append(value)
                            if metric['metric'] not in perfStats:
                                perfStats[metric['metric']] = []

                            perfStats[metric['metric']].append(value)

if options.debug:
    print("perfStats")
    print( str(perfStats))

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
df = df_baseline = pd.DataFrame.from_dict(perfStats)

#print(str(df))

if browsertimeData:
    df_browsertime = pd.DataFrame.from_dict(browsertimeData)
    print( str(df_browsertime) )
    df = pd.concat([df_baseline,df_browsertime], axis=1)

print(str(df.std()))
print(str(df.mean()))

df_rel_std = df.std().div(df.mean())


df_rel_std = df_rel_std.multiply(100.0)
print('Relative std deviation %')
print(str(df_rel_std))

# if test_results != None:
#     df_test = pd.DataFrame(data=test_results, columns=[labels[1]])
#     df = pd.concat([df_baseline,df_test], axis=1)


# if test_results != None:
#     df_test = pd.DataFrame(data=test_results, columns=[labels[1]])
#     df = pd.concat([df_baseline,df_test], axis=1)

# Plot the data

# Histogram
plt.hist(df, bins=30)
plt.legend(prop={'size': 10})
plt.legend(loc='upper right')
plt.gca().set(title=x_axis, ylabel='Frequency');

# kernel density estimate
# kde = sns.displot(data=df, kind="kde", bw_adjust=.15)
# kde.set(xlabel=x_axis)

#empirical cumulative distribution function
#ecdf = sns.displot(data=df, kind="ecdf")
#ecdf.set(xlabel=x_axis)

# boxplot
boxplot = sns.boxplot(data=df)
boxplot.set(xlabel='metric')
boxplot.set(ylabel='ms')

# scatter = sns.scatterplot(data=df)
# scatter.set(xlabel='metric')
# scatter.set(ylabel='ms')


plt.show()