##############################################################################################################
# %%          Add `<root>/src` to sys.path
##############################################################################################################

import sys
from pathlib import Path

path = Path(__file__).parent
sys.path.insert(0, str((path).resolve()))
sys.path.insert(0, str((path / "../../src").resolve()))

##############################################################################################################
# %%          Resources
##############################################################################################################
import pytest
from typing import Protocol, Sequence


class OutErr(Protocol):
    out: str
    err: str


class CapSys(Protocol):
    def readouterr(self) -> OutErr: ...


from clig import Command, Arg, data

##############################################################################################################
# %%          LISTS
##############################################################################################################


def test_list_noDefaultOnFunction_turnsIntoPositionalNargsPlus(capsys: CapSys):
    def main(names: list[str]):
        return locals()

    cmd = Command(main)

    assert cmd.run(["tony", "neo"]) == {"names": ["tony", "neo"]}
    assert cmd.arguments[0].nargs == "+"
    assert cmd.arguments[0].default == None  # standard default in argparse

    with pytest.raises(SystemExit) as e:
        Command(main).run([])

    assert e.value.code == 2  # argparse exits with code 2 for argument errors
    output = capsys.readouterr().err
    assert "the following arguments are required: names" in output


def test_list_defaultOnData_noDefaultOnFunction_turnsIntoPositionalNargsPlus(capsys: CapSys):
    def main(names: Arg[list[str], data(default="rocky")]):
        return locals()

    cmd = Command(main)

    assert cmd.run(["tony", "neo"]) == {"names": ["tony", "neo"]}
    assert cmd.arguments[0].nargs == "+"
    assert cmd.arguments[0].default == "rocky"

    with pytest.raises(SystemExit) as e:
        Command(main).run([])

    assert e.value.code == 2  # argparse exits with code 2 for argument errors
    output = capsys.readouterr().err
    assert "the following arguments are required: names" in output


def test_list_withDefault_turnsIntoFlaggedNargsStar():
    def main(names: list[str] = []):
        return locals()

    cmd = Command(main)

    assert cmd.run(["--names", "tony", "neo"]) == {"names": ["tony", "neo"]}
    assert cmd.run([]) == {"names": []}
    assert cmd.arguments[0].nargs == "*"


def test_list_defaultOnData_withDefault_turnsIntoFlaggedNargsStar():
    def main(names: Arg[list[str], data(default="rocky")] = []):
        return locals()

    cmd = Command(main)

    assert cmd.run(["--names", "tony", "neo"]) == {"names": ["tony", "neo"]}
    assert cmd.run([]) == {"names": "rocky"}
    assert cmd.arguments[0].nargs == "*"


def test_unionListNone_withDefaultNone_turnsIntoFlaggedNargsStar():
    def foo(ages: list[int] | None = None):
        return locals()

    cmd = Command(foo)

    assert cmd.run(["--ages", "36", "64", "42"]) == {"ages": [36, 64, 42]}
    assert cmd.run([]) == {"ages": None}
    assert cmd.arguments[0].nargs == "*"


##############################################################################################################
# %%          TUPLES
##############################################################################################################


def test_tuple_noDefaultOnFunction_turnsIntoPositionalNargsN(capsys: CapSys):
    def main(names: tuple[str, str]):
        return locals()

    cmd = Command(main)

    assert cmd.run(["tony", "neo"]) == {"names": ("tony", "neo")}
    assert cmd.arguments[0].nargs == 2
    assert cmd.arguments[0].default == None  # standard default in argparse

    with pytest.raises(SystemExit) as e:
        cmd.run([])

    assert e.value.code == 2  # argparse exits with code 2 for argument errors
    output = capsys.readouterr().err

    assert "the following arguments are required: name" in output

    with pytest.raises(SystemExit) as e:
        cmd.run(["tony", "neo", "jean"])

    assert e.value.code == 2  # argparse exits with code 2 for argument errors
    output = capsys.readouterr().err

    assert "unrecognized arguments: jean" in output


def test_tuple_defaultOnData_noDefaultOnFunction_turnsIntoPositionalNargsN(capsys: CapSys):
    def main(names: Arg[tuple[str, str], data(default="rocky")]):
        return locals()

    cmd = Command(main)

    assert cmd.run(["tony", "neo"]) == {"names": ("tony", "neo")}
    assert cmd.arguments[0].nargs == 2
    assert cmd.arguments[0].default == "rocky"  # give default in data (does not make difference here)

    with pytest.raises(SystemExit) as e:
        cmd.run([])

    assert e.value.code == 2  # argparse exits with code 2 for argument errors
    output = capsys.readouterr().err

    assert "the following arguments are required: name" in output

    with pytest.raises(SystemExit) as e:
        cmd.run(["tony", "neo", "jean"])

    assert e.value.code == 2  # argparse exits with code 2 for argument errors
    output = capsys.readouterr().err

    assert "unrecognized arguments: jean" in output


def test_tuple_withDefault_turnsIntoFlaggedNargsN():
    def main(names: tuple[str, str] = ("tommy", "caco")):
        return locals()

    cmd = Command(main)

    assert cmd.run(["--names", "tony", "neo"]) == {"names": ("tony", "neo")}
    assert cmd.run([]) == {"names": ("tommy", "caco")}
    assert cmd.arguments[0].nargs == 2


