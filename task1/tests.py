import unittest
from solution import sum_two, strict


def idk(a: list) -> None:
    return None


class TestWrapStrict(unittest.TestCase):
    def test_sum(self):
        self.assertEqual(sum_two(2, 4), 6)

    def test_sum_raise_1(self):
        with self.assertRaises(TypeError):
            sum_two(1, 2.2)

    def test_sum_raise_2(self):
        with self.assertRaises(TypeError):
            sum_two(1.1, 1)

    def test_sum_raise_3(self):
        with self.assertRaises(TypeError):
            sum_two(2, a='1')

    def test_idk_func(self):
        self.assertEqual(strict(idk)(['123']), None)

    def test_idk_func_raise_1(self):
        with self.assertRaises(TypeError):
            strict(idk)('123')

    def test_idk_func_raise_2(self):
        with self.assertRaises(TypeError):
            strict(idk)((1,))
