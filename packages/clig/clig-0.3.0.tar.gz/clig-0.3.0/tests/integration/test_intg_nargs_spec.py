import sys
from pathlib import Path

path = Path(__file__).parent
sys.path.insert(0, str((path).resolve()))
sys.path.insert(0, str((path / "../../src").resolve()))

from argparse import ArgumentParser
from clig import Command, Arg, data
from clig import clig


def test_nargs_questionMark_nonDefault():
    """Ref: https://docs.python.org/3/library/argparse.html#nargs"""

    # original behavior

    parser = ArgumentParser("foo")
    parser.add_argument(dest="name")
    parser.add_argument(dest="size", nargs="?", type=int)

    args = parser.parse_args(["rocky", "123"])  # positional passed
    assert {"name": args.name, "size": args.size} == {"name": "rocky", "size": 123}

    args = parser.parse_args(["rocky"])  # not passed, produce default = None
    assert {"name": args.name, "size": args.size} == {"name": "rocky", "size": None}

    # test of lib

    def foo(name: str, size: Arg[float, data(nargs="?")]):
        return locals()

    assert clig.run(foo, ["rocky", "123"]) == {"name": "rocky", "size": 123}  # positional passed
    assert clig.run(foo, ["rocky"]) == {"name": "rocky", "size": None}  # not passed, produce default = None

    def bar(name: str, size: Arg[float, data(nargs="?", default=666)]):
        return locals()

    assert clig.run(bar, ["rocky", "123"]) == {"name": "rocky", "size": 123}  # positional passed
    assert clig.run(bar, ["rocky"]) == {"name": "rocky", "size": 666}  # not passed, produce default


def test_nargs_questionMark_default():
    """Ref: https://docs.python.org/3/library/argparse.html#nargs"""

    # original behavior

    parser = ArgumentParser("foo")
    parser.add_argument(dest="name")
    parser.add_argument("--size", dest="size", const=456, default=789, nargs="?", type=int)

    args = parser.parse_args(["rocky", "--size", "123"])  # optional passed
    assert {"name": args.name, "size": args.size} == {"name": "rocky", "size": 123}

    args = parser.parse_args(["rocky", "--size"])  # no value, produce const
    assert {"name": args.name, "size": args.size} == {"name": "rocky", "size": 456}

    args = parser.parse_args(["rocky"])  # not passed, produce default
    assert {"name": args.name, "size": args.size} == {"name": "rocky", "size": 789}

    # test of lib

    def bar(name: str, size: Arg[float, data(nargs="?", const=456)] = 789):
        return locals()

    assert clig.run(bar, ["rocky", "--size", "123"]) == {"name": "rocky", "size": 123}  # optional passed
    assert clig.run(bar, ["rocky", "--size"]) == {"name": "rocky", "size": 456}  # no value, produce const
    assert clig.run(bar, ["rocky"]) == {"name": "rocky", "size": 789}  # not passed, produce default


def test_nargs_starMark_nonDefault():
    """Ref: https://docs.python.org/3/library/argparse.html#nargs"""

    # original behavior

    parser = ArgumentParser("foo")
    parser.add_argument(dest="name")
    parser.add_argument(dest="size", nargs="*", type=int)

    args = parser.parse_args(["rocky", "123", "456"])  # positional passed
    assert {"name": args.name, "size": args.size} == {"name": "rocky", "size": [123, 456]}

    args = parser.parse_args(["rocky"])  # not passed, produce empty list
    assert {"name": args.name, "size": args.size} == {"name": "rocky", "size": []}

    # test of lib

    def foo(name: str, size: Arg[list[int], data(nargs="*")]):
        return locals()

    assert clig.run(foo, ["rocky", "123", "456"]) == {"name": "rocky", "size": [123, 456]}  # passed
    assert clig.run(foo, ["rocky"]) == {"name": "rocky", "size": []}  # not passed, produce empty list

    # same but with type = tuple

    def bar(name: str, size: Arg[tuple[int], data(nargs="*")]):
        return locals()

    assert clig.run(bar, ["rocky", "123", "456"]) == {"name": "rocky", "size": (123, 456)}  # passed
    assert clig.run(bar, ["rocky"]) == {"name": "rocky", "size": ()}  # not passed, produce empty tuple


def test_nargs_starMark_default():
    """Ref: https://docs.python.org/3/library/argparse.html#nargs"""

    # original behavior
    # note that, in this case, to pass a normal nargs="*" produces list, but the default is integer

    parser = ArgumentParser("foo")
    parser.add_argument(dest="name")
    parser.add_argument(dest="size", nargs="*", default=789, type=int)

    args = parser.parse_args(["rocky", "123", "456"])  # positional passed
    assert {"name": args.name, "size": args.size} == {"name": "rocky", "size": [123, 456]}

    args = parser.parse_args(["rocky"])  # not passed, produce default
    assert {"name": args.name, "size": args.size} == {"name": "rocky", "size": 789}

    # test of lib
    # here is the same: a normal nargs="*" produces list, but the default is integer

    def foo(name: str, size: Arg[int, data(nargs="*")] = 789):
        return locals()

    assert clig.run(foo, ["rocky", "--size", "123", "456"]) == {"name": "rocky", "size": [123, 456]}  # passed
    assert clig.run(foo, ["rocky"]) == {"name": "rocky", "size": 789}  # not passed, produce default

    # same but with type = tuple
    # in this case, the default is intentionally passed as tuple (type checker complains)

    def bar(name: str, size: Arg[tuple[int], data(nargs="*")] = (789,)):
        return locals()

    assert clig.run(bar, ["rocky", "--size", "123", "456"]) == {"name": "rocky", "size": (123, 456)}  # passed
    assert clig.run(bar, ["rocky"]) == {"name": "rocky", "size": (789,)}  # not passed, produce default


def test_nargs_starMark_noDefault_defaultOnData():

    # original behavior

    parser = ArgumentParser("foo")
    parser.add_argument(dest="name")
    parser.add_argument(dest="size", nargs="*", default=789, type=int)

    args = parser.parse_args(["rocky", "123", "456"])  # positional passed
    assert {"name": args.name, "size": args.size} == {"name": "rocky", "size": [123, 456]}

    args = parser.parse_args(["rocky"])  # not passed, produce default
    assert {"name": args.name, "size": args.size} == {"name": "rocky", "size": 789}

    # test of lib

    def foo(name: str, size: Arg[int, data(nargs="*", default=789)]):
        return locals()

    assert clig.run(foo, ["rocky", "123", "456"]) == {"name": "rocky", "size": [123, 456]}  # passed
    assert clig.run(foo, ["rocky"]) == {"name": "rocky", "size": 789}  # not passed, produce default

    # same but with type = tuple

    def bar(name: str, size: Arg[tuple[int], data(nargs="*", default=789)]):
        return locals()

    assert clig.run(bar, ["rocky", "123", "456"]) == {"name": "rocky", "size": (123, 456)}  # passed
    assert clig.run(bar, ["rocky"]) == {"name": "rocky", "size": 789}  # not passed, produce default

    # same but with type = list

    def ham(name: str, size: Arg[list[int], data(nargs="*", default=789)]):
        return locals()

    assert clig.run(ham, ["rocky", "123", "456"]) == {"name": "rocky", "size": [123, 456]}  # passed
    assert clig.run(ham, ["rocky"]) == {"name": "rocky", "size": 789}  # not passed, produce default
