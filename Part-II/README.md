# Pioneer Delivery Algorithm Portfolio
## Part II: Divide and Conquer

**Language:** Python 3.9 or newer. The program, tests, and timing script only use
the standard library, so there are no packages to install.

This part is its own project inside the `Part-II` folder. It does not need the
code from Part I. Open this folder in VS Code, or change into it in a terminal.

## Run the project

From the repository folder:

```bash
cd Part-II
python3 main.py
```

This runs A-C using `data/example.json`. On Windows, use `python` or `py` instead
of `python3` if that is the command for your Python installation.

Each part can also run on its own:

```bash
python3 main.py --task a
python3 main.py --task b
python3 main.py --task c
python3 main.py --task a --file data/example.json
```

The example prints closest pair C, D with squared distance 1, an inversion count
of 2, and a delivery time of 16 at rank 5.

## See the test inputs and outputs

```bash
python3 main.py --cases
python3 main.py --cases --task a
python3 -m unittest discover -s tests -v
```

`--cases` prints each saved case, its expected answer, its actual answer, and
PASS or FAIL. It also saves the results in `results/case_results.txt` and
`results/case_results.json`. Selecting one part adds `_a`, `_b`, or `_c` to those
filenames, so it does not overwrite the results for all parts.

The saved inputs are in `data/test_cases.json`. There are 22 cases: A1-A7,
B1-B6, and C1-C9. These include every required case and extension, plus extra
cases for each task. The automated test file also checks the results against
simple reference solutions on 200 small inputs per task. Part C checks every
valid rank on each of those inputs. All 34 automated tests passed; the recorded
test output is in `results/test_results.txt`.

## Input format

The input is a JSON object. It needs only the fields for the task being run.
Running all three parts needs all the fields shown in `data/example.json`.

For A, locations are `[ID, x, y]`. IDs must be unique nonempty strings.
Coordinates must be integers, two points cannot share the same coordinates,
and at least two points are needed.

```json
{"locations": [["A", 0, 0], ["B", 3, 4]]}
```

For B, both orders contain the same distinct delivery IDs exactly once. IDs can
be strings or integers in the JSON input. At least one delivery is needed.

```json
{"planned": ["A", "B", "C"], "actual": ["B", "A", "C"]}
```

For C, times are nonnegative integers. `k` starts at 1, so 1 means the minimum
and the number of values means the maximum. Repeated values take separate ranks.

```json
{"times": [18, 4, 29, 11, 4, 16, 35, 9, 22], "k": 5}
```

Invalid input gives a clear terminal error. The algorithm functions raise
`ValueError` for inputs outside their documented assumptions. They do not change
the original lists. Task A returns `((first_ID, second_ID), squared_distance)`;
B returns an integer count; C returns the selected integer. Tied closest pairs
can return any minimizing pair, in either ID order.

Two large saved tests use generator descriptions to avoid typing thousands of
values into the JSON file. `main.py` expands them before running the algorithm:

- B5 uses `{"generator": "reversed_dispatch", "n": 100000}`. Planned IDs are
  the integers 1 through n, and actual IDs are those same integers reversed.
  The expected answer is 4,999,950,000.
- C8 uses `{"generator": "duplicate_times", "n": 5000, "distinct": 23, "k": 2500}`.
  Value i is `(i * 17) % 23` for i from 0 through 4,999. The expected answer is 11.

## Files

```text
Part-II/
  algorithms.py           Algorithms A-C and their recursive helper functions
  main.py                 Reads input, chooses the task, and prints the answers
  benchmark.py            Measures all three algorithms at increasing sizes
  data/example.json       Example input for A-C
  data/test_cases.json    Required cases, extra cases, and expected answers
  tests/test_project.py   Automated checks and simple reference solutions
  results/               Saved case outputs, test output, and measured timings
  report.pdf             Task D report: design, analysis, tests, and timings
  report.md              Editable text of the same report
  .vscode/               Run, test, and debug configurations for VS Code
  README.md              How to run and test the project
```

In VS Code, Cmd+Shift+B on Mac runs the example. **Terminal > Run Task** also
includes **Show Part II case results** and **Test Part II**. The tasks work
without extensions. F5 debugging uses Microsoft's Python and Python Debugger
extensions if they are already installed.

## Part A: closest delivery locations

Sorts the locations once by x and once by y. Splits the x-list into two halves
and keeps the correct y-list for each half using IDs. This matters when two
locations have the same x-value. Recursion finds the closest pair on each side.

Then checks the strip near the dividing line for a closer cross-half pair.
The strip stays in y-order and each point checks at most the next seven points,
so it does not compare every pair. Squared distances keep the calculations exact.

Time is O(n log n), including the initial sorts. Auxiliary space is O(n), with
an O(log n) recursion depth. The small base case checks all pairs for at most
three points.

## Part B: counting dispatch-order inversions

Turns actual delivery IDs into their positions in the planned order. The ranks
start at 0 in the code, which gives the same answer as starting at 1. Splits the
ranks into halves and recursively counts the inversions in each half.

When merging, if a value on the right is smaller than the next value on the
left, it is smaller than every remaining value on the left. Adds all those
inversions at once using `len(left) - i`. Each reversed pair is counted exactly
once, either inside a half or while merging across halves.

The merge-sort work is O(n log n), and auxiliary space is O(n). Python integers
can represent the required large count without a 32-bit overflow.

## Part C: selecting a delivery-time threshold

Uses groups of at most five values. Sorts each small group and takes its median,
then recursively selects the median of those medians as the pivot. It does not
sort the whole dataset or use a random pivot.

Splits the values into lower, equal, and higher groups. If k is in the lower
group, k stays the same. If it falls in the equal group, the answer is the
pivot. Otherwise, it goes into the higher group and subtracts the sizes of both
the lower and equal groups from k. This also handles repeated values correctly.

The pivot guarantees that a constant fraction can be discarded. The recurrence
is `T(n) <= T(ceil(n/5)) + T(7n/10 + O(1)) + O(n)`, giving O(n) worst-case time.
The list-based implementation uses O(n) auxiliary space, with O(log n) stack
depth. Only groups and base cases of five or fewer values are sorted.

## Part D: report and measured timings

The two-page report is `report.pdf`. Its editable text is `report.md`.
To reproduce the timings, run:

```bash
python3 benchmark.py --sizes 100 1000 5000 --repeats 7
```

The timing script creates its inputs before starting the timer, runs one warm-up,
then records seven runs per task and size. The median and all samples are saved
in `results/timings.json`. Validation inside each public algorithm is included.
Rerunning the script replaces the timings file; the included PDF records the
original measured run. Timings will vary by machine and system load.

## Submit

Submit the `Part-II` folder as one ZIP, including the source, data, test outputs,
README, and `report.pdf`. Leave out `.git`, `__pycache__`, and virtual environments.
The GitHub link is for the portfolio; Canvas still needs the ZIP submission.
