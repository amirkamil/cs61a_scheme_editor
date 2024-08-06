from typing import List

from datamodel import bools, Character, Expression, Nil, Number, String
from environment import global_attr, Frame
from helper import verify_exact_callable_length, verify_range_callable_length
from primitives import BuiltIn, SingleOperandPrimitive, UnsupportedBuiltIn
from scheme_exceptions import OperandDeduceError, UnsupportedOperationError


@global_attr("make-string")
class MakeString(BuiltIn):
    def execute_evaluated(self, operands: List[Expression], frame: Frame) -> Expression:
        verify_range_callable_length(self, 1, 2, len(operands))
        if len(operands) == 1:
            raise UnsupportedOperationError("the single-argument version of make-string")
        if not isinstance(operands[0], Number) or not isinstance(operands[0].value, int):
            raise OperandDeduceError("make-string expects an integer for the first "
                                     f"argument, received: {operands[0]}.")
        if not isinstance(operands[1], Character):
            raise OperandDeduceError("make-string expects a character for the second "
                                     f"argument, received: {operands[1]}.")
        return String(operands[1].value * operands[0].value)


@global_attr("string")
class StringProc(BuiltIn):
    def execute_evaluated(self, operands: List[Expression], frame: Frame) -> Expression:
        for arg in operands:
            if not isinstance(arg, Character):
                raise OperandDeduceError("string procedure expects a character, "
                                         f"received: {arg}.")
        return String(''.join(arg.value for arg in operands))


@global_attr("string-length")
class StringLength(SingleOperandPrimitive):
    def execute_simple(self, operand: Expression) -> Expression:
        if not isinstance(operand, String):
            raise OperandDeduceError("string-length expects a character, received: "
                                     f"{operand}.")
        return Number(len(operand.value))


@global_attr("string-ref")
class StringRef(BuiltIn):
    def execute_evaluated(self, operands: List[Expression], frame: Frame) -> Expression:
        verify_exact_callable_length(self, 2, len(operands))
        if not isinstance(operands[0], String):
            raise OperandDeduceError("string-ref expects a string for the first, "
                                     f"argument, received: {operands[0]}.")
        if not isinstance(operands[1], Number) or not isinstance(operands[1].value, int):
            raise OperandDeduceError("string-ref expects an integer for the second "
                                     f"argument, received: {operands[1]}.")
        if not (0 <= operands[1].value < len(operands[0].value)):
            raise OperandDeduceError("string-ref received out-of-range index "
                                     f"{operands[1]} for string {operands[0]}.")
        return Character(f"#\\{operands[0].value[operands[1].value]}")


@global_attr("string-set!")
class StringRef(UnsupportedBuiltIn):
    pass  # unimplemented


def verify_string_comparison_operands(operator: Expression, operands: List[Expression]):
    verify_exact_callable_length(operator, 2, len(operands))
    for operand in operands:
        if not isinstance(operand, String):
            raise OperandDeduceError(f"{operator} expects a string, received: {operand}.")


@global_attr("string=?")
class IsStringEq(BuiltIn):
    def execute_evaluated(self, operands: List[Expression], frame: Frame) -> Expression:
        verify_string_comparison_operands(self, operands)
        return bools[operands[0].value == operands[1].value]


@global_attr("string-ci=?")
class IsStringCiEq(BuiltIn):
    def execute_evaluated(self, operands: List[Expression], frame: Frame) -> Expression:
        verify_string_comparison_operands(self, operands)
        return bools[operands[0].value.lower() == operands[1].value.lower()]


@global_attr("string<?")
class IsStringLess(BuiltIn):
    def execute_evaluated(self, operands: List[Expression], frame: Frame) -> Expression:
        verify_string_comparison_operands(self, operands)
        return bools[operands[0].value < operands[1].value]


@global_attr("string-ci<?")
class IsStringCiLess(BuiltIn):
    def execute_evaluated(self, operands: List[Expression], frame: Frame) -> Expression:
        verify_string_comparison_operands(self, operands)
        return bools[operands[0].value.lower() < operands[1].value.lower()]


@global_attr("string<=?")
class IsStringLessOrEq(BuiltIn):
    def execute_evaluated(self, operands: List[Expression], frame: Frame) -> Expression:
        verify_string_comparison_operands(self, operands)
        return bools[operands[0].value <= operands[1].value]


@global_attr("string-ci<=?")
class IsStringCiLessOrEq(BuiltIn):
    def execute_evaluated(self, operands: List[Expression], frame: Frame) -> Expression:
        verify_string_comparison_operands(self, operands)
        return bools[operands[0].value.lower() <= operands[1].value.lower()]


@global_attr("string>?")
class IsStringGreater(BuiltIn):
    def execute_evaluated(self, operands: List[Expression], frame: Frame) -> Expression:
        verify_string_comparison_operands(self, operands)
        return bools[operands[0].value > operands[1].value]


@global_attr("string-ci>?")
class IsStringCiGreater(BuiltIn):
    def execute_evaluated(self, operands: List[Expression], frame: Frame) -> Expression:
        verify_string_comparison_operands(self, operands)
        return bools[operands[0].value.lower() > operands[1].value.lower()]


@global_attr("string>=?")
class IsStringGreaterOrEq(BuiltIn):
    def execute_evaluated(self, operands: List[Expression], frame: Frame) -> Expression:
        verify_string_comparison_operands(self, operands)
        return bools[operands[0].value >= operands[1].value]


@global_attr("string-ci>=?")
class IsStringCiGreaterOrEq(BuiltIn):
    def execute_evaluated(self, operands: List[Expression], frame: Frame) -> Expression:
        verify_string_comparison_operands(self, operands)
        return bools[operands[0].value.lower() >= operands[1].value.lower()]


@global_attr("substring")
class SubString(BuiltIn):
    def execute_evaluated(self, operands: List[Expression], frame: Frame) -> Expression:
        verify_exact_callable_length(self, 3, len(operands))
        if not isinstance(operands[0], String):
            raise OperandDeduceError("substring expects a string, received: "
                                     f"{operands[0]}.")
        for arg in operands[1:]:
            if not isinstance(arg, Number) or not isinstance(arg.value, int):
                raise OperandDeduceError("substring expects an integer index, "
                                         f"received: {arg}.")
            if not (0 <= arg.value <= len(operands[0].value)):
                raise OperandDeduceError("substring received out-of-range index "
                                         f"{arg} for string {operands[0]}.")
        if operands[1].value > operands[2].value:
            raise OperandDeduceError("substring requires start index to be greater "
                                     "than or equal to end index, received start: "
                                     f"{operands[1]}; end: {operands[2]}.")
        return String(operands[0].value[operands[1].value: operands[2].value])


@global_attr("string-append")
class StringAppend(BuiltIn):
    def execute_evaluated(self, operands: List[Expression], frame: Frame) -> Expression:
        for arg in operands:
            if not isinstance(arg, String):
                raise OperandDeduceError("string-append expects a string, "
                                         f"received: {arg}.")
        return String(''.join(arg.value for arg in operands))


@global_attr("string-copy")
class StringAppend(SingleOperandPrimitive):
    def execute_simple(self, operand: Expression) -> Expression:
        if not isinstance(operand, String):
            raise OperandDeduceError("string-copy expects a string, received: "
                                     f"{operand}.")
        return String(operand.value)


@global_attr("string-fill!")
class StringRef(UnsupportedBuiltIn):
    pass  # unimplemented
