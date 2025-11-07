"""Decorator functions."""

import functools, inspect

from typing import Any, Callable

from ._helpers import list_to_str


def check_all_none(parameter_names: list[str]) -> Callable:
    """
    Checks if specific parameters are assigned ``None``.

    Parameters
    ----------
    parameter_names: :obj:`list[str]`
        List of parameter names to check.

    Returns
    -------
    Callable
        Decorator function wrapping target function.
    """

    def decorator(func: Callable) -> Callable:
        signature = inspect.signature(func)
        if invalid_params := [
            param
            for param in parameter_names
            if param not in signature.parameters.keys()
        ]:
            raise NameError(
                "Error in ``parameter_names`` of decorator. The following "
                f"parameters are not in the signature of '{func.__name__}': "
                f"{list_to_str(invalid_params)}."
            )

        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Callable:
            bound_args = signature.bind(*args, **kwargs)
            bound_args.apply_defaults()
            all_param_values = [bound_args.arguments[name] for name in parameter_names]
            if all(value is None for value in all_param_values):
                raise ValueError(
                    "All of the following arguments cannot be None, "
                    f"one must be specified: {list_to_str(parameter_names)}."
                )

            return func(*args, **kwargs)

        return wrapper

    return decorator
