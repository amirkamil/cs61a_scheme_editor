import itertools
from typing import List

import log
import arithmetic
from datamodel import Expression, Pair, Nil, Number, bools, Undefined, NilType, Promise, SingletonTrue
from environment import global_attr
from evaluate_apply import Frame
from helper import pair_to_list, make_list, verify_exact_callable_length
from primitives import SingleOperandPrimitive, BuiltIn
from scheme_exceptions import OperandDeduceError, IrreversibleOperationError


@global_attr("append")
class Append(BuiltIn):
    def execute_evaluated(self, operands: List[Expression], frame: Frame) -> Expression:
        if len(operands) == 0:
            return Nil
        exprs = []
        for operand in operands[:-1]:
            if not isinstance(operand, Pair) and operand is not Nil:
                raise OperandDeduceError(f"Expected operand to be valid list, not {operand}")
            exprs.extend(pair_to_list(operand))
        out = operands[-1]
        for expr in reversed(exprs):
            out = Pair(expr, out)
        return out



@global_attr("car")
class Car(SingleOperandPrimitive):
    def execute_simple(self, operand: Expression) -> Expression:
        if isinstance(operand, Pair):
            return operand.first
        else:
            raise OperandDeduceError(f"Unable to extract first element, as {operand} is not a Pair.")


@global_attr("cdr")
class Cdr(SingleOperandPrimitive):
    def execute_simple(self, operand: Expression) -> Expression:
        if isinstance(operand, Pair):
            return operand.rest
        else:
            raise OperandDeduceError(f"Unable to extract second element, as {operand} is not a Pair.")


@global_attr("cons")
class Cons(BuiltIn):
    def execute_evaluated(self, operands: List[Expression], frame: Frame) -> Expression:
        verify_exact_callable_length(self, 2, len(operands))
        return Pair(operands[0], operands[1])


@global_attr("length")
class Length(SingleOperandPrimitive):
    def execute_simple(self, operand: Expression) -> Expression:
        if not isinstance(operand, Pair) and operand is not Nil:
            raise OperandDeduceError(f"Unable to calculate length, as {operand} is not a valid list.")
        return Number(len(pair_to_list(operand)))


# @global_attr("map")
# class Map(BuiltIn):
#     def execute_evaluated(self, operands: List[Expression], frame: Frame) -> Expression:
#         verify_exact_callable_length(self, 2, len(operands))
#
#         func, lst = operands
#
#         if not isinstance(func, Callable):
#             raise OperandDeduceError(f"Unable to call {operands[0]}.")
#
#         if not isinstance(lst, Pair):
#             raise OperandDeduceError(f"Unable to iterate, since {operands[1]} is not a valid list.")
#
#         lst = pair_to_list(lst)
#         out = [func.execute([x], frame, dummy_holder) for x in lst]
#
#         return make_list(out)


@global_attr("list")
class MakeList(BuiltIn):
    def execute_evaluated(self, operands: List[Expression], frame: Frame) -> Expression:
        return make_list(operands)


@global_attr("set-car!")
class SetCar(BuiltIn):
    def execute_evaluated(self, operands: List[Expression], frame: Frame) -> Expression:
        verify_exact_callable_length(self, 2, len(operands))
        if log.logger.fragile:
            raise IrreversibleOperationError()
        pair, val = operands
        if not isinstance(pair, Pair):
            raise OperandDeduceError(f"set-car! expected a Pair, received {pair}.")
        pair.first = val
        log.logger.raw_out("WARNING: Mutation operations on pairs are not yet supported by the debugger.")
        return Undefined


@global_attr("set-cdr!")
class SetCdr(BuiltIn):
        def execute_evaluated(self, operands: List[Expression], frame: Frame) -> Expression:
            verify_exact_callable_length(self, 2, len(operands))
            if log.logger.fragile:
                raise IrreversibleOperationError()
            pair, val = operands
            if not isinstance(pair, Pair):
                raise OperandDeduceError(f"set-cdr! expected a Pair, received {pair}.")
            if not isinstance(val, (Pair, Promise, NilType)):
                raise OperandDeduceError(f"Unable to assign {val} to cdr, expected a Pair, Nil, or Promise.")
            pair.rest = val
            log.logger.raw_out("WARNING: Mutation operations on pairs are not yet supported by the debugger.")
            return Undefined


# EECS 390 additions

