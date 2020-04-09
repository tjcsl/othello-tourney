import importlib.util
import importlib.machinery


def import_strategy(path):
    return importlib.machinery.SourceFileLoader("strategy", path, ).load_module().Strategy().best_strategy
