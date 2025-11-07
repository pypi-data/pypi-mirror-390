import functools
import inspect
import os
from typing import Any
import warnings


class TestModeMixin:
    """
    Mixin for switching between production and test implementations of methods
    depending on the `IS_TEST_MODE` environment variable.

    Example:
    ----------

    >>> class MyClass(TestModeMixin):
    >>>     dict_tst_mode = {"base_method": "tst_base_method"}
    >>>
    >>>     def base_method(self):
    >>>         print("PROD")
    >>>
    >>>     def tst_base_method(self):
    >>>         print("TEST")
    >>>
    >>> MyClass().base_method() # PROD
    >>> os.environ["IS_TEST_MODE"] = "1"
    >>> MyClass().base_method()  # TEST
    """

    _dict_tst_mode: dict[str, str] = {}

    @property
    def dict_tst_mode(self) -> dict[str, str]:  # pragma: no cover
        """Return mapping of base methods to their test equivalents."""

        return self._dict_tst_mode

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        """
        Initialize mixin and patch test methods if test mode is enabled.

        Environment variables:
        - IS_TEST_MODE=1 → activates test mode
        - IS_RAISE_TEST_MODE=1 → raises exceptions instead of warnings
        """
        self._is_raise_test: int = int(os.environ.get("IS_RAISE_TEST_MODE", "0")) == 1
        super().__init__(*args, **kwargs)  # type: ignore
        self._patch_test_methods()

    def __handle_error(self, msg: str, error: type[Exception]) -> None:
        """
        Handle error when test substitution fails.

        If IS_RAISE_TEST_MODE=1 → raises an exception.
        Otherwise → emits a warning.
        """
        warnings.warn(msg, stacklevel=2)
        if self._is_raise_test:
            raise error(msg)

    def _patch_test_methods(self) -> None:
        """
        Replace production methods with test ones if IS_TEST_MODE=1.

        For every pair in dict_tst_mode:
        - Verify both methods exist and are callable.
        - Ensure both are of the same type (sync/async).
        - Dynamically replace the base method with its test equivalent.
        """
        is_test_mode = int(os.environ.get("IS_TEST_MODE", "0")) == 1
        if not is_test_mode:
            return

        for base_name, test_name in self.dict_tst_mode.items():
            base_func = getattr(self, base_name, None)
            test_func = getattr(self, test_name, None)

            if not callable(base_func):
                self.__handle_error(
                    f"[TestModeMixin]  not found base method'{base_name}' not found",
                    error=KeyError,
                )
                continue
            if not callable(test_func):
                self.__handle_error(
                    f"[TestModeMixin]  not found test method'{test_name}'",
                    error=KeyError,
                )
                continue

            if inspect.iscoroutinefunction(base_func) != inspect.iscoroutinefunction(
                test_func
            ):
                self.__handle_error(
                    f"[TestModeMixin] Not matched sync / async for methods `{test_name}` and `{base_name}`",
                    error=ValueError,
                )
                continue

            # setattr(self, base_name, functools.partial(test_func))
            # Correctly bind method to the instance (preserve `self`)
            bound_func = test_func.__get__(self, self.__class__)
            setattr(self, base_name, bound_func)
