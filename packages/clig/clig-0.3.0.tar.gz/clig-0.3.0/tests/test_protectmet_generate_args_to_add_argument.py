# cSpell: disable
import sys
from pathlib import Path
from argparse import BooleanOptionalAction

this_dir = Path(__file__).parent

sys.path.insert(0, str((this_dir).resolve()))
sys.path.insert(0, str((this_dir / "../src").resolve()))
sys.path.insert(0, str((this_dir / "../src").resolve()))
from clig.clig import Command, _normalize_docstring, _CompleteKeywordArguments
import functions as fun


def test_inferarg__pn_knc_noDoc():
    cmd = Command(fun.pn_knc_noDoc)
    arg_1, arg_2 = cmd.argument_data
    assert cmd._generate_args_for_add_argument(arg_1) == (
        (),
        _CompleteKeywordArguments(
            action="store",
            dest="first",
            type=str,
            default=None,
            nargs=None,
            choices=None,
            help=None,
        ),
    )
    assert cmd._generate_args_for_add_argument(arg_2) == (
        ("--second",),
        _CompleteKeywordArguments(
            action="store",
            dest="second",
            type=str,
            default="test",
            nargs=None,
            choices=None,
            help=None,
        ),
    )


def test_inferarg__pn_pt_kti_noDoc():
    cmd = Command(fun.pn_pt_kti_noDoc)
    arg_a, arg_b, arg_c = cmd.argument_data
    assert cmd._generate_args_for_add_argument(arg_a) == (
        (),
        _CompleteKeywordArguments(
            action="store",
            dest="a",
            type=str,
            default=None,
            nargs=None,
            choices=None,
            help=None,
        ),
    )
    assert cmd._generate_args_for_add_argument(arg_b) == (
        (),
        _CompleteKeywordArguments(
            action="store",
            dest="b",
            type=float,
            default=None,
            nargs=None,
            choices=None,
            help=None,
        ),
    )
    assert cmd._generate_args_for_add_argument(arg_c) == (
        ("--c",),
        _CompleteKeywordArguments(
            action="store",
            dest="c",
            type=int,
            default=123,
            nargs=None,
            choices=None,
            help=None,
        ),
    )


def test_inferarg__ptc_kti_ktb_cligDocMutiline():
    cmd = Command(fun.ptc_kti_ktb_cligDocMutiline)
    arg_a, arg_b, arg_c = cmd.argument_data
    assert cmd._generate_args_for_add_argument(arg_a) == (
        (),
        _CompleteKeywordArguments(
            action="store",
            dest="a",
            type=str,
            default=None,
            nargs=None,
            choices=None,
            help=arg_a.help,
        ),
    )
    assert cmd._generate_args_for_add_argument(arg_b) == (
        ("--b",),
        _CompleteKeywordArguments(
            action="store",
            dest="b",
            type=int,
            default=123,
            nargs=None,
            choices=None,
            help=arg_b.help,
        ),
    )
    assert cmd._generate_args_for_add_argument(arg_c) == (
        ("--c",),
        _CompleteKeywordArguments(
            action="store_false",
            dest="c",
            default=True,
            help=arg_c.help,
        ),
    )


def test_inferarg__ptcm_ptcm_ktb():
    cmd = Command(fun.ptcm_ptim_ktb)
    arg_a, arg_b, arg_c = cmd.argument_data
    assert cmd._generate_args_for_add_argument(arg_a) == (
        ("-f", "--first"),
        _CompleteKeywordArguments(
            dest="a",
            default=None,
            nargs=None,
            required=True,
            choices=None,
            action="store",
            type=str,
            help="The first argument",
        ),
    )
    assert cmd._generate_args_for_add_argument(arg_b) == (
        (),
        _CompleteKeywordArguments(
            dest="b",
            action="store_const",
            default=None,
            const=123,
            help=None,
        ),
    )
    assert cmd._generate_args_for_add_argument(arg_c) == (
        ("--c",),
        _CompleteKeywordArguments(
            dest="c",
            help=None,
            default=True,
            action="store_false",
        ),
    )


def test_inferarg__pti_ptc_ptf_ktb_ktlo_numpyEpilogMultiline():
    cmd = Command(fun.pti_ptc_ptf_ktb_ktlo_numpyEpilogMultiline)
    args_a, args_b, args_c, args_d, args_e = cmd.argument_data
    assert cmd._generate_args_for_add_argument(args_a) == (
        (),
        _CompleteKeywordArguments(
            dest="a",
            default=None,
            action="store",
            type=int,
            nargs=None,
            choices=None,
            help=_normalize_docstring(
                """Fuga nemo provident vero odio qui sint et aut veritatis. Facere necessitatibus ut. Voluptatem
                natus natus veritatis earum. Reprehenderit voluptate dolorem dolores consequuntur magnam impedit
                eius. Est ut nisi aut accusamus."""
            ),
        ),
    )
    assert cmd._generate_args_for_add_argument(args_b) == (
        (),
        _CompleteKeywordArguments(
            dest="b",
            default=None,
            action="store",
            type=str,
            nargs=None,
            choices=None,
            help="Culpa asperiores incidunt molestias aliquam soluta voluptas excepturi nulla.",
        ),
    )


def test_inferarg__ptc_ptb_cligEpilog():
    cmd = Command(fun.ptc_ptb_cligEpilog)
    arg_name, arg_flag = cmd.argument_data
    assert cmd._generate_args_for_add_argument(arg_name) == (
        (),
        _CompleteKeywordArguments(
            dest="name",
            default=None,
            action="store",
            type=str,
            nargs=None,
            choices=None,
            help="Sequi deserunt est quia qui.",
        ),
    )
    assert cmd._generate_args_for_add_argument(arg_flag) == (
        ("--flag",),
        _CompleteKeywordArguments(
            dest="flag",
            default=None,
            action=BooleanOptionalAction,
            required=True,
            help="Labore eius et voluptatem quos et consequatur dolores.",
        ),
    )
