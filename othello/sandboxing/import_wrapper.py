import importlib.machinery
import json
import sys
from inspect import signature


def import_strategy(path: str):
    strat = importlib.machinery.SourceFileLoader("strategy", path).load_module().Strategy()
    assert len(signature(strat.best_strategy).parameters) in (4, 5)
    return strat


def main() -> None:
    try:
        import_strategy(sys.argv[-1])
    except SyntaxError:
        sys.exit(json.dumps({"message": "File has invalid syntax"}))
    except AttributeError:
        sys.exit(json.dumps({"message": "Cannot find attribute Strategy.best_strategy in file"}))
    except AssertionError:
        sys.exit(
            json.dumps(
                {"message": "Attribute Strategy.best_strategy has an invalid amount of parameters"}
            )
        )
    except Exception:
        sys.stderr.write(
            json.dumps(
                {
                    "message": "Script is unable to be run, make sure your script runs on your computer before submitting"
                }
            )
        )
        sys.exit(1)
    sys.exit(0)


if __name__ == "__main__":
    main()
