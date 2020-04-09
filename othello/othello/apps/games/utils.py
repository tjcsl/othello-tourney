import importlib.util
import importlib.machinery

from inspect import signature


def import_strategy(path):
    assert len(signature(func := importlib.machinery.SourceFileLoader("strategy", path, ).load_module().Strategy().best_strategy).parameters) == 4
    return func