@global_attr("reverse")
class Reverse(SingleOperandPrimitive):
    def execute_simple(self, operand: Expression) -> Expression:
        if not isinstance(operand, Pair) and operand is not Nil:
            raise OperandDeduceError(f"Unable to reverse, as {operand} is not a valid list.")
        elements = pair_to_list(operand)
        out = Nil
        for expr in elements:
            out = Pair(expr, out)
        return out


@global_attr("memq")
class Memq(BuiltIn):
    def execute_evaluated(self, operands: List[Expression], frame: Frame) -> Expression:
        verify_exact_callable_length(self, 2, len(operands))
        value, sequence = operands
        if not isinstance(sequence, Pair) and sequence is not Nil:
            raise OperandDeduceError(f"memq expected a list as the second argument, received {sequence}.")
        for item in pair_to_list(sequence):
            if arithmetic.IsEq().execute_evaluated([value, item], frame) is SingletonTrue:
                return item
        return bools[0]


@global_attr("memv")
class Memv(BuiltIn):
    def execute_evaluated(self, operands: List[Expression], frame: Frame) -> Expression:
        verify_exact_callable_length(self, 2, len(operands))
        value, sequence = operands
        if not isinstance(sequence, Pair) and sequence is not Nil:
            raise OperandDeduceError(f"memv expected a list as the second argument, received {sequence}.")
        for item in pair_to_list(sequence):
            if arithmetic.IsEqv().execute_evaluated([value, item], frame) is SingletonTrue:
                return item
        return bools[0]


@global_attr("member")
class Member(BuiltIn):
    def execute_evaluated(self, operands: List[Expression], frame: Frame) -> Expression:
        verify_exact_callable_length(self, 2, len(operands))
        value, sequence = operands
        if not isinstance(sequence, Pair) and sequence is not Nil:
            raise OperandDeduceError(f"member expected a list as the second argument, received {sequence}.")
        for item in pair_to_list(sequence):
            if arithmetic.IsEqual().execute_evaluated([value, item], frame) is SingletonTrue:
                return item
        return bools[0]


@global_attr("assq")
class Assq(BuiltIn):
    def execute_evaluated(self, operands: List[Expression], frame: Frame) -> Expression:
        verify_exact_callable_length(self, 2, len(operands))
        value, sequence = operands
        if not isinstance(sequence, Pair) and sequence is not Nil:
            raise OperandDeduceError(f"assq expected a list as the second argument, received {sequence}.")
        for item in pair_to_list(sequence):
            if not isinstance(item, Pair):
                raise OperandDeduceError(f"association list expected a pair, received {item}.")
            if arithmetic.IsEq().execute_evaluated([value, item.first], frame) is SingletonTrue:
                return item
        return bools[0]


@global_attr("assv")
class Assv(BuiltIn):
    def execute_evaluated(self, operands: List[Expression], frame: Frame) -> Expression:
        verify_exact_callable_length(self, 2, len(operands))
        value, sequence = operands
        if not isinstance(sequence, Pair) and sequence is not Nil:
            raise OperandDeduceError(f"assv expected a list as the second argument, received {sequence}.")
        for item in pair_to_list(sequence):
            if not isinstance(item, Pair):
                raise OperandDeduceError(f"association list expected a pair, received {item}.")
            if arithmetic.IsEqv().execute_evaluated([value, item.first], frame) is SingletonTrue:
                return item
        return bools[0]


@global_attr("assoc")
class Assoc(BuiltIn):
    def execute_evaluated(self, operands: List[Expression], frame: Frame) -> Expression:
        verify_exact_callable_length(self, 2, len(operands))
        value, sequence = operands
        if not isinstance(sequence, Pair) and sequence is not Nil:
            raise OperandDeduceError(f"assoc expected a list as the second argument, received {sequence}.")
        for item in pair_to_list(sequence):
            if not isinstance(item, Pair):
                raise OperandDeduceError(f"association list expected a pair, received {item}.")
            if arithmetic.IsEqual().execute_evaluated([value, item.first], frame) is SingletonTrue:
                return item
        return bools[0]


# generate pair accessor combinations
def make_combinator(seq):
    class_name = f"C{''.join(seq)}r"
    func_name = f"c{''.join(seq)}r"

    @global_attr(func_name)
    class Comb(SingleOperandPrimitive):
        __name__ = class_name
        __qualname__ = class_name

        def execute_simple(self, operand: Expression) -> Expression:
            for op in reversed(seq):
                accessor = Car() if op == 'a' else Cdr()
                operand = accessor.execute_simple(operand)
            return operand

    globals()[class_name] = Comb


for i in range(2, 5):
    for seq in itertools.product(("a", "d"), repeat=i):
        make_combinator(seq)
