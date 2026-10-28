"""Records real timings for Task D. Input generation is outside the timer."""

import argparse
import json
from pathlib import Path
import platform
import random
import statistics
import sys
import time

from algorithms import closest_locations, count_inversions, select_delivery_time

ROOT = Path(__file__).resolve().parent


def measure(function, arguments, repeats):
    # Runs once first, then uses the median so one slow run has less influence.
    function(*arguments)
    samples = []
    for _ in range(repeats):
        start = time.perf_counter()
        function(*arguments)
        samples.append(time.perf_counter() - start)
    return samples


def main(argv=None):
    parser = argparse.ArgumentParser(description="Measure the three Part II algorithms")
    parser.add_argument("--sizes", nargs="+", type=int, default=[100, 1000, 5000])
    parser.add_argument("--repeats", type=int, default=7)
    args = parser.parse_args(argv)
    if any(size < 2 for size in args.sizes) or args.repeats < 1:
        parser.error("sizes must be at least 2 and repeats must be positive")

    rows = []
    for n in args.sizes:
        randomizer = random.Random(601 + n)
        coordinates = set()
        points = []
        while len(points) < n:
            position = (randomizer.randrange(-10 * n, 10 * n),
                        randomizer.randrange(-10 * n, 10 * n))
            if position not in coordinates:
                coordinates.add(position)
                points.append((f"P{len(points)}", *position))
        planned = list(range(n))
        actual = planned[:]
        randomizer.shuffle(actual)
        times = [randomizer.randrange(n // 4 + 1) for _ in range(n)]
        tasks = [("A", closest_locations, (points,)),
                 ("B", count_inversions, (planned, actual)),
                 ("C", select_delivery_time, (times, (n + 1) // 2))]
        for task, function, arguments in tasks:
            samples = measure(function, arguments, args.repeats)
            median_ms = statistics.median(samples) * 1000
            rows.append({"task": task, "n": n, "median_ms": median_ms,
                         "samples_ms": [sample * 1000 for sample in samples]})
            print(f"Task {task} | n={n:>6} | median={median_ms:.4f} ms")

    result = {"python": platform.python_version(), "implementation": sys.implementation.name,
              "system": platform.system(), "machine": platform.machine(),
              "seed_rule": "601 + n", "repeats": args.repeats,
              "method": "one warm-up; median perf_counter time; input generation excluded; validation included",
              "rows": rows}
    output = ROOT / "results"
    output.mkdir(exist_ok=True)
    (output / "timings.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
