from typing import List, Tuple


def get_test_case_descriptions(test_cases: List[Tuple]):
    return [
        f'test #{index+1}: {test_case[0]}'
        for index, test_case in enumerate(test_cases)
    ]
