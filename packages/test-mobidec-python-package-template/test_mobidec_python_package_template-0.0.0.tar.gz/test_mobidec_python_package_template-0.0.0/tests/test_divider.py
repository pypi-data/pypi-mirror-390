import pytest
from test_mobidec_python_package_template.divider import CantDivideByZeroError, divide


def test_devide_by_zero():
    with pytest.raises(CantDivideByZeroError):
        divide(1, 0)


def test_devide_by_one():
    assert divide(1, 1) == 1
