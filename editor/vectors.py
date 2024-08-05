from typing import List

import log
from datamodel import Expression, Number, Vector, Undefined
from environment import global_attr, Frame
from helper import verify_exact_callable_length, verify_range_callable_length
from primitives import BuiltIn, SingleOperandPrimitive
from scheme_exceptions import IrreversibleOperationError, OperandDeduceError


@global_attr("make-vector")
class MakeVector(BuiltIn):
    def execute_evaluated(self, operands: List[Expression], frame: Frame):
        verify_range_callable_length(self, 1, 2, len(operands))
        if not isinstance(operands[0], Number) or not isinstance(operands[0].value, int):
            raise OperandDeduceError(f"make-vector expects an integer, received: {operands[0]}.")
        if operands[0].value < 0:
            raise OperandDeduceError("make-vector expects a nonnegative size, "
                                     f"received {operands[0]}.")
        return Vector([Undefined if len(operands) == 1 else operands[1]] * operands[0].value)


@global_attr("vector")
class VectorProc(BuiltIn):
    def execute_evaluated(self, operands: List[Expression], frame: Frame):
        return Vector(operands)


@global_attr("vector-length")
class VectorLength(SingleOperandPrimitive):
    def execute_simple(self, operand: Expression):
        if not isinstance(operand, Vector):
            raise OperandDeduceError(f"vector-length expects a vector, received: {operand}.")
        return Number(len(operand.value))


@global_attr("vector-ref")
class VectorRef(BuiltIn):
    def execute_evaluated(self, operands: List[Expression], frame: Frame):
        verify_exact_callable_length(self, 2, len(operands))
        if not isinstance(operands[0], Vector):
            raise OperandDeduceError(f"vector-ref expects a vector, received: {operands[0]}.")
        if not isinstance(operands[1], Number) or not isinstance(operands[1].value, int):
            raise OperandDeduceError(f"vector-ref expects an integer, received: {operands[1]}.")
        if not (0 <= operands[1].value < len(operands[0].value)):
            raise OperandDeduceError("vector-ref received out-of-range index "
                                     f"{operands[1]} for vector {operands[0]}.")
        return operands[0].value[operands[1].value]


@global_attr("vector-set!")
class VectorSet(BuiltIn):
    def execute_evaluated(self, operands: List[Expression], frame: Frame):
        verify_exact_callable_length(self, 3, len(operands))
        if log.logger.fragile:
            raise IrreversibleOperationError()
        if not isinstance(operands[0], Vector):
            raise OperandDeduceError(f"vector-set! expects a vector, received: {operands[0]}.")
        if not isinstance(operands[1], Number) or not isinstance(operands[1].value, int):
            raise OperandDeduceError(f"vector-set! expects an integer, received: {operands[1]}.")
        if not (0 <= operands[1].value < len(operands[0].value)):
            raise OperandDeduceError("vector-set! received out-of-range index "
                                     f"{operands[1]} for vector {operands[0]}.")
        operands[0].value[operands[1].value] = operands[2]
        log.logger.raw_out("WARNING: Mutation operations on pairs are not yet supported by the debugger.\n")
        return Undefined


@global_attr("vector-fill!")
class VectorFill(BuiltIn):
    def execute_evaluated(self, operands: List[Expression], frame: Frame):
        verify_exact_callable_length(self, 2, len(operands))
        if log.logger.fragile:
            raise IrreversibleOperationError()
        if not isinstance(operands[0], Vector):
            raise OperandDeduceError(f"vector-fill! expects a vector, received: {operands[0]}.")
        for i in range(len(operands[0].value)):
            operands[0].value[i] = operands[1]
        log.logger.raw_out("WARNING: Mutation operations on pairs are not yet supported by the debugger.\n")
        return Undefined
