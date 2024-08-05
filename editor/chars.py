from typing import List

from datamodel import bools, Character, Expression, Nil
from environment import global_attr, Frame
from helper import verify_exact_callable_length
from primitives import BuiltIn, SingleOperandPrimitive
from scheme_exceptions import OperandDeduceError


def assert_all_characters(operator: Expression, operands: List[Expression]):
    for operand in operands:
        if not isinstance(operand, Character):
            raise OperandDeduceError(f"{operator} expected a character, received: {operand}.")


@global_attr("char=?")
class IsCharEqual(BuiltIn):
    def execute_evaluated(self, operands: List[Expression], frame: Frame):
        verify_exact_callable_length(self, 2, len(operands))
        assert_all_characters(self, operands)
        return bools[operands[0].value == operands[1].value]


@global_attr("char<?")
class IsCharLess(BuiltIn):
    def execute_evaluated(self, operands: List[Expression], frame: Frame):
        verify_exact_callable_length(self, 2, len(operands))
        assert_all_characters(self, operands)
        return bools[operands[0].value < operands[1].value]


@global_attr("char>?")
class IsCharGreater(BuiltIn):
    def execute_evaluated(self, operands: List[Expression], frame: Frame):
        verify_exact_callable_length(self, 2, len(operands))
        assert_all_characters(self, operands)
        return bools[operands[0].value > operands[1].value]


@global_attr("char<=?")
class IsCharLessOrEqual(BuiltIn):
    def execute_evaluated(self, operands: List[Expression], frame: Frame):
        verify_exact_callable_length(self, 2, len(operands))
        assert_all_characters(self, operands)
        return bools[operands[0].value <= operands[1].value]


@global_attr("char>=?")
class IsCharGreaterOrEqual(BuiltIn):
    def execute_evaluated(self, operands: List[Expression], frame: Frame):
        verify_exact_callable_length(self, 2, len(operands))
        assert_all_characters(self, operands)
        return bools[operands[0].value >= operands[1].value]


@global_attr("char-ci=?")
class IsCharCiEqual(BuiltIn):
    def execute_evaluated(self, operands: List[Expression], frame: Frame):
        verify_exact_callable_length(self, 2, len(operands))
        assert_all_characters(self, operands)
        return bools[operands[0].value.lower() == operands[1].value.lower()]


@global_attr("char-ci<?")
class IsCharCiLess(BuiltIn):
    def execute_evaluated(self, operands: List[Expression], frame: Frame):
        verify_exact_callable_length(self, 2, len(operands))
        assert_all_characters(self, operands)
        return bools[operands[0].value.lower() < operands[1].value.lower()]


@global_attr("char-ci>?")
class IsCharCiGreater(BuiltIn):
    def execute_evaluated(self, operands: List[Expression], frame: Frame):
        verify_exact_callable_length(self, 2, len(operands))
        assert_all_characters(self, operands)
        return bools[operands[0].value.lower() > operands[1].value.lower()]


@global_attr("char-ci<=?")
class IsCharCiLessOrEqual(BuiltIn):
    def execute_evaluated(self, operands: List[Expression], frame: Frame):
        verify_exact_callable_length(self, 2, len(operands))
        assert_all_characters(self, operands)
        return bools[operands[0].value.lower() <= operands[1].value.lower()]


@global_attr("char-ci>=?")
class IsCharCiGreaterOrEqual(BuiltIn):
    def execute_evaluated(self, operands: List[Expression], frame: Frame):
        verify_exact_callable_length(self, 2, len(operands))
        assert_all_characters(self, operands)
        return bools[operands[0].value.lower() >= operands[1].value.lower()]


@global_attr("char-alphabetic?")
class IsCharAlphabetic(SingleOperandPrimitive):
    def execute_simple(self, operand: Expression):
        assert_all_characters(self, [operand])
        return bools[operand.value.isalpha()]


@global_attr("char-numeric?")
class IsCharNumeric(SingleOperandPrimitive):
    def execute_simple(self, operand: Expression):
        assert_all_characters(self, [operand])
        return bools[operand.value.isnumeric()]


@global_attr("char-whitespace?")
class IsCharWhitespace(SingleOperandPrimitive):
    def execute_simple(self, operand: Expression):
        assert_all_characters(self, [operand])
        return bools[operand.value.isspace()]


@global_attr("char-lower-case?")
class IsCharLowerCase(SingleOperandPrimitive):
    def execute_simple(self, operand: Expression):
        assert_all_characters(self, [operand])
        return bools[operand.value.islower()]


@global_attr("char-upper-case?")
class IsCharUpperCase(SingleOperandPrimitive):
    def execute_simple(self, operand: Expression):
        assert_all_characters(self, [operand])
        return bools[operand.value.isupper()]


@global_attr("char-upcase")
class CharUpcase(SingleOperandPrimitive):
    def execute_simple(self, operand: Expression):
        assert_all_characters(self, [operand])
        return Character(f"#\\{operand.value.upper()}")


@global_attr("char-downcase")
class CharDowncase(SingleOperandPrimitive):
    def execute_simple(self, operand: Expression):
        assert_all_characters(self, [operand])
        return Character(f"#\\{operand.value.lower()}")
