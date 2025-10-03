import pytest


@pytest.fixture(autouse=True)
def _xunit_setUp_tearDown(request):
    """
    Bridge unittest-style setUp/tearDown for pytest-collected test classes.
    If the test instance defines setUp/tearDown, call them around each test.
    """
    instance = getattr(request.node, "instance", None)
    if instance is not None:
        setup = getattr(instance, "setUp", None)
        if callable(setup):
            setup()
    try:
        yield
    finally:
        if instance is not None:
            teardown = getattr(instance, "tearDown", None)
            if callable(teardown):
                teardown()
