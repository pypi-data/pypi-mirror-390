# cSpell: disable
import sys
from pathlib import Path

this_dir = Path(__file__).parent

sys.path.insert(0, str((this_dir).resolve()))
sys.path.insert(0, str((this_dir / "../src").resolve()))

from clig.clig import _normalize_docstring, Command, _ArgumentData, EMPTY
import functions as fun


def test_argumentdata_simple():
    cmd = Command(fun.pn_knc_noDoc)
    arg_1, arg_2 = cmd.argument_data
    assert arg_1 == _ArgumentData("first")
    assert arg_2 == _ArgumentData("second", typeannotation=str, default="test")


def test_argumentdata_with_types():
    cmd = Command(fun.pn_pt_kti_noDoc)
    arg_a, arg_b, arg_c = cmd.argument_data
    assert arg_a == _ArgumentData("a")
    assert arg_b == _ArgumentData("b", typeannotation=float)
    assert arg_c == _ArgumentData("c", typeannotation=int, default=123)


def test_argumentdata_with_types_and_helps():
    cmd = Command(fun.ptc_kti_ktb_cligDocMutiline)
    arg_a, arg_b, arg_c = cmd.argument_data
    assert arg_a == _ArgumentData("a", typeannotation=str, help="Dicta et optio dicta.")
    assert arg_b == _ArgumentData(
        "b", typeannotation=int, default=123, help="Dolorum voluptate voluptas nisi."
    )
    assert arg_c == _ArgumentData(
        "c",
        typeannotation=bool,
        default=True,
        help=_normalize_docstring(
            """Asperiores quisquam odit voluptates et eos incidunt. Maiores minima provident doloremque aut
            dolorem. Minus natus ab voluptatum totam in. Natus consectetur modi similique rerum excepturi
            delectus aut."""
        ),
    )


def test_argumentdata_with_types_and_metadata():
    cmd = Command(fun.ptcm_ptim_ktb)
    arga, argb, argc = cmd.argument_data
    assert arga == _ArgumentData(
        name="a",
        default=EMPTY,
        typeannotation=str,
        help=None,
        make_flag=None,
        group=None,
        flags=["-f", "--first"],
        kwargs={"help": "The first argument"},
    )
    assert argb == _ArgumentData(
        "b", flags=[], typeannotation=int, kwargs={"action": "store_const", "const": 123}
    )
    assert argc == _ArgumentData(
        "c",
        flags=[],
        typeannotation=bool,
        default=True,
    )


def test_argumentdata_posWithType_posBoolWithType_cligDoc():
    cmd = Command(fun.ptc_ptb_cligEpilog)
    arg_name, arg_flag = cmd.argument_data
    assert arg_name == _ArgumentData("name", typeannotation=str, help="Sequi deserunt est quia qui.")
    assert arg_flag == _ArgumentData(
        "flag", typeannotation=bool, help="Labore eius et voluptatem quos et consequatur dolores."
    )
