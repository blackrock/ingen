import logging
from contextlib import contextmanager
from typing import Any, Iterable, Optional, Type

import pytest


class _LogCapture:
    def __init__(self, level: int = logging.WARNING, logger: Optional[logging.Logger] = None) -> None:
        self.level = level
        self.logger = logger or logging.getLogger()
        self._handler: Optional[logging.Handler] = None
        self.records: list[logging.LogRecord] = []

    def __enter__(self) -> "_LogCapture":
        class _Handler(logging.Handler):
            def __init__(self, records: list[logging.LogRecord]):
                super().__init__()
                self._records = records

            def emit(self, record: logging.LogRecord) -> None:
                self._records.append(record)

        self._handler = _Handler(self.records)
        self._handler.setLevel(self.level)
        self._old_level = self.logger.level
        self.logger.setLevel(min(self.level, self._old_level) if self._old_level else self.level)
        self.logger.addHandler(self._handler)
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        if self._handler is not None:
            self.logger.removeHandler(self._handler)
        # restore previous level
        try:
            self.logger.setLevel(self._old_level)
        except Exception:
            pass


class TestCase:
    """
    Lightweight shim exposing common unittest.TestCase assertion APIs using pytest assertions.
    Only methods referenced in this repository's tests are implemented.
    """

    # basic truthiness
    def assertTrue(self, expr: Any, msg: str | None = None) -> None:
        assert expr, msg or "Expected expression to be truthy"

    def assertFalse(self, expr: Any, msg: str | None = None) -> None:
        assert not expr, msg or "Expected expression to be falsy"

    # equality and identity
    def assertEqual(self, first: Any, second: Any, msg: str | None = None) -> None:
        assert first == second, msg or f"Expected {first!r} == {second!r}"

    def assertNotEqual(self, first: Any, second: Any, msg: str | None = None) -> None:
        assert first != second, msg or f"Expected {first!r} != {second!r}"

    def assertIs(self, first: Any, second: Any, msg: str | None = None) -> None:
        assert first is second, msg or f"Expected {first!r} is {second!r}"

    def assertIsNone(self, expr: Any, msg: str | None = None) -> None:
        assert expr is None, msg or f"Expected None, got {expr!r}"

    def assertIsNotNone(self, expr: Any, msg: str | None = None) -> None:
        assert expr is not None, msg or "Expected value to be not None"

    def assertIsInstance(self, obj: Any, cls: Type[Any], msg: str | None = None) -> None:
        assert isinstance(obj, cls), msg or f"Expected {obj!r} to be instance of {cls}"

    # containers
    def assertIn(self, member: Any, container: Iterable[Any], msg: str | None = None) -> None:
        assert member in container, msg or f"Expected {member!r} to be in {container!r}"

    def assertNotIn(self, member: Any, container: Iterable[Any], msg: str | None = None) -> None:
        assert member not in container, msg or f"Expected {member!r} to not be in {container!r}"

    def assertDictEqual(self, d1: dict, d2: dict, msg: str | None = None) -> None:
        assert d1 == d2, msg or f"Expected dicts to be equal: {d1!r} != {d2!r}"

    def assertListEqual(self, l1: list, l2: list, msg: str | None = None) -> None:
        assert l1 == l2, msg or f"Expected lists to be equal: {l1!r} != {l2!r}"

    # numeric comparisons
    def assertLess(self, a: Any, b: Any, msg: str | None = None) -> None:
        assert a < b, msg or f"Expected {a!r} < {b!r}"

    # lifecycle hooks to keep compatibility; pytest will just call test methods
    def setUp(self, *args: Any, **kwargs: Any) -> None:  # noqa: N802 (unittest-style name)
        pass

    def tearDown(self) -> None:  # noqa: N802
        pass

    # context managers
    def assertRaises(
        self,
        expected_exception: Type[BaseException],
        func: Optional[callable] = None,
        *args: Any,
        **kwargs: Any,
    ):
        """
        Supports both forms:
        - with self.assertRaises(Error): ...
        - self.assertRaises(Error, func, *args, **kwargs)
        """
        if func is not None:
            with pytest.raises(expected_exception):
                func(*args, **kwargs)
            return None
        return pytest.raises(expected_exception)

    def assertRaisesRegex(
        self,
        expected_exception: Type[BaseException],
        match: str,
        func: Optional[callable] = None,
        *args: Any,
        **kwargs: Any,
    ):
        if func is not None:
            with pytest.raises(expected_exception, match=match):
                func(*args, **kwargs)
            return None
        return pytest.raises(expected_exception, match=match)

    @contextmanager
    def assertLogs(self, level: str | int = "WARNING"):
        levelno = logging.getLevelName(level) if isinstance(level, str) else level
        capture = _LogCapture(level=levelno)
        with capture:
            yield capture


