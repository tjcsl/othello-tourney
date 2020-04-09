import importlib.util
import importlib.machinery

from inspect import signature


def import_strategy(path):
    strat = importlib.machinery.SourceFileLoader("strategy", path).load_module().Strategy()
    assert len(signature(strat.best_strategy).parameters) == 4
    return strat
