"""
Greedy Algorithm Templates in Python:
1. Activity Selection / Interval Scheduling (Max non-overlapping intervals)
2. Minimum Meeting Rooms / Overlap (Sweep Line / Event Sorting)
"""

import sys

def max_non_overlapping_intervals(intervals):
    """
    Selects the maximum number of mutually non-overlapping intervals.
    Greedy strategy: Sort intervals by end time ascending.
    Time Complexity: O(N log N)
    """
    if not intervals:
        return 0
    # Sort by end time
    intervals.sort(key=lambda x: x[1])
    
    count = 1
    last_end = intervals[0][1]
    
    for start, end in intervals[1:]:
        if start >= last_end:
            count += 1
            last_end = end
            
    return count

def min_meeting_rooms(intervals):
    """
    Given intervals of meetings, find the minimum number of rooms required.
    Greedy event sorting: +1 on start, -1 on end.
    Time Complexity: O(N log N)
    """
    events = []
    for start, end in intervals:
        events.append((start, 1))   # Meeting starts
        events.append((end, -1))    # Meeting ends
        
    # Sort events. If times are equal, process end (-1) before start (+1)
    events.sort(key=lambda x: (x[0], x[1]))
    
    current_rooms = 0
    max_rooms = 0
    for time_pt, delta in events:
        current_rooms += delta
        max_rooms = max(max_rooms, current_rooms)
        
    return max_rooms

TEST_CASES = [
    (
        "3\n1 4\n3 5\n0 6",
        "1"
    ),
    (
        "4\n1 2\n2 3\n3 4\n4 5",
        "4"
    )
]

def solve():
    tokens = sys.stdin.read().split()
    if not tokens:
        return
    it = iter(tokens)
    n = int(next(it))
    intervals = []
    for _ in range(n):
        s = int(next(it))
        e = int(next(it))
        intervals.append((s, e))
    ans = max_non_overlapping_intervals(intervals)
    sys.stdout.write(str(ans) + "\n")

if __name__ == "__main__":
    solve()