def test_tuple_withDefault_withDefaultOnData_turnsIntoFlaggedNargsN(capsys: CapSys):
    def main(names: Arg[tuple[str, str], data(default="rocky")] = ("tommy", "caco")):
        return locals()

    cmd = Command(main)

    assert cmd.run(["--names", "tony", "neo"]) == {"names": ("tony", "neo")}
    assert cmd.run([]) == {"names": "rocky"}
    assert cmd.arguments[0].nargs == 2

    with pytest.raises(SystemExit) as e:
        cmd.run(["--names", "tony", "neo", "jean"])

    assert e.value.code == 2  # argparse exits with code 2 for argument errors
    output = capsys.readouterr().err

    assert "unrecognized arguments: jean" in output


def test_tupleEllipisis_withDefault_turnsIntoFlaggedNargsStar():
    def main(names: Arg[tuple[str, ...], data(default="rocky")] = ()):
        return locals()

    cmd = Command(main)

    assert cmd.run(["--names", "tony", "neo"]) == {"names": ("tony", "neo")}
    assert cmd.run(["--names", "tony", "neo", "jean"]) == {"names": ("tony", "neo", "jean")}
    assert cmd.run([]) == {"names": "rocky"}
    assert cmd.arguments[0].nargs == "*"


def test_unionTupleNone_withDefaultNone_turnsIntoFlaggedNargsN():
    def foo(ages: tuple[int, int] | None = None):
        return locals()

    cmd = Command(foo)

    assert cmd.run(["--ages", "36", "64"]) == {"ages": (36, 64)}
    assert cmd.run([]) == {"ages": None}
    assert cmd.arguments[0].nargs == 2


def test_unions_with_different_types():

    # This is to show that the order in the Union matters

    def foo(ages: tuple[int, int] | int = 33):
        return locals()

    cmd = Command(foo)

    assert cmd.run(["--ages", "36", "45"]) == {"ages": (36, 45)}
    assert cmd.run([]) == {"ages": 33}
    assert cmd.arguments[0].nargs == 2

    def bar(ages: int | tuple[int, int] = 33):
        return locals()

    cmd = Command(bar)

    assert cmd.run(["--ages", "36"]) == {"ages": 36}
    assert cmd.run([]) == {"ages": 33}
    assert cmd.arguments[0].nargs == None


##############################################################################################################
# %%          SEQUENCES
##############################################################################################################


def test_Sequence_noDefaultOnFunction_turnsIntoPositionalNargsPlus(capsys: CapSys):
    def main(names: Sequence[str]):
        return locals()

    cmd = Command(main)

    assert cmd.run(["tony", "neo"]) == {"names": ["tony", "neo"]}
    assert cmd.run(["tony", "neo", "jean"]) == {"names": ["tony", "neo", "jean"]}
    assert cmd.arguments[0].nargs == "+"
    assert cmd.arguments[0].default == None  # standard default in argparse

    with pytest.raises(SystemExit) as e:
        Command(main).run([])

    assert e.value.code == 2  # argparse exits with code 2 for argument errors
    output = capsys.readouterr().err
    assert "the following arguments are required: names" in output


def test_Sequence_defaultOnData_noDefaultOnFunction_turnsIntoPositionalNargsPlus(capsys: CapSys):
    def main(names: Arg[Sequence[str], data(default="rocky")]):
        return locals()

    cmd = Command(main)

    assert cmd.run(["tony", "neo"]) == {"names": ["tony", "neo"]}
    assert cmd.run(["tony", "neo", "jean"]) == {"names": ["tony", "neo", "jean"]}
    assert cmd.arguments[0].nargs == "+"
    assert cmd.arguments[0].default == "rocky"  # give default in data (does not make difference here)

    with pytest.raises(SystemExit) as e:
        Command(main).run([])

    assert e.value.code == 2  # argparse exits with code 2 for argument errors
    output = capsys.readouterr().err
    assert "the following arguments are required: names" in output


def test_Sequence_withDefault_turnsIntoFlaggedNargsStar():
    def main(names: Sequence[str] = []):
        return locals()

    cmd = Command(main)

    assert cmd.run(["--names", "tony", "neo"]) == {"names": ["tony", "neo"]}
    assert cmd.run(["--names", "tony", "neo", "jean"]) == {"names": ["tony", "neo", "jean"]}
    assert cmd.run([]) == {"names": []}
    assert cmd.arguments[0].nargs == "*"


def test_Sequence_withDefaultAndDefaultOnData_turnsIntoFlaggedNargsStar():
    def main(names: Arg[Sequence[str], data(default="rocky")] = []):
        return locals()

    cmd = Command(main)

    assert cmd.run(["--names", "tony", "neo"]) == {"names": ["tony", "neo"]}
    assert cmd.run([]) == {"names": "rocky"}
    assert cmd.arguments[0].nargs == "*"


def test_unionSequenceNone_withDefaultNone_turnsIntoFlaggedNargsStar():
    def foo(ages: Sequence[int] | None = None):
        return locals()

    cmd = Command(foo)

    assert cmd.run(["--ages", "36", "64", "42"]) == {"ages": [36, 64, 42]}
    assert cmd.run([]) == {"ages": None}
    assert cmd.arguments[0].nargs == "*"
