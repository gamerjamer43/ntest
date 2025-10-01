from ntest import TestCase
from itertools import permutations

def next_permutation(arr: list[int]) -> None:
    # find the pivot
    n: int = len(arr)

    # point to the second last element
    i: int = n - 2

    # find the first decreasing element
    while i >= 0 and arr[i] >= arr[i + 1]:
        # move pointer to the left
        i -= 1

    if i >= 0:
        # get last index
        j: int = n - 1

        # find the first element that is greater than the pivot
        while arr[j] <= arr[i]:
            j -= 1

        # execute the swap
        arr[i], arr[j] = arr[j], arr[i]

    # reverse the pointers from i+1 to end
    left, right = i + 1, n - 1

    # reverse elements from left to right
    while left < right:
        # execute another swap
        arr[left], arr[right] = arr[right], arr[left]

        # advance pointers
        left += 1
        right -= 1

class TestNextPermutation(TestCase):
    def test_sorted_list(self):
        arr = [1, 2, 3]
        next_permutation(arr)
        self.assertEqual(arr, [1, 3, 2])

    def test_all_descending(self):
        arr = [3, 2, 1]
        next_permutation(arr)
        self.assertEqual(arr, [1, 2, 3])

    def test_with_duplicates(self):
        arr = [1, 1, 5]
        next_permutation(arr)
        self.assertEqual(arr, [1, 5, 1])

    def test_single_element(self):
        arr = [42]
        next_permutation(arr)
        self.assertEqual(arr, [42])

    def test_middle_case(self):
        arr = [2, 3, 1]
        next_permutation(arr)
        self.assertEqual(arr, [3, 1, 2])

    def run(self):
        self.assertTrue(True)

def main() -> None:
    test: list[int] = [1,2,3]
    print(test)
    next_permutation(test)

if __name__ == "__main__":
    main()