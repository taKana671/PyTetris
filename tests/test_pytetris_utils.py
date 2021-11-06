import os
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

import copy
from unittest import TestCase, main

import numpy as np

from pytetris_utils import update_blockset_row, update_blockset_col


class PytetrisUtilsTestCase(TestCase):
    """Test extension module pytetris_utils
    """

    def setUp(self):
        test_array_1 = np.array([
            [[-1, 4], [0, 4], [1, 4], [2, 4]],
            [[-1, 4], [-1, 5], [-1, 6], [-1, 7]],
            [[-1, 4], [0, 4], [1, 4], [2, 4]],
            [[-1, 4], [-1, 5], [-1, 6], [-1, 7]]])
        test_array_2 = np.array([
            [[-1, 3], [0, 3], [0, 4], [0, 5]],
            [[-1, 4], [0, 4], [1, 4], [1, 3]],
            [[-1, 3], [-1, 4], [-1, 5], [0, 5]],
            [[-1, 4], [-1, 5], [0, 4], [1, 4]]])
        test_array_3 = np.array([
            [[-1, 4], [-1, 5], [0, 3], [0, 4]],
            [[-1, 3], [0, 3], [0, 4], [1, 4]],
            [[-1, 4], [-1, 5], [0, 3], [0, 4]],
            [[-1, 3], [0, 3], [0, 4], [1, 4]]])
        self.tests = [test_array_1, test_array_2, test_array_3]
        self.steps = [1, 2, -1]

    def test_updcate_blockset_row(self):
        for test, step in zip(self.tests, self.steps):
            before = copy.deepcopy(test)
            update_blockset_row(test, step)
            for before_row, after_row in zip(before, test):
                for before_item, after_item in zip(before_row, after_row):
                    with self.subTest(step):
                        self.assertEqual(before_item[0], after_item[0] - step)

    def test_update_blockset_col(self):
        for test, step in zip(self.tests, self.steps):
            before = copy.deepcopy(test)
            update_blockset_col(test, step)
            for before_row, after_row in zip(before, test):
                for before_item, after_item in zip(before_row, after_row):
                    with self.subTest(step):
                        self.assertEqual(before_item[1], after_item[1] - step)


if __name__ == '__main__':
    main()
