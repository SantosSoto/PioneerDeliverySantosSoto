"""Part II contains the divide and conquer algorithms for A-C.

The functions return their answers without printing, so each part can be tested
on its own. None of them changes the original input.
"""


def closest_locations(points):
    """Part A: return ((first ID, second ID), squared distance).

    Points are (id, x, y), with unique nonempty string IDs and distinct integer
    coordinates. Raises ValueError for invalid input, including fewer than two
    points. The divide and conquer algorithm takes O(n log n) time.
    """
    if len(points) < 2:
        raise ValueError("Part A needs at least two locations")
    ids = set()
    coordinates = set()
    for point in points:
        if not isinstance(point, (list, tuple)) or len(point) != 3:
            raise ValueError("each location must contain ID, x, and y")
        identifier, x, y = point
        if not isinstance(identifier, str) or not identifier:
            raise ValueError("location IDs must be nonempty strings")
        if type(x) is not int or type(y) is not int:
            raise ValueError("location coordinates must be integers")
        if identifier in ids:
            raise ValueError("location IDs must be unique")
        if (x, y) in coordinates:
            raise ValueError("two locations cannot have identical coordinates")
        ids.add(identifier)
        coordinates.add((x, y))

    # Sorts twice at the start. Inside the recursion we keep the y-order instead
    # of sorting it again, because that would add extra work at every level.
    by_x = sorted(points, key=lambda point: (point[1], point[2], point[0]))
    by_y = sorted(points, key=lambda point: (point[2], point[1], point[0]))
    pair, distance = _closest_pair(by_x, by_y)
    return (pair[0][0], pair[1][0]), distance


def _squared_distance(first, second):
    # There is no need for a square root when comparing which pair is closer.
    return (first[1] - second[1]) ** 2 + (first[2] - second[2]) ** 2


def _closest_pair(by_x, by_y):
    if len(by_x) <= 3:
        # Only checks every pair when the group has two or three points.
        best_pair = (by_x[0], by_x[1])
        best_distance = _squared_distance(*best_pair)
        for i in range(len(by_x)):
            for j in range(i + 1, len(by_x)):
                distance = _squared_distance(by_x[i], by_x[j])
                if distance < best_distance:
                    best_pair = (by_x[i], by_x[j])
                    best_distance = distance
        return best_pair, best_distance

    middle = len(by_x) // 2
    left_x, right_x = by_x[:middle], by_x[middle:]
    dividing_x = right_x[0][1]

    # Uses IDs to split the y-list. Checking x alone would put tied x-values
    # in the wrong half, so the recursive lists would no longer match.
    left_ids = {point[0] for point in left_x}
    left_y, right_y = [], []
    for point in by_y:
        if point[0] in left_ids:
            left_y.append(point)
        else:
            right_y.append(point)

    left_pair, left_distance = _closest_pair(left_x, left_y)
    right_pair, right_distance = _closest_pair(right_x, right_y)
    if left_distance <= right_distance:
        best_pair, best_distance = left_pair, left_distance
    else:
        best_pair, best_distance = right_pair, right_distance

    # A closer cross-half pair has to be near the dividing line.
    # Filtering the y-list keeps the strip in y-order without another sort.
    strip = [point for point in by_y
             if (point[1] - dividing_x) ** 2 < best_distance]
    for i in range(len(strip)):
        # The geometric bound means only the next seven points need checking.
        # This keeps the combine step linear instead of comparing all pairs.
        for j in range(i + 1, min(i + 8, len(strip))):
            if (strip[j][2] - strip[i][2]) ** 2 >= best_distance:
                break
            distance = _squared_distance(strip[i], strip[j])
            if distance < best_distance:
                best_pair = (strip[i], strip[j])
                best_distance = distance
    return best_pair, best_distance


def count_inversions(planned, actual):
    """Part B: count reversed pairs between two dispatch orders, O(n log n).

    Orders must contain the same distinct, hashable IDs exactly once and must
    not be empty. Invalid input raises ValueError. Python integers handle the
    count even when it is larger than a 32-bit integer.
    """
    if not planned or len(planned) != len(actual):
        raise ValueError("dispatch orders must have the same nonzero length")
    try:
        planned_ids, actual_ids = set(planned), set(actual)
    except TypeError:
        raise ValueError("delivery IDs must be hashable, such as strings or integers") from None
    if len(planned_ids) != len(planned) or len(actual_ids) != len(actual):
        raise ValueError("each dispatch order must contain distinct IDs")
    if planned_ids != actual_ids:
        raise ValueError("planned and actual must contain the same delivery IDs")

    # Turns the actual IDs into their positions in the planned order.
    # Positions start at 0 here; this gives the same inversion count as 1-based.
    ranks = {identifier: i for i, identifier in enumerate(planned)}
    ranked_actual = [ranks[identifier] for identifier in actual]
    _, inversions = _merge_count(ranked_actual)
    return inversions


def _merge_count(values):
    if len(values) <= 1:
        return values[:], 0
    middle = len(values) // 2
    left, left_count = _merge_count(values[:middle])
    right, right_count = _merge_count(values[middle:])
    count = left_count + right_count
    merged = []
    i = j = 0
    while i < len(left) and j < len(right):
        if left[i] <= right[j]:
            merged.append(left[i])
            i += 1
        else:
            merged.append(right[j])
            j += 1
            # Both halves are sorted. This right value is smaller than every
            # value still left, so all those pairs are inversions at once.
            count += len(left) - i
    merged.extend(left[i:])
    merged.extend(right[j:])
    return merged, count


def select_delivery_time(times, k):
    """Part C: return the kth smallest time using median of medians, O(n).

    k is 1-based and repeated values count as separate positions. Times must be
    nonnegative integers. Invalid input or an out-of-range k raises ValueError.
    """
    if not times:
        raise ValueError("Part C needs at least one delivery time")
    if type(k) is not int or not 1 <= k <= len(times):
        raise ValueError("k must be an integer between 1 and the number of times")
    if any(type(value) is not int or value < 0 for value in times):
        raise ValueError("delivery times must be nonnegative integers")
    return _select(list(times), k)


def _select(values, k):
    if len(values) <= 5:
        # Sorting a small base case is allowed. We never sort the full dataset
        # when it has more than five values.
        return sorted(values)[k - 1]

    medians = []
    for start in range(0, len(values), 5):
        group = sorted(values[start:start + 5])
        medians.append(group[len(group) // 2])
    # Recursively selects the middle median instead of sorting all the medians.
    pivot = _select(medians, (len(medians) + 1) // 2)
    lower, equal, higher = [], [], []
    for value in values:
        if value < pivot:
            lower.append(value)
        elif value == pivot:
            equal.append(value)
        else:
            higher.append(value)

    if k <= len(lower):
        return _select(lower, k)
    if k <= len(lower) + len(equal):
        return pivot
    # Removes the positions already taken by the lower and equal groups.
    return _select(higher, k - len(lower) - len(equal))
