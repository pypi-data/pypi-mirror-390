##############################################################################################################
# %%          Add `<root>/src` to sys.path
##############################################################################################################

import sys
from pathlib import Path

path = Path(__file__).parent
sys.path.insert(0, str((path).resolve()))
sys.path.insert(0, str((path / "../../src").resolve()))


from clig import Arg, data, run


def test_action_append():
    def main(foo: Arg[list[int], data(action="append")] = [0]):
        return locals()

    assert run(main, "--foo 1 --foo 2".split()) == {"foo": [0, 1, 2]}

    def bar(foo: Arg[list[str], data(action="append")] = ["0"]):
        return locals()

    assert run(bar, "--foo 1 --foo 2".split()) == {"foo": ["0", "1", "2"]}


def test_action_append_const():
    def main(foo: Arg[list[int], data(action="append_const", const=42)] = [0]):
        return locals()

    assert run(main, "--foo --foo --foo --foo".split()) == {"foo": [0, 42, 42, 42, 42]}

    def bar(foo: Arg[list[str], data(action="append_const", const="10")] = ["0"]):
        return locals()

    assert run(bar, "--foo --foo".split()) == {"foo": ["0", "10", "10"]}


def test_action_extend():
    def main(foo: Arg[list[int], data(action="extend")] = [0]):
        return locals()

    assert run(main, "--foo 42 --foo 52 62".split()) == {"foo": [0, 42, 52, 62]}
