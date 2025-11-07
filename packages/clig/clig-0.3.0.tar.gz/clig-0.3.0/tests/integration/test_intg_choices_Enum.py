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
from typing import Protocol, Literal
from enum import Enum, StrEnum


class OutErr(Protocol):
    out: str
    err: str


class CapSys(Protocol):
    def readouterr(self) -> OutErr: ...


class Color(Enum):
    red = 1
    blue = 2
    yellow = 3


class Statistic(StrEnum):
    minimun = "minimun"
    mean = "mean"
    maximum = "maximum"


from clig import Command

##############################################################################################################
# %%          TESTS
##############################################################################################################


def test_enum(capsys: CapSys):

    def main(color: Color, statistic: Statistic):
        return locals()

    cmd = Command(main)

    assert cmd.run(["red", "mean"]) == {"color": Color(1), "statistic": Statistic("mean")}

    with pytest.raises(SystemExit) as e:
        Command(main).run(["green"])

    assert e.value.code == 2  # argparse exits with code 2 for argument errors
    output = capsys.readouterr().err
    assert "argument color: invalid choice: 'green' (choose from red, blue, yellow)" in output


def test_LiteralWithenum(capsys: CapSys):

    def main(color: Literal[Color.red, "green", "black"]):
        return locals()

    cmd = Command(main)

    assert cmd.run(["red"]) == {"color": Color(1)}
    assert cmd.run(["green"]) == {"color": "green"}
    assert cmd.run(["black"]) == {"color": "black"}

    with pytest.raises(SystemExit) as e:
        Command(main).run(["cyan"])

    assert e.value.code == 2  # argparse exits with code 2 for argument errors
    output = capsys.readouterr().err
    assert "argument color: invalid choice: 'cyan' (choose from red, green, black)" in output
