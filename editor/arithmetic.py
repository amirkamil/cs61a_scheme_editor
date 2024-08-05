import itertools
import math
from typing import List

from datamodel import Expression, Number, bools, SingletonFalse, ValueHolder, Pair, SingletonTrue, Character, String, Vector
from environment import global_attr
from evaluate_apply import Frame
from helper import assert_all_numbers, verify_exact_callable_length, verify_min_callable_length
from primitives import BuiltIn, SingleOperandPrimitive, UnsupportedBuiltIn, UnsupportedSingleOperandPrimitive


@global_attr("+")
class Add(BuiltIn):
    def execute_evaluated(self, operands: List[Expression], frame: Frame):
        assert_all_numbers(operands)
        return Number(sum(operand.value for operand in operands))


@global_attr("-")
class Subtract(BuiltIn):
    def execute_evaluated(self, operands: List[Expression], frame: Frame):
        verify_min_callable_length(self, 1, len(operands))
        assert_all_numbers(operands)
        if len(operands) == 1:
            return Number(-operands[0].value)
        return Number(operands[0].value - sum(operand.value for operand in operands[1:]))


@global_attr("*")
class Multiply(BuiltIn):
    def execute_evaluated(self, operands: List[Expression], frame: Frame):
        assert_all_numbers(operands)
        out = 1
        for operand in operands:
            out *= operand.value
        return Number(out)


@global_attr("/")
class Divide(BuiltIn):
    def execute_evaluated(self, operands: List[Expression], frame: Frame) -> Expression:
        verify_min_callable_length(self, 1, len(operands))
        assert_all_numbers(operands)
        if len(operands) == 1:
            return Number(1 / operands[0].value)

        out = operands[0].value
        for operand in operands[1:]:
            out /= operand.value
        return Number(out)


@global_attr("abs")
class Abs(SingleOperandPrimitive):
    def execute_simple(self, operand: Expression) -> Expression:
        assert_all_numbers([operand])
        return Number(abs(operand.value))


@global_attr("expt")
class Expt(BuiltIn):
    def execute_evaluated(self, operands: List[Expression], frame: Frame) -> Expression:
        verify_exact_callable_length(self, 2, len(operands))
        assert_all_numbers(operands)
        return Number(operands[0].value ** operands[1].value)


@global_attr("modulo")
class Modulo(BuiltIn):
    def execute_evaluated(self, operands: List[Expression], frame: Frame) -> Expression:
        verify_exact_callable_length(self, 2, len(operands))
        assert_all_numbers(operands)
        return Number(operands[0].value % abs(operands[1].value))


