import pytest


@pytest.mark.usefixtures("evaluator")
class TestPyEvaluator:
    def test_eval_ok(self, evaluator):
        """
        We can execute valid python code
        """

        statement = "1 + 1"
        res = evaluator.py_eval(statement)

        assert res == 2

    def test_eval_exc(self, evaluator):
        """
        We raise exceptions properly
        """

        statement = "a = random"

        with pytest.raises(NameError):
            evaluator.py_eval(statement)

    def test_eval_expr(self, evaluator):
        """
        Expressions return None
        """

        statement = "def random():\n    print('random')"
        res = evaluator.py_eval(statement)

        assert res is None

    def test_eval_assignment(self, evaluator):
        """
        We handle assignments correctly
        """

        statement = "a = 1"
        res = evaluator.py_eval(statement)

        assert res is None
        assert evaluator._locals.get("a") is not None
