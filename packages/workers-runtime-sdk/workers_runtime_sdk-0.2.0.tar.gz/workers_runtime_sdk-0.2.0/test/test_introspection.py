import pytest
import sys
from unittest.mock import MagicMock


@pytest.fixture
def pyodide_imports(monkeypatch):
    monkeypatch.setitem(sys.modules, "js", MagicMock())
    monkeypatch.setitem(sys.modules, "_pyodide_entrypoint_helper", MagicMock())
    monkeypatch.setitem(sys.modules, "pyodide", MagicMock(__version__=2))
    monkeypatch.setitem(sys.modules, "pyodide.code", MagicMock())
    monkeypatch.setitem(sys.modules, "pyodide.http", MagicMock())
    monkeypatch.setitem(sys.modules, "pyodide.ffi", MagicMock())


def test_collect_methods(pyodide_imports):
    from introspection import collect_methods

    class A:
        x = 2

        @staticmethod
        def f():
            pass

        @classmethod
        def g(cls):
            pass

        @property
        def y(self):
            return 7

        async def fetch(request):
            pass

    assert collect_methods(A) == ["fetch"]

    class B(A):
        def some_method(self):
            pass

    assert collect_methods(B) == ["fetch", "some_method"]

    from workers import WorkerEntrypoint

    class C(WorkerEntrypoint, B):
        def third_method(self):
            pass

    assert collect_methods(C) == ["fetch", "some_method", "third_method"]

    class D(B, WorkerEntrypoint):
        def third_method(self):
            pass

    assert collect_methods(C) == ["fetch", "some_method", "third_method"]
