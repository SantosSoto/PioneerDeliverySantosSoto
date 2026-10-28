"""Reads the JSON input and prints the answers for Part II.

Run python3 main.py for the example, or python3 main.py --cases to see tests.
"""

import argparse
import json
from pathlib import Path

from algorithms import closest_locations, count_inversions, select_delivery_time

ROOT = Path(__file__).resolve().parent


def run_task(task, data):
    """Calls one algorithm so the parts can run independently."""
    if task == "a":
        pair, distance = closest_locations(data["locations"])
        return {"pair": list(pair), "squared_distance": distance}
    if task == "b":
        return count_inversions(data["planned"], data["actual"])
    if task == "c":
        return select_delivery_time(data["times"], data["k"])
    raise ValueError("task must be a, b, or c")


def expand_input(data):
    """Builds the two large test inputs from their small saved descriptions."""
    if data.get("generator") == "reversed_dispatch":
        planned = list(range(1, data["n"] + 1))
        return {"planned": planned, "actual": planned[::-1]}
    if data.get("generator") == "duplicate_times":
        return {"times": [(i * 17) % data["distinct"] for i in range(data["n"])],
                "k": data["k"]}
    return data


def case_passes(task, data, actual, expected):
    if task != "a":
        return actual == expected
    # Checks the IDs too, so a correct distance with a wrong pair does not pass.
    locations = {point[0]: point[1:] for point in data["locations"]}
    first, second = actual["pair"]
    if first == second or first not in locations or second not in locations:
        return False
    x1, y1 = locations[first]
    x2, y2 = locations[second]
    distance = (x1 - x2) ** 2 + (y1 - y2) ** 2
    if distance != actual["squared_distance"] or distance != expected["squared_distance"]:
        return False
    return "pair" not in expected or set(actual["pair"]) == set(expected["pair"])


def run_cases(task="all"):
    """Prints expected and actual answers, then saves the same results."""
    cases = json.loads((ROOT / "data" / "test_cases.json").read_text(encoding="utf-8"))
    results = []
    lines = []
    for letter, task_cases in cases.items():
        if task not in ("all", letter.lower()):
            continue
        for case in task_cases:
            data = expand_input(case["input"])
            actual = run_task(letter.lower(), data)
            passed = case_passes(letter.lower(), data, actual, case["expected"])
            result = {"case": case["name"], "description": case["description"],
                      "expected": case["expected"], "actual": actual, "passed": passed}
            results.append(result)
            lines.append(f"{case['name']}: {case['description']}\n"
                         f"  Expected: {json.dumps(case['expected'])}\n"
                         f"  Actual:   {json.dumps(actual)}\n"
                         f"  {'PASS' if passed else 'FAIL'}")
    passed_count = sum(result["passed"] for result in results)
    lines.append(f"\n{passed_count}/{len(results)} cases passed.")
    report = "\n".join(lines) + "\n"
    print(report, end="")
    output = ROOT / "results"
    output.mkdir(exist_ok=True)
    suffix = "" if task == "all" else "_" + task
    (output / f"case_results{suffix}.json").write_text(json.dumps(results, indent=2) + "\n", encoding="utf-8")
    (output / f"case_results{suffix}.txt").write_text(report, encoding="utf-8")
    return 0 if passed_count == len(results) else 1


def main(argv=None):
    parser = argparse.ArgumentParser(description="Pioneer Delivery | Part II: Divide and Conquer")
    parser.add_argument("--task", type=str.lower, choices=("all", "a", "b", "c"), default="all")
    parser.add_argument("--file", type=Path, default=ROOT / "data" / "example.json")
    parser.add_argument("--cases", action="store_true", help="print and save the required and extra test results")
    args = parser.parse_args(argv)
    try:
        if args.cases:
            return run_cases(args.task)
        data = json.loads(args.file.read_text(encoding="utf-8"))
        if not isinstance(data, dict):
            raise ValueError("the input JSON must be an object with the fields for the chosen task")
        for task in ("abc" if args.task == "all" else args.task):
            result = run_task(task, data)
            print(f"TASK {task.upper()}")
            if task == "a":
                print("Closest pair: " + ", ".join(result["pair"]))
                print(f"Squared distance: {result['squared_distance']}")
            elif task == "b":
                print(f"Dispatch-order inversions: {result}")
            else:
                print(f"Delivery time at rank {data['k']}: {result}")
            print()
    except KeyError as error:
        parser.error(f"missing input field: {error.args[0]}")
    except (OSError, ValueError, TypeError) as error:
        parser.error(str(error))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
