"""Checks the saved cases, invalid inputs, and answers from simple references."""

import builtins
import contextlib
import io
import json
from pathlib import Path
import random
import tempfile
import unittest
from unittest.mock import patch

from algorithms import closest_locations, count_inversions, select_delivery_time
from main import case_passes, expand_input, main, run_task

ROOT = Path(__file__).resolve().parent.parent
CASES = json.loads((ROOT / "data" / "test_cases.json").read_text())


def brute_closest(points):
    # Tries every pair only as a reference on small test inputs.
    return min((first[1] - second[1]) ** 2 + (first[2] - second[2]) ** 2
               for i, first in enumerate(points) for second in points[i + 1:])


def brute_inversions(planned, actual):
    ranks = {identifier: i for i, identifier in enumerate(planned)}
    return sum(ranks[actual[i]] > ranks[actual[j]]
               for i in range(len(actual)) for j in range(i + 1, len(actual)))


class SavedCases(unittest.TestCase):
    """Each required or extra case gets its own PASS or FAIL result."""

    def check_case(self, task, case):
        data = expand_input(case["input"])
        original = json.loads(json.dumps(data))
        result = run_task(task.lower(), data)
        self.assertTrue(case_passes(task.lower(), data, result, case["expected"]),
                        f"expected {case['expected']}; actual {result}")
        self.assertEqual(data, original, "the algorithm should not change the input")


def saved_test(task, case):
    def test(self):
        self.check_case(task, case)
    test.__doc__ = case["description"]
    return test


for task, task_cases in CASES.items():
    for case in task_cases:
        setattr(SavedCases, "test_" + case["name"], saved_test(task, case))


class ReferenceTests(unittest.TestCase):
    def test_A_against_every_pair_on_200_small_inputs(self):
        randomizer = random.Random(2101)
        grid = [(x, y) for x in range(-10, 11) for y in range(-10, 11)]
        for _ in range(200):
            positions = randomizer.sample(grid, randomizer.randrange(2, 35))
            points = [(f"P{i}", x, y) for i, (x, y) in enumerate(positions)]
            pair, distance = closest_locations(points)
            self.assertEqual(distance, brute_closest(points))
            locations = {identifier: (x, y) for identifier, x, y in points}
            self.assertNotEqual(pair[0], pair[1])
            first, second = locations[pair[0]], locations[pair[1]]
            self.assertEqual(distance, (first[0] - second[0]) ** 2 + (first[1] - second[1]) ** 2)

    def test_A_only_sorts_the_two_initial_lists(self):
        points = [(f"P{i}", i % 4, i) for i in range(100)]
        calls = []

        def tracked_sort(values, **kwargs):
            calls.append(len(values))
            return builtins.sorted(values, **kwargs)

        with patch("algorithms.sorted", tracked_sort, create=True):
            self.assertEqual(closest_locations(points)[1], brute_closest(points))
        self.assertEqual(calls, [100, 100])

    def test_B_against_nested_loops_on_200_small_inputs(self):
        randomizer = random.Random(2102)
        for _ in range(200):
            planned = [f"D{i}" for i in range(randomizer.randrange(1, 45))]
            randomizer.shuffle(planned)
            actual = planned[:]
            randomizer.shuffle(actual)
            self.assertEqual(count_inversions(planned, actual), brute_inversions(planned, actual))

    def test_C_every_rank_against_sorting_on_200_small_inputs(self):
        randomizer = random.Random(2103)
        for _ in range(200):
            values = [randomizer.randrange(21) for _ in range(randomizer.randrange(1, 65))]
            expected = sorted(values)
            for k, answer in enumerate(expected, 1):
                self.assertEqual(select_delivery_time(values, k), answer)

    def test_C_never_sorts_more_than_five_values(self):
        values = [(i * 31) % 83 for i in range(700)]
        expected = sorted(values)[350]

        def small_sort(group, **kwargs):
            self.assertLessEqual(len(group), 5, "only small groups may be sorted")
            return builtins.sorted(group, **kwargs)

        with patch("algorithms.sorted", small_sort, create=True):
            self.assertEqual(select_delivery_time(values, 351), expected)


class InvalidInputTests(unittest.TestCase):
    def test_A_rejects_invalid_locations(self):
        invalid = [[], [("A", 0, 0)], [("A", 0, 0), ("A", 1, 1)],
                   [("A", 0, 0), ("B", 0, 0)], [("A", 0.5, 1), ("B", 1, 2)],
                   [("A", 0), ("B", 1, 2)], [(1, 0, 0), ("B", 1, 2)]]
        for points in invalid:
            with self.subTest(points=points), self.assertRaises(ValueError):
                closest_locations(points)

    def test_B_rejects_invalid_dispatch_orders(self):
        invalid = [([], []), (["A"], []), (["A", "A"], ["A", "A"]),
                   (["A", "B"], ["A", "C"]), ([[1]], [[1]])]
        for planned, actual in invalid:
            with self.subTest(planned=planned, actual=actual), self.assertRaises(ValueError):
                count_inversions(planned, actual)

    def test_C_rejects_invalid_times_and_ranks(self):
        invalid = [([], 1), ([1], 0), ([1], 2), ([1], 1.0), ([1], True),
                   ([-1, 2], 1), ([1.5, 2], 1), ([True, 2], 1)]
        for times, k in invalid:
            with self.subTest(times=times, k=k), self.assertRaises(ValueError):
                select_delivery_time(times, k)


class ProgramTests(unittest.TestCase):
    def test_default_program_shows_all_three_tasks(self):
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            self.assertEqual(main([]), 0)
        for letter in "ABC":
            self.assertIn("TASK " + letter, output.getvalue())

    def test_one_task_needs_only_its_own_fields(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "input.json"
            path.write_text(json.dumps({"times": [5, 0, 5], "k": 2}))
            output = io.StringIO()
            with contextlib.redirect_stdout(output):
                self.assertEqual(main(["--task", "c", "--file", str(path)]), 0)
            self.assertIn("Delivery time at rank 2: 5", output.getvalue())
            self.assertNotIn("TASK A", output.getvalue())

    def test_bad_json_has_a_clear_error(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "bad.json"
            path.write_text("{broken")
            output = io.StringIO()
            with contextlib.redirect_stderr(output), self.assertRaises(SystemExit) as error:
                main(["--file", str(path)])
            self.assertEqual(error.exception.code, 2)
            self.assertIn("error:", output.getvalue())
            self.assertNotIn("Traceback", output.getvalue())

    def test_missing_field_has_a_clear_error(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "input.json"
            path.write_text("{}")
            output = io.StringIO()
            with contextlib.redirect_stderr(output), self.assertRaises(SystemExit):
                main(["--task", "a", "--file", str(path)])
            self.assertIn("missing input field: locations", output.getvalue())


if __name__ == "__main__":
    unittest.main()
