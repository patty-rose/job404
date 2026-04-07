"""
DS&A question bank organized by pattern.
Each question has: id, title, pattern, difficulty, prompt, hints, solution, pattern_note
"""

PATTERNS = {
    "hash_map": "Hash Map / Counter",
    "two_pointer": "Two Pointers",
    "sliding_window": "Sliding Window",
    "stack": "Stack",
    "binary_search": "Binary Search",
    "bfs_dfs": "BFS / DFS",
    "sorting": "Sorting",
}

QUESTIONS = [
    # ─── HASH MAP / COUNTER ──────────────────────────────────────────────────
    {
        "id": "two_sum",
        "title": "Two Sum",
        "pattern": "hash_map",
        "difficulty": "easy",
        "prompt": """\
Given an array of integers and a target, return the indices of the two numbers
that add up to the target. Assume exactly one solution exists.

  Input:  nums = [2, 7, 11, 15], target = 9
  Output: [0, 1]   # 2 + 7 = 9

  Input:  nums = [3, 2, 4], target = 6
  Output: [1, 2]""",
        "hints": [
            "Brute force is O(n²): for every element, scan the rest. Can you do one pass?",
            "As you walk the list, you need to know: 'have I already seen (target - current)?'"
            " Store each number you've visited — and what index it was at — in a dict.",
        ],
        "solution": """\
def two_sum(nums, target):
    seen = {}          # value -> index
    for i, num in enumerate(nums):
        complement = target - num
        if complement in seen:
            return [seen[complement], i]
        seen[num] = i
    return []

# Time: O(n)  |  Space: O(n)
# One pass — for each number, check if its complement is already recorded.""",
        "pattern_note": "Hash Map — store what you've seen for O(1) lookup. Classic O(n²) → O(n) trade-off.",
        "example_call": "print(two_sum([2, 7, 11, 15], 9))  # [0, 1]\nprint(two_sum([3, 2, 4], 6))     # [1, 2]",
    },
    {
        "id": "valid_anagram",
        "title": "Valid Anagram",
        "pattern": "hash_map",
        "difficulty": "easy",
        "prompt": """\
Given two strings s and t, return True if t is an anagram of s.

  Input:  s = "anagram", t = "nagaram"   → True
  Input:  s = "rat",     t = "car"       → False""",
        "hints": [
            "An anagram has the same characters in the same frequencies. How do you count frequencies?",
            "Counter(s) == Counter(t) is the one-liner. For the manual version: build a freq dict"
            " for s, then subtract for each char in t. If anything goes negative or is missing → False.",
        ],
        "solution": """\
from collections import Counter

def is_anagram(s, t):
    return Counter(s) == Counter(t)

# Manual version (good to know):
def is_anagram_manual(s, t):
    if len(s) != len(t):
        return False
    freq = {}
    for c in s:
        freq[c] = freq.get(c, 0) + 1
    for c in t:
        if c not in freq or freq[c] == 0:
            return False
        freq[c] -= 1
    return True

# Time: O(n)  |  Space: O(n)""",
        "pattern_note": "Counter is your friend for frequency problems. Know both the one-liner and the manual version.",
        "example_call": "print(is_anagram('anagram', 'nagaram'))  # True\nprint(is_anagram('rat', 'car'))        # False",
    },
    {
        "id": "group_anagrams",
        "title": "Group Anagrams",
        "pattern": "hash_map",
        "difficulty": "medium",
        "prompt": """\
Given a list of strings, group the anagrams together.

  Input:  ["eat","tea","tan","ate","nat","bat"]
  Output: [["bat"], ["nat","tan"], ["ate","eat","tea"]]
  (order within groups and between groups doesn't matter)""",
        "hints": [
            "You need a key that is the same for all anagrams. What's unique about a word's sorted characters?",
            "Use a defaultdict(list). For each word, the key is tuple(sorted(word))."
            " Append the word to the list at that key. Return the values.",
        ],
        "solution": """\
from collections import defaultdict

def group_anagrams(strs):
    groups = defaultdict(list)
    for word in strs:
        key = tuple(sorted(word))   # same key for all anagrams
        groups[key].append(word)
    return list(groups.values())

# Time: O(n * k log k) where k is max word length (sorting each word)
# Space: O(n * k)""",
        "pattern_note": "Canonical key pattern — transform each item into a normalized form that groups equivalents together.",
        "example_call": "print(group_anagrams(['eat','tea','tan','ate','nat','bat']))",
    },
    {
        "id": "top_k_frequent",
        "title": "Top K Frequent Elements",
        "pattern": "hash_map",
        "difficulty": "medium",
        "prompt": """\
Given an integer array and k, return the k most frequent elements.

  Input:  nums = [1, 1, 1, 2, 2, 3],  k = 2
  Output: [1, 2]

  Input:  nums = [1],  k = 1
  Output: [1]""",
        "hints": [
            "Step 1 is obvious: count frequencies with Counter. Step 2 is extracting the top-k.",
            "Counter.most_common(k) does it in one call. Alternatively: sort by frequency descending"
            " and slice. For O(n) you could use bucket sort — index = frequency, bucket = list of nums.",
        ],
        "solution": """\
from collections import Counter

def top_k_frequent(nums, k):
    return [num for num, _ in Counter(nums).most_common(k)]

# Manual sort version:
def top_k_frequent_v2(nums, k):
    count = Counter(nums)
    return sorted(count, key=count.get, reverse=True)[:k]

# Bucket sort version (O(n)):
def top_k_frequent_v3(nums, k):
    count = Counter(nums)
    buckets = [[] for _ in range(len(nums) + 1)]
    for num, freq in count.items():
        buckets[freq].append(num)
    result = []
    for freq in range(len(buckets) - 1, 0, -1):
        result.extend(buckets[freq])
        if len(result) >= k:
            return result[:k]

# Time: O(n log n) with sort  |  O(n) with bucket sort""",
        "pattern_note": "Counter + most_common is O(n log n). Know the bucket sort trick for O(n) if asked to optimize.",
        "example_call": "print(top_k_frequent([1, 1, 1, 2, 2, 3], 2))  # [1, 2]\nprint(top_k_frequent([1], 1))            # [1]",
    },

    # ─── TWO POINTERS ────────────────────────────────────────────────────────
    {
        "id": "valid_palindrome",
        "title": "Valid Palindrome",
        "pattern": "two_pointer",
        "difficulty": "easy",
        "prompt": """\
A phrase is a palindrome if it reads the same forward and backward, ignoring
case and non-alphanumeric characters.

  Input:  "A man, a plan, a canal: Panama"  → True
  Input:  "race a car"                       → False
  Input:  " "                                → True""",
        "hints": [
            "First clean the string (lowercase, alphanumeric only). Then check if it equals its reverse.",
            "Two-pointer version (in-place): left pointer at start, right at end."
            " Skip non-alphanumeric. Compare chars. Move inward.",
        ],
        "solution": """\
def is_palindrome(s):
    cleaned = [c.lower() for c in s if c.isalnum()]
    return cleaned == cleaned[::-1]

# Two-pointer version (O(1) extra space):
def is_palindrome_v2(s):
    left, right = 0, len(s) - 1
    while left < right:
        while left < right and not s[left].isalnum():
            left += 1
        while left < right and not s[right].isalnum():
            right -= 1
        if s[left].lower() != s[right].lower():
            return False
        left += 1
        right -= 1
    return True

# Time: O(n)  |  Space: O(n) cleaned / O(1) two-pointer""",
        "pattern_note": "Two pointers from both ends, moving inward — classic for palindrome, sorted pair problems.",
        "example_call": "print(is_palindrome('A man, a plan, a canal: Panama'))  # True\nprint(is_palindrome('race a car'))                       # False",
    },
    {
        "id": "container_with_most_water",
        "title": "Container With Most Water",
        "pattern": "two_pointer",
        "difficulty": "medium",
        "prompt": """\
Given an integer array height of length n, find two lines that together with
the x-axis form a container that holds the most water. Return the max area.

  Input:  height = [1,8,6,2,5,4,8,3,7]
  Output: 49   # lines at index 1 and 8, area = min(8,7) * (8-1) = 49""",
        "hints": [
            "Brute force: check every pair O(n²). Think about what determines area: min(left, right) * width.",
            "Start with widest container (left=0, right=end). The only reason to shrink width is if"
            " the shorter side might improve. Move the pointer at the shorter height inward.",
        ],
        "solution": """\
def max_area(height):
    left, right = 0, len(height) - 1
    best = 0
    while left < right:
        area = min(height[left], height[right]) * (right - left)
        best = max(best, area)
        if height[left] < height[right]:
            left += 1
        else:
            right -= 1
    return best

# Time: O(n)  |  Space: O(1)
# Key insight: always move the shorter-height pointer — the taller one
# can never help us if we shrink width, but the shorter one might.""",
        "pattern_note": "Greedy two-pointer: always eliminate the side that can't possibly improve the result.",
        "example_call": "print(max_area([1,8,6,2,5,4,8,3,7]))  # 49",
    },
    {
        "id": "three_sum",
        "title": "3Sum",
        "pattern": "two_pointer",
        "difficulty": "medium",
        "prompt": """\
Given an integer array, return all unique triplets [a, b, c] such that
a + b + c == 0. The solution set must not contain duplicate triplets.

  Input:  nums = [-1, 0, 1, 2, -1, -4]
  Output: [[-1, -1, 2], [-1, 0, 1]]""",
        "hints": [
            "Sort first. Then for each number at index i, run a two-pointer search on the rest.",
            "Fix nums[i] as the first element. Use left=i+1, right=end. If sum < 0, move left up."
            " If sum > 0, move right down. Skip duplicates to avoid repeats in output.",
        ],
        "solution": """\
def three_sum(nums):
    nums.sort()
    result = []
    for i in range(len(nums) - 2):
        if i > 0 and nums[i] == nums[i - 1]:   # skip duplicates
            continue
        left, right = i + 1, len(nums) - 1
        while left < right:
            total = nums[i] + nums[left] + nums[right]
            if total == 0:
                result.append([nums[i], nums[left], nums[right]])
                while left < right and nums[left] == nums[left + 1]:
                    left += 1
                while left < right and nums[right] == nums[right - 1]:
                    right -= 1
                left += 1
                right -= 1
            elif total < 0:
                left += 1
            else:
                right -= 1
    return result

# Time: O(n²)  |  Space: O(1) (ignoring output)
# Sort + fix one element + two-pointer on the rest.""",
        "pattern_note": "Sort first, then reduce to Two Sum with two pointers. Careful with duplicate skipping.",
        "example_call": "print(three_sum([-1, 0, 1, 2, -1, -4]))  # [[-1,-1,2],[-1,0,1]]",
    },

    # ─── SLIDING WINDOW ──────────────────────────────────────────────────────
    {
        "id": "best_time_to_buy_stock",
        "title": "Best Time to Buy and Sell Stock",
        "pattern": "sliding_window",
        "difficulty": "easy",
        "prompt": """\
Given prices[i] = price of a stock on day i, find the max profit from buying
on one day and selling on a later day. Return 0 if no profit is possible.

  Input:  prices = [7, 1, 5, 3, 6, 4]  → 5  (buy at 1, sell at 6)
  Input:  prices = [7, 6, 4, 3, 1]      → 0  (prices only fall)""",
        "hints": [
            "Track the minimum price seen so far as you scan left to right.",
            "For each day: profit = today's price - min_price_so_far. Update max_profit. Update min_price.",
        ],
        "solution": """\
def max_profit(prices):
    min_price = float('inf')
    max_profit = 0
    for price in prices:
        min_price = min(min_price, price)
        max_profit = max(max_profit, price - min_price)
    return max_profit

# Time: O(n)  |  Space: O(1)
# This is really a sliding window where left = cheapest buy, right = today.""",
        "pattern_note": "Sliding window: left tracks best buy, right scans forward. Classic single-pass greedy.",
        "example_call": "print(max_profit([7, 1, 5, 3, 6, 4]))  # 5\nprint(max_profit([7, 6, 4, 3, 1]))      # 0",
    },
    {
        "id": "longest_substring_no_repeat",
        "title": "Longest Substring Without Repeating Characters",
        "pattern": "sliding_window",
        "difficulty": "medium",
        "prompt": """\
Given a string s, find the length of the longest substring with no repeating chars.

  Input:  "abcabcbb"  → 3   ("abc")
  Input:  "bbbbb"     → 1   ("b")
  Input:  "pwwkew"    → 3   ("wke")""",
        "hints": [
            "Use a sliding window: expand right pointer, shrink left when you hit a duplicate.",
            "Keep a set of characters in the current window. When s[right] is already in the set,"
            " remove s[left] from the set and advance left. Track max window size.",
        ],
        "solution": """\
def length_of_longest_substring(s):
    seen = set()
    left = 0
    best = 0
    for right in range(len(s)):
        while s[right] in seen:
            seen.remove(s[left])
            left += 1
        seen.add(s[right])
        best = max(best, right - left + 1)
    return best

# Optimized (jump left pointer directly):
def length_of_longest_substring_v2(s):
    last_seen = {}   # char -> last index
    left = 0
    best = 0
    for right, char in enumerate(s):
        if char in last_seen and last_seen[char] >= left:
            left = last_seen[char] + 1
        last_seen[char] = right
        best = max(best, right - left + 1)
    return best

# Time: O(n)  |  Space: O(min(n, alphabet))""",
        "pattern_note": "Variable-size sliding window: expand right, shrink left to maintain the invariant (no repeats).",
        "example_call": "print(length_of_longest_substring('abcabcbb'))  # 3\nprint(length_of_longest_substring('bbbbb'))      # 1",
    },

    # ─── STACK ───────────────────────────────────────────────────────────────
    {
        "id": "valid_parentheses",
        "title": "Valid Parentheses",
        "pattern": "stack",
        "difficulty": "easy",
        "prompt": """\
Given a string of brackets, determine if it's valid. Valid means:
  - Open brackets are closed by the same type
  - Brackets are closed in the correct order

  Input:  "()"      → True
  Input:  "()[]{}"  → True
  Input:  "(]"      → False
  Input:  "([)]"    → False""",
        "hints": [
            "When you see an opening bracket, push it. When you see a closing bracket, what should be on top of the stack?",
            "Use a dict: closing -> expected_opening. For each char: if opening, push."
            " If closing, pop and check it matches. If stack is empty at close, invalid. At end, stack must be empty.",
        ],
        "solution": """\
def is_valid(s):
    stack = []
    matching = {')': '(', ']': '[', '}': '{'}
    for char in s:
        if char in '([{':
            stack.append(char)
        elif char in matching:
            if not stack or stack[-1] != matching[char]:
                return False
            stack.pop()
    return len(stack) == 0

# Time: O(n)  |  Space: O(n)""",
        "pattern_note": "Stack — use when you need to match/undo things in reverse order (LIFO). Brackets, undo history, call stacks.",
        "example_call": "print(is_valid('()[]{}'))  # True\nprint(is_valid('(]'))      # False",
    },
    {
        "id": "daily_temperatures",
        "title": "Daily Temperatures",
        "pattern": "stack",
        "difficulty": "medium",
        "prompt": """\
Given temperatures[], return answer[] where answer[i] = number of days until
a warmer temperature. If no warmer day exists, answer[i] = 0.

  Input:  [73, 74, 75, 71, 69, 72, 76, 73]
  Output: [ 1,  1,  4,  2,  1,  1,  0,  0]""",
        "hints": [
            "You need to find the next greater element for each position. Brute force is O(n²).",
            "Use a monotonic stack (decreasing). Push indices. When current temp > temp at stack top,"
            " that stack top has found its answer: today's index - popped index.",
        ],
        "solution": """\
def daily_temperatures(temps):
    result = [0] * len(temps)
    stack = []   # indices of days waiting for a warmer day
    for i, temp in enumerate(temps):
        while stack and temps[stack[-1]] < temp:
            j = stack.pop()
            result[j] = i - j
        stack.append(i)
    return result

# Time: O(n)  |  Space: O(n)
# Monotonic decreasing stack: each element pushed and popped at most once.""",
        "pattern_note": "Monotonic stack — when you need 'next greater/smaller element'. Stack stays sorted; violations trigger pops.",
        "example_call": "print(daily_temperatures([73,74,75,71,69,72,76,73]))  # [1,1,4,2,1,1,0,0]",
    },

    # ─── BINARY SEARCH ───────────────────────────────────────────────────────
    {
        "id": "binary_search",
        "title": "Binary Search",
        "pattern": "binary_search",
        "difficulty": "easy",
        "prompt": """\
Given a sorted array and a target, return the index of target or -1 if not found.

  Input:  nums = [-1, 0, 3, 5, 9, 12], target = 9  → 4
  Input:  nums = [-1, 0, 3, 5, 9, 12], target = 2  → -1""",
        "hints": [
            "Maintain left and right bounds. Mid = (left + right) // 2.",
            "If nums[mid] == target: found. If nums[mid] < target: move left up to mid+1."
            " If nums[mid] > target: move right down to mid-1. Stop when left > right.",
        ],
        "solution": """\
def binary_search(nums, target):
    left, right = 0, len(nums) - 1
    while left <= right:
        mid = (left + right) // 2
        if nums[mid] == target:
            return mid
        elif nums[mid] < target:
            left = mid + 1
        else:
            right = mid - 1
    return -1

# Time: O(log n)  |  Space: O(1)
# Invariant: target is always within [left, right] if it exists.""",
        "pattern_note": "Binary search template: while left <= right, mid = (l+r)//2. Memorize this — it's the base for many variants.",
        "example_call": "print(binary_search([-1, 0, 3, 5, 9, 12], 9))   # 4\nprint(binary_search([-1, 0, 3, 5, 9, 12], 2))   # -1",
    },
    {
        "id": "search_rotated_array",
        "title": "Search in Rotated Sorted Array",
        "pattern": "binary_search",
        "difficulty": "medium",
        "prompt": """\
A sorted array was rotated at some unknown pivot. Search for a target. Return
its index or -1. Must be O(log n).

  Input:  nums = [4, 5, 6, 7, 0, 1, 2], target = 0  → 4
  Input:  nums = [4, 5, 6, 7, 0, 1, 2], target = 3  → -1""",
        "hints": [
            "Standard binary search fails because the array isn't fully sorted. But one half is always sorted.",
            "At each mid: check which half is sorted (compare nums[left] with nums[mid])."
            " Determine if target falls in the sorted half. If yes, search there; otherwise search the other half.",
        ],
        "solution": """\
def search_rotated(nums, target):
    left, right = 0, len(nums) - 1
    while left <= right:
        mid = (left + right) // 2
        if nums[mid] == target:
            return mid
        # Left half is sorted
        if nums[left] <= nums[mid]:
            if nums[left] <= target < nums[mid]:
                right = mid - 1
            else:
                left = mid + 1
        # Right half is sorted
        else:
            if nums[mid] < target <= nums[right]:
                left = mid + 1
            else:
                right = mid - 1
    return -1

# Time: O(log n)  |  Space: O(1)
# Key: one half is ALWAYS sorted — use that to decide which side to eliminate.""",
        "pattern_note": "Modified binary search: determine which half is sorted, use that to decide where to search.",
        "example_call": "print(search_rotated([4,5,6,7,0,1,2], 0))  # 4\nprint(search_rotated([4,5,6,7,0,1,2], 3))  # -1",
    },

    # ─── BFS / DFS ───────────────────────────────────────────────────────────
    {
        "id": "number_of_islands",
        "title": "Number of Islands",
        "pattern": "bfs_dfs",
        "difficulty": "medium",
        "prompt": """\
Given an m x n grid of '1' (land) and '0' (water), count the number of islands.
An island is a group of '1's connected horizontally or vertically.

  Input:
    [["1","1","0","0","0"],
     ["1","1","0","0","0"],
     ["0","0","1","0","0"],
     ["0","0","0","1","1"]]
  Output: 3""",
        "hints": [
            "Iterate the grid. When you find a '1', it's the start of a new island. How do you mark it as visited?",
            "DFS from each unvisited '1': mark it as visited (e.g., flip to '0'), then recursively do the same"
            " for all 4 neighbors. Each DFS call = one island discovered. Count the calls.",
        ],
        "solution": """\
def num_islands(grid):
    if not grid:
        return 0
    count = 0
    rows, cols = len(grid), len(grid[0])

    def dfs(r, c):
        if r < 0 or r >= rows or c < 0 or c >= cols or grid[r][c] != '1':
            return
        grid[r][c] = '0'   # mark visited
        dfs(r+1, c); dfs(r-1, c); dfs(r, c+1); dfs(r, c-1)

    for r in range(rows):
        for c in range(cols):
            if grid[r][c] == '1':
                count += 1
                dfs(r, c)
    return count

# Time: O(m*n)  |  Space: O(m*n) recursion stack
# Note: modifies input grid. If you can't modify it, use a visited set instead.""",
        "pattern_note": "DFS flood fill — visit and mark. Same pattern for: connected components, flood fill, number of provinces.",
        "example_call": 'grid = [["1","1","0"],["1","1","0"],["0","0","1"]]\nprint(num_islands(grid))  # 2',
    },
    {
        "id": "climbing_stairs",
        "title": "Climbing Stairs",
        "pattern": "bfs_dfs",
        "difficulty": "easy",
        "prompt": """\
You can climb 1 or 2 steps at a time. How many distinct ways can you climb n stairs?

  Input: n = 2  → 2   (1+1 or 2)
  Input: n = 3  → 3   (1+1+1, 1+2, 2+1)
  Input: n = 5  → 8""",
        "hints": [
            "At each step, you came from either step n-1 or step n-2. So ways(n) = ways(n-1) + ways(n-2).",
            "It's Fibonacci. Base cases: ways(1)=1, ways(2)=2. Build up from there with two variables — no array needed.",
        ],
        "solution": """\
def climb_stairs(n):
    if n <= 2:
        return n
    prev2, prev1 = 1, 2
    for _ in range(3, n + 1):
        prev2, prev1 = prev1, prev1 + prev2
    return prev1

# Time: O(n)  |  Space: O(1)
# This is your intro to dynamic programming: overlapping subproblems, optimal substructure.
# Memoized recursive version:
from functools import lru_cache

def climb_stairs_recursive(n):
    @lru_cache(None)
    def dp(i):
        if i <= 2:
            return i
        return dp(i-1) + dp(i-2)
    return dp(n)""",
        "pattern_note": "Intro DP — recognize the recurrence relation. Fibonacci-style: current state depends on last two states.",
        "example_call": "print(climb_stairs(2))  # 2\nprint(climb_stairs(3))  # 3\nprint(climb_stairs(5))  # 8",
    },
]

PATTERN_GROUPS = {}
for q in QUESTIONS:
    PATTERN_GROUPS.setdefault(q["pattern"], []).append(q)


def get_by_id(question_id: str) -> dict | None:
    return next((q for q in QUESTIONS if q["id"] == question_id), None)


def get_by_pattern(pattern: str) -> list[dict]:
    return PATTERN_GROUPS.get(pattern, [])


def get_all_ids() -> list[str]:
    return [q["id"] for q in QUESTIONS]