@global_attr("quotient")
class Quotient(BuiltIn):
    def execute_evaluated(self, operands: List[Expression], frame: Frame) -> Expression:
        verify_exact_callable_length(self, 2, len(operands))
        assert_all_numbers(operands)
        negate = (operands[0].value < 0) != (operands[1].value < 0)
        negate = -1 if negate else 1
        return Number(negate * operands[0].value // operands[1].value)


@global_attr("remainder")
class Remainder(BuiltIn):
    def execute_evaluated(self, operands: List[Expression], frame: Frame) -> Expression:
        verify_exact_callable_length(self, 2, len(operands))
        assert_all_numbers(operands)
        negate = (operands[0].value < 0)
        negate = -1 if negate else 1
        return Number(negate * (abs(operands[0].value) % abs(operands[1].value)))


@global_attr("=")
class NumEq(BuiltIn):
    def execute_evaluated(self, operands: List[Expression], frame: Frame) -> Expression:
        verify_min_callable_length(self, 2, len(operands))
        assert_all_numbers(operands)
        return bools[all(map(lambda pair: pair[0].value == pair[1].value,
                             itertools.pairwise(operands)))]


@global_attr("<")
class Less(BuiltIn):
    def execute_evaluated(self, operands: List[Expression], frame: Frame) -> Expression:
        verify_min_callable_length(self, 2, len(operands))
        assert_all_numbers(operands)
        return bools[all(map(lambda pair: pair[0].value < pair[1].value,
                             itertools.pairwise(operands)))]


@global_attr("<=")
class LessOrEq(BuiltIn):
    def execute_evaluated(self, operands: List[Expression], frame: Frame) -> Expression:
        verify_min_callable_length(self, 2, len(operands))
        assert_all_numbers(operands)
        return bools[all(map(lambda pair: pair[0].value <= pair[1].value,
                             itertools.pairwise(operands)))]


@global_attr(">")
class Greater(BuiltIn):
    def execute_evaluated(self, operands: List[Expression], frame: Frame) -> Expression:
        verify_min_callable_length(self, 2, len(operands))
        assert_all_numbers(operands)
        return bools[all(map(lambda pair: pair[0].value > pair[1].value,
                             itertools.pairwise(operands)))]


@global_attr(">=")
class GreaterOrEq(BuiltIn):
    def execute_evaluated(self, operands: List[Expression], frame: Frame) -> Expression:
        verify_min_callable_length(self, 2, len(operands))
        assert_all_numbers(operands)
        return bools[all(map(lambda pair: pair[0].value >= pair[1].value,
                             itertools.pairwise(operands)))]


@global_attr("even?")
class IsEven(SingleOperandPrimitive):
    def execute_simple(self, operand: Expression) -> Expression:
        assert_all_numbers([operand])
        return bools[not operand.value % 2]


@global_attr("odd?")
class IsOdd(SingleOperandPrimitive):
    def execute_simple(self, operand: Expression) -> Expression:
        assert_all_numbers([operand])
        return bools[operand.value % 2]


@global_attr("zero?")
class IsZero(SingleOperandPrimitive):
    def execute_simple(self, operand: Expression) -> Expression:
        assert_all_numbers([operand])
        return bools[operand.value == 0]


@global_attr("not")
class Not(SingleOperandPrimitive):
    def execute_simple(self, operand: Expression) -> Expression:
        return bools[operand is SingletonFalse]


@global_attr("eqv?")
class IsEqv(BuiltIn):
    def execute_evaluated(self, operands: List[Expression], frame: Frame):
        verify_exact_callable_length(self, 2, len(operands))
        if all(isinstance(x, ValueHolder) for x in operands):
            if isinstance(operands[0], String):
                return bools[operands[0] is operands[1]]
            else:
                return bools[operands[0].value == operands[1].value]
        return bools[operands[0] is operands[1]]


@global_attr("eq?")
class IsEq(BuiltIn):
    def execute_evaluated(self, operands: List[Expression], frame: Frame):
        verify_exact_callable_length(self, 2, len(operands))
        if all(isinstance(x, ValueHolder) for x in operands):
            if isinstance(operands[0], (Number, Character, String)):
                return bools[operands[0] is operands[1]]
            else:
                return bools[operands[0].value == operands[1].value]
        return bools[operands[0] is operands[1]]


@global_attr("equal?")
class IsEqual(BuiltIn):
    def execute_evaluated(self, operands: List[Expression], frame: Frame):
        verify_exact_callable_length(self, 2, len(operands))
        if all(isinstance(x, ValueHolder) for x in operands):
            return bools[operands[0].value == operands[1].value]
        elif all(isinstance(x, Pair) for x in operands):
            return bools[IsEqual().execute_evaluated([operands[0].first, operands[1].first], frame) is SingletonTrue and \
                         IsEqual().execute_evaluated([operands[0].rest, operands[1].rest], frame) is SingletonTrue]
        elif all(isinstance(x, Vector) for x in operands):
            return bools[len(operands[0].value) == len(operands[1].value) and
                         all(IsEqual().execute_evaluated([operands[0].value[i],
                                                          operands[1].value[i]], frame)
                             is SingletonTrue for i in range(len(operands[0].value)))]
        else:
            return IsEqv().execute_evaluated(operands, frame)


# EECS 390 additions

@global_attr("round")
class Round(SingleOperandPrimitive):
    def execute_simple(self, operand: Expression) -> Expression:
        assert_all_numbers([operand])
        below = math.floor(operand.value)
        above = math.ceil(operand.value)
        if above == below:
            return Number(above)
        if operand.value - below < above - operand.value:
            return Number(below)
        if above - operand.value < operand.value - below:
            return Number(above)
        return Number(below if below % 2 == 0 else above)


@global_attr("max")
class Max(BuiltIn):
    def execute_evaluated(self, operands: List[Expression], frame: Frame):
        verify_min_callable_length(self, 1, len(operands))
        assert_all_numbers(operands)
        return Number(max(operand.value for operand in operands))


@global_attr("min")
class Min(BuiltIn):
    def execute_evaluated(self, operands: List[Expression], frame: Frame):
        verify_min_callable_length(self, 1, len(operands))
        assert_all_numbers(operands)
        return Number(min(operand.value for operand in operands))


@global_attr("positive?")
class IsPositive(SingleOperandPrimitive):
    def execute_simple(self, operand: Expression) -> Expression:
        assert_all_numbers([operand])
        return bools[operand.value > 0]


@global_attr("negative?")
class IsNegative(SingleOperandPrimitive):
    def execute_simple(self, operand: Expression) -> Expression:
        assert_all_numbers([operand])
        return bools[operand.value < 0]


@global_attr("exact?")
class IsExact(SingleOperandPrimitive):
    def execute_simple(self, operand: Expression) -> Expression:
        return bools[isinstance(operand, Number) and isinstance(operand.value, int)]


@global_attr("inexact?")
class IsInexact(SingleOperandPrimitive):
    def execute_simple(self, operand: Expression) -> Expression:
        return bools[isinstance(operand, Number) and not isinstance(operand.value, int)]


@global_attr("rationalize")
class Rationalize(UnsupportedBuiltIn):
    pass  # unimplemented


@global_attr("make-rectangular")
class MakeRectangular(UnsupportedBuiltIn):
    pass  # unimplemented


@global_attr("make-polar")
class MakePolar(UnsupportedBuiltIn):
    pass  # unimplemented


@global_attr("real-part")
class RealPart(UnsupportedSingleOperandPrimitive):
    pass  # unimplemented


@global_attr("imag-part")
class ImagPart(UnsupportedSingleOperandPrimitive):
    pass  # unimplemented


@global_attr("magnitude")
class Magnitude(UnsupportedSingleOperandPrimitive):
    pass  # unimplemented


@global_attr("angle")
class Angle(UnsupportedSingleOperandPrimitive):
    pass  # unimplemented
