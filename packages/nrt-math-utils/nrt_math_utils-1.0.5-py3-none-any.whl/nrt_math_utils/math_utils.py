from typing import Optional

from math import floor
from numbers import Number

from nrt_collections_utils.collections_utils import CollectionsUtil
from nrt_math_utils.nrt_numbers import DecimalNumber


class MathUtil:

    @classmethod
    def average(cls, numbers: list, weights: Optional[list]) -> DecimalNumber:
        cls.__verify_all_list_are_numbers(numbers)

        if weights is not None:
            cls.__verify_all_list_are_numbers(weights)
        else:
            weights = [1] * len(numbers)

        if len(numbers) != len(weights):
            raise ValueError(
                f'Numbers list length {len(numbers)}'
                f' ,is different from weights list length {len(weights)}')

        numbers_weighted = DecimalNumber(0)

        for i, number in enumerate(numbers):
            numbers_weighted += number * weights[i]

        return numbers_weighted / DecimalNumber(sum(weights))

    @staticmethod
    def floor(number, digits: int):
        denominator = 10 ** digits
        return type(number)(floor(number * denominator) / denominator)

    @staticmethod
    def is_all_numbers(elements: list) -> bool:
        return \
            all(isinstance(item, (Number, DecimalNumber)) and not isinstance(item, bool)
                for item in elements)

    @staticmethod
    def max(*elements):
        num_list = [
            num for num in CollectionsUtil.deep_args_to_list(elements)
            if num is not None
        ]

        return max(num_list) if num_list else None

    @staticmethod
    def min(*elements):
        num_list = [
            num for num in CollectionsUtil.deep_args_to_list(elements)
            if num is not None
        ]

        return min(num_list) if num_list else None

    @staticmethod
    def sum_0_to_n(n: int) -> int:
        return n * (n + 1) // 2

    @classmethod
    def __verify_all_list_are_numbers(cls, elements: list):
        if not cls.is_all_numbers(elements):
            raise ValueError(f'Not all numbers in list [{elements}] are numbers.')
