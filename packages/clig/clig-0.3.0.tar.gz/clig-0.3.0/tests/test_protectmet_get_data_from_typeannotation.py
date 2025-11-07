import inspect
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.dirname(__file__) + "/../src"))
from clig import clig

from typing import Literal, Sequence


def test_get_data_from_argtype_simple_type():
    action, nargs, argtype, choices = clig._get_data_from_typeannotation(ascii)
    assert action == "store"
    assert nargs == None
    assert argtype == ascii
    assert choices is None


def test_get_data_from_argtype_Literal():
    action, nargs, argtype, choices = clig._get_data_from_typeannotation(Literal["option1", "option2"])
    assert action == "store"
    assert nargs == None
    assert argtype == None
    assert choices is not None
    assert set(choices) == set(["option1", "option2"])


def test_get_data_from_argtype_List():
    action, nargs, argtype, choices = clig._get_data_from_typeannotation(list[str])
    assert action == "store"
    assert nargs == "*"
    assert argtype == str
    assert choices is None


def test_get_data_from_argtype_Sequence():
    action, nargs, argtype, choices = clig._get_data_from_typeannotation(Sequence[int])
    assert action == "store"
    assert nargs == "*"
    assert argtype == int
    assert choices is None


def test_get_data_from_argtype_Tuple():
    action, nargs, argtype, choices = clig._get_data_from_typeannotation(tuple[int, int, int])
    assert action == "store"
    assert nargs == 3
    assert argtype == int
    assert choices is None


def test_get_data_from_argtype_Tuple_Ellipsis():
    action, nargs, argtype, choices = clig._get_data_from_typeannotation(tuple[float, ...])
    assert action == "store"
    assert nargs == "*"
    assert argtype == float
    assert choices is None


def test_get_data_from_argtype_Bool():
    action, nargs, argtype, choices = clig._get_data_from_typeannotation(bool)
    assert action == "store_true"
    assert nargs == None
    assert argtype == None
    assert choices is None
