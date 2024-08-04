from typing import List

from datamodel import Expression, Nil
from environment import global_attr, Frame
from helper import verify_exact_callable_length
from primitives import BuiltIn, SingleOperandPrimitive, UnsupportedBuiltIn, UnsupportedSingleOperandPrimitive
from scheme_exceptions import OperandDeduceError
