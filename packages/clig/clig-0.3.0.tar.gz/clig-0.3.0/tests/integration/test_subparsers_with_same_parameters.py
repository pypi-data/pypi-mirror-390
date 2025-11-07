import sys
from pathlib import Path

path = Path(__file__).parent
sys.path.insert(0, str((path).resolve()))
sys.path.insert(0, str((path / "../../src").resolve()))

from clig import Command, Arg, data
from argparse import ArgumentParser, Namespace


def test_subparsers_with_same_parameters_all_kw():

    # original lib has an issue

    parser = ArgumentParser()
    parser.add_argument("--foo")
    subs = parser.add_subparsers()
    subparser = subs.add_parser("sub")
    subparser.add_argument("--foo")
    subsubs = subparser.add_subparsers()
    subsubparser = subsubs.add_parser("subsub")
    subsubparser.add_argument("--foo")

    assert parser.parse_args(["--foo", "yoco"]) == Namespace(foo="yoco")
    assert parser.parse_args(["--foo", "yoco", "sub", "--foo", "rocky"]) == Namespace(foo="rocky")
    assert parser.parse_args(
        ["--foo", "yoco", "sub", "--foo", "rocky", "subsub", "--foo", "sand"]
    ) == Namespace(foo="sand")

    # issue solved

    def maincmd(foo: str | None = None):
        assert foo == "yoco"

    def subcmd(foo: str | None = None):
        assert foo == "rocky"

    def subsubcmd(foo: str | None = None):
        assert foo == "sand"

    (
        Command(maincmd)
        .new_subcommand(subcmd)
        .end_subcommand(subsubcmd)
        .run("--foo yoco subcmd --foo rocky subsubcmd --foo sand".split())
    )
