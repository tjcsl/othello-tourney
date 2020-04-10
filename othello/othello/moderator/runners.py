from .utils import import_strategy


class LocalRunner:
    def __init__(self, script_path, logging):
        self.path = script_path
        self.logging = logging
        self.strat = import_strategy(script_path)
