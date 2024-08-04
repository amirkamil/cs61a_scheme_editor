from typing import List

from datamodel import Character, Expression, Nil, Number, Pair, Symbol, String, Vector
from environment import global_attr, Frame
from execution_parser import is_number
from helper import make_list, pair_to_list, verify_range_callable_length
from lexer import SPECIALS
from primitives import BuiltIn, SingleOperandPrimitive, UnsupportedBuiltIn, UnsupportedSingleOperandPrimitive
from scheme_exceptions import OperandDeduceError


@global_attr("exact->inexact")
class ExactToInexact(UnsupportedSingleOperandPrimitive):
    pass  # unimplemented


@global_attr("inexact->exact")
class InexactToExact(UnsupportedSingleOperandPrimitive):
    pass  # unimplemented


@global_attr("number->string")
class NumberToString(UnsupportedBuiltIn):
    def execute_evaluated(self, operands: List[Expression], frame: Frame) -> Expression:
        verify_range_callable_length(self, 1, 2, len(operands))
        if not isinstance(operands[0], Number):
            raise OperandDeduceError(f"number->string expects a number, received: {operands[0]}.")
        if len(operands) == 2 and \
               (not isinstance(operands[1], Number) or
                operands[1].value not in (2, 8, 10, 16)):
            raise OperandDeduceError(f"number->string expects the radix to be 2, 8, 10, or 16, received: {operands[1]}.")
        base = 10 if len(operands) < 2 else operands[1].value
        if base != 10 and not isinstance(operands[0].value, int):
            raise OperandDeduceError(f"number->string only supports a radix of 10 for "
                                     "floating-point numbers, received radix "
                                     f"{operands[1]} for number {operands[0]}.")
        if base == 10:
            return String(str(operands[0].value))
        fmt = {2: "{:b}", 8: "{:o}", 16: "{:x}"}[base]
        return String(fmt.format(operands[0].value))


@global_attr("string->number")
class StringToNumber(BuiltIn):
    def execute_evaluated(self, operands: List[Expression], frame: Frame) -> Expression:
        verify_range_callable_length(self, 1, 2, len(operands))
        if not isinstance(operands[0], String):
            raise OperandDeduceError(f"string->number expects a string, received: {operands[0]}.")
        if len(operands) == 2 and \
               (not isinstance(operands[1], Number) or
                operands[1].value not in (2, 8, 10, 16)):
            raise OperandDeduceError(f"string->number expects the radix to be 2, 8, 10, or 16, received: {operands[1]}.")
        base = 10 if len(operands) < 2 else operands[1].value
        try:
            return Number(int(operands[0].value, base))
        except ValueError:
            pass
        if base != 10:
            raise OperandDeduceError("string->number only supports a radix other than "
                                     f"10 for integers, received radix {base} for "
                                     f"incompatible string {operands[0]}.")
        try:
            return Number(float(operands[0].value))
        except ValueError:
            raise OperandDeduceError(f"string does not represent a supported number in radix 10: {operands[0]}.")


@global_attr("symbol->string")
class SymbolToString(SingleOperandPrimitive):
    def execute_simple(self, operand: Expression) -> Expression:
        if not isinstance(operand, Symbol):
            raise OperandDeduceError(f"symbol->string expects a symbol, received: {operand}.")
        if operand.value[0] == '[':
            value = operand.value[1:-1]
            for escapee in "][\\":
                value = value.replace("\\" + escapee, escapee)
            return String(value)
        return String(operand.value)


@global_attr("string->symbol")
class StringToSymbol(SingleOperandPrimitive):
    def _escape(self, value: str) -> bool:
        if is_number(value) or value.lower() in ('nil', '#f', '#t') or \
               value.startswith("#\\") or set(value) & set(SPECIALS):
            for escapee in "\\[]":
                value = value.replace(escapee, "\\" + escapee)
            value = f"[{value}]"
        return value

    def execute_simple(self, operand: Expression) -> Expression:
        if not isinstance(operand, String):
            raise OperandDeduceError(f"string->symbol expects a string, received: {operand}.")
        return Symbol(self._escape(operand.value))


@global_attr("char->integer")
class CharToInteger(SingleOperandPrimitive):
    def execute_simple(self, operand: Expression) -> Expression:
        if not isinstance(operand, Character):
            raise OperandDeduceError(f"char->integer expects a character, received: {operand}.")
        return Number(ord(operand.value))


@global_attr("integer->char")
class IntegerToChar(SingleOperandPrimitive):
    def execute_simple(self, operand: Expression) -> Expression:
        if not isinstance(operand, Number) or not isinstance(operand.value, int):
            raise OperandDeduceError(f"integer->char expects an integer, received: {operand}.")
        return Character(f"#\\{chr(operand.value)}")


@global_attr("string->list")
class StringToList(SingleOperandPrimitive):
    def execute_simple(self, operand: Expression) -> Expression:
        if not isinstance(operand, String):
            raise OperandDeduceError(f"string->list expects a string, received: {operand}.")
        return make_list([Character(f"#\\{c}") for c in operand.value])


@global_attr("list->string")
class ListToString(SingleOperandPrimitive):
    def execute_simple(self, operand: Expression) -> Expression:
        if not isinstance(operand, Pair) and operand is not Nil:
            raise OperandDeduceError(f"list->string expects a list, received: {operand}.")
        chars = pair_to_list(operand)
        for item in chars:
            if not isinstance(item, Character):
                raise OperandDeduceError(f"list->string expects a list of characters, received: {operand}.")
        return String(''.join(item.value for item in chars))


@global_attr("vector->list")
class VectorToList(SingleOperandPrimitive):
    def execute_simple(self, operand: Expression) -> Expression:
        if not isinstance(operand, Vector):
            raise OperandDeduceError(f"vector->list expects a vector, received: {operand}.")
        return make_list(operand.value)


@global_attr("list->vector")
class ListToVector(SingleOperandPrimitive):
    def execute_simple(self, operand: Expression) -> Expression:
        if not isinstance(operand, Pair) and operand is not Nil:
            raise OperandDeduceError(f"list->vector expects a list, received: {operand}.")
        return Vector(pair_to_list(operand))
