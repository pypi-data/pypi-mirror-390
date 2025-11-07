import pytest

from nifti2bids._decorators import check_all_none


def test_check_all_none():
    """Test ``check_all_none`` decorator"""

    def mock_func(a=None, b=None):
        return a

    with pytest.raises(NameError):
        check_all_none(parameter_names=["a", "c"])(mock_func)

    with pytest.raises(ValueError):
        check_all_none(parameter_names=["a", "b"])(mock_func)(None, None)

    # Should capture positional and keyword args
    assert check_all_none(parameter_names=["a", "b"])(mock_func)(True, b=None)
