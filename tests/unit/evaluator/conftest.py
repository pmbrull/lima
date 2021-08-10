import pytest

from lima.evaluator import Evaluator


@pytest.fixture
def evaluator():

    evaluator = Evaluator(_globals={}, _locals={})

    return evaluator
