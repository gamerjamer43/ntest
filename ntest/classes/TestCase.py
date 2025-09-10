from abc import ABC, abstractmethod
from typing import Self, Any, Callable

from logging.handlers import BufferingHandler
from logging import getLogger

from warnings import catch_warnings, simplefilter

class TestCase(ABC):
    """Test case class for you to subclass in your tests.
    Methods:
    - setUpClass(cls): Optional class method to set up anything you need before running tests.
    - tearDownClass(cls): OOptional class method to clean up anything you need after running tests.
    - setUp(self): Optional method to set up resources before each test function.
    - tearDown(self): Optional method to clean up resources after each test function.

    - assertEqual(a, b, msg=None): Assert that a == b.
    - assertNotEqual(a, b, msg=None): Assert that a != b.
    - assertTrue(expr, msg=None): Assert that expr is True.
    - assertFalse(expr, msg=None): Assert that expr is False.
    - assertIsNone(obj, msg=None): Assert that obj is None.
    - assertIsNotNone(obj, msg=None): Assert that obj is not None.
    - assertIn(member, container, msg=None): Assert that member is in container.
    - assertNotIn(member, container, msg=None): Assert that member is not in container.
    - assertRaises(exc, func, *args, **kwargs): Assert that func(*args, **kwargs) raises exc.
    - assertWarns(warn, func, *args, **kwargs): Assert that func(*args, **kwargs) raises warn.
    - assertLogs(logger_name, level, func, *args, **kwargs): Assert that func(*args, **kwargs) logs at level or higher.
    
    Subclasses have to implement the run() method themselves."""

    # setup and teardown methods
    @classmethod
    def setUpClass(cls) -> None:
        pass
    
    @classmethod
    def tearDownClass(cls) -> None:
        pass

    def setUp(self: Self) -> None:
        pass

    def tearDown(self: Self) -> None:
        pass

    # before and after
    def beforeAll(self: Self) -> None:
        pass

    def afterAll(self: Self) -> None:
        pass

    # built-in assert functions
    def assertEqual(self: Self, a: Any, b: Any, msg: str | None = None) -> None:
        if a != b:
            raise AssertionError(msg or f"{a!r} != {b!r}")

    def assertNotEqual(self: Self, a: Any, b: Any, msg: str | None = None) -> None:
        if a == b:
            raise AssertionError(msg or f"{a!r} == {b!r}")

    def assertTrue(self: Self, expr: Any, msg: str | None = None) -> None:
        if not expr:
            raise AssertionError(msg or f"{expr!r} is not True")

    def assertFalse(self: Self, expr: Any, msg: str | None = None) -> None:
        if expr:
            raise AssertionError(msg or f"{expr!r} is not False")

    def assertIsNone(self: Self, obj: Any, msg: str | None = None) -> None:
        if obj is not None:
            raise AssertionError(msg or f"{obj!r} is not None")

    def assertIsNotNone(self: Self, obj: Any, msg: str | None = None) -> None:
        if obj is None:
            raise AssertionError(msg or "Unexpected None")

    def assertIn(self: Self, member: Any, container: Any, msg: str | None = None) -> None:
        if member not in container:
            raise AssertionError(msg or f"{member!r} not found in {container!r}")

    def assertNotIn(self: Self, member: Any, container: Any, msg: str | None = None) -> None:
        if member in container:
            raise AssertionError(msg or f"{member!r} unexpectedly found in {container!r}")

    # control flow assertions
    def assertRaises(self: Self, exc: type[BaseException], func: Callable[..., Any], *args: Any, **kwargs: Any) -> None:
        try:
            func(*args, **kwargs)
        except Exception as e:
            if not isinstance(e, exc):
                raise AssertionError(f"Expected {exc}, got {type(e)}")
        else:
            raise AssertionError(f"{exc} was not raised")

    def assertWarns(self: Self, expected_warning: type[BaseException], func: Callable[..., Any], *args: Any, **kwargs: Any) -> None:
        with catch_warnings(record=True) as ws:
            simplefilter("always")
            func(*args, **kwargs)
            if not any(isinstance(w.message, expected_warning) for w in ws):
                raise AssertionError(f"Expected warning {expected_warning}")

    # logging
    def assertLogs(self: Self, logger_name: str, level: int, func: Callable[..., Any], *args: Any, **kwargs: Any) -> None:
        # initalize logger (set max buffer of 100 records)
        logger = getLogger(logger_name)
        handler = BufferingHandler(100)
        logger.addHandler(handler)
        logger.setLevel(level)

        func(*args, **kwargs)
        logger.removeHandler(handler)
        records = [r for r in handler.buffer if r.levelno >= level]
        if not records:
            raise AssertionError(f"No logs with level >= {level}")

    @abstractmethod
    def run(self: Self) -> None:
        """What actually makes your test class run. Put here what you want to happen when it's called."""
        ...