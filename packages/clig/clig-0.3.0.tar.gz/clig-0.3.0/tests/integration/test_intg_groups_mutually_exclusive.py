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


from clig import Command, Arg, data, MutuallyExclusiveGroup

##############################################################################################################
# %%          LISTS
##############################################################################################################


def test_groups_mutually_exclusive_noRequired(capsys: CapSys):

    g = MutuallyExclusiveGroup(required=False)

    def main(foo: Arg[str, data(group=g)] = "test", bar: Arg[int, data(group=g)] = 0):
        return locals()

    with pytest.raises(SystemExit) as e:
        Command(main).run("--foo rocky --bar 42".split())

    assert e.value.code == 2  # argparse exits with code 2 for argument errors
    output = capsys.readouterr().err
    assert "argument --bar: not allowed with argument --foo" in output


def test_groups_mutually_exclusive_required(capsys: CapSys):

    g = MutuallyExclusiveGroup(required=True)

    def main(foo: Arg[str, data(group=g)] = "test", bar: Arg[int, data(group=g)] = 0):
        return locals()

    with pytest.raises(SystemExit) as e:
        Command(main).run([])

    assert e.value.code == 2  # argparse exits with code 2 for argument errors
    output = capsys.readouterr().err
    assert "one of the arguments --foo --bar is required" in output
