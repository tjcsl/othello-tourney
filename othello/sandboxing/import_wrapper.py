import importlib.machinery
import json
import sys
from inspect import signature


def import_strategy(path):
    strat = importlib.machinery.SourceFileLoader("strategy", path).load_module().Strategy()
    assert len(signature(strat.best_strategy).parameters) == 4
    return strat


def main():
    try:
        import_strategy(sys.argv[-1])
    except SyntaxError:
        sys.stderr.write(json.dumps({"message": "File has invalid syntax"}))
        sys.exit(1)
    except AttributeError:
        sys.stderr.write(
            json.dumps({"message": "Cannot find attribute Strategy.best_strategy in file"})
        )
        sys.exit(1)
    except AssertionError:
        sys.stderr.write(
            json.dumps(
                {"message": "Attribute Strategy.best_strategy has an invalid amount of parameters"}
            )
        )
        sys.exit(1)
    except Exception as e:
        sys.stderr.write(json.dumps({"message": f"Script is unable to be run, {str(e)}"}))
    sys.exit(0)


if __name__ == "__main__":
    main()
