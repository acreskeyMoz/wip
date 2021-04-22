# wip
work-in-progress tools

`plot_timings.py`
Local tooling that visualizes and does some simple analysis on raw results.

You put raw results in a text file, separated by line, eg.

```
123423
29
44
...
```

And then run
`python plot_timings.py --baseline results.txt`
You can optionally add test results to compare, e.g.
`python plot_timings.py --baseline results.txt --test test_results.txt`
And some options for filtering outliers & graph titles.

<img width="927" alt="plot_timings" src="https://user-images.githubusercontent.com/44072237/115725085-88ee6200-a34f-11eb-8cc3-2550220ef308.png">
