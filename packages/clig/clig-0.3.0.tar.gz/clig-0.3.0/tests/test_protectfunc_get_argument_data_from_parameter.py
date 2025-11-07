# cSpell: disable
import inspect
import sys
from pathlib import Path

this_dir = Path(__file__).parent

sys.path.insert(0, str((this_dir).resolve()))
sys.path.insert(0, str((this_dir / "../src").resolve()))

from clig.clig import _get_argument_data_from_parameter, _ArgumentData, Kind
import functions as fun


def test_parameter_without_annotation():
    parameter = inspect.signature(fun.pn_noDoc).parameters["a"]
    argmetadata = _get_argument_data_from_parameter(parameter)
    assert argmetadata == _ArgumentData(name="a", kind=Kind.POSITIONAL_OR_KEYWORD)


def test_get_argdata_from_parameter_posWithType_posBoolWithType_cligDoc():
    parameters = inspect.signature(fun.ptc_ptb_cligEpilog).parameters
    par_name, par_flag = parameters["name"], parameters["flag"]
    arg_data_par_name = _get_argument_data_from_parameter(par_name)
    arg_data_par_flag = _get_argument_data_from_parameter(par_flag)
    assert arg_data_par_name == _ArgumentData(name="name", typeannotation=str)
    assert arg_data_par_flag == _ArgumentData(name="flag", typeannotation=bool)
