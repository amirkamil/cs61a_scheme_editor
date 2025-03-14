from datamodel import Expression, Boolean, Number, Symbol, Nil, SingletonTrue, SingletonFalse, Pair, bools, \
    String, Character, Vector
from environment import global_attr
from helper import pair_to_list
from primitives import SingleOperandPrimitive
from scheme_exceptions import OperandDeduceError
from special_forms import LambdaObject, MuObject, MacroObject


@global_attr("atom?")
class IsAtom(SingleOperandPrimitive):
    def execute_simple(self, operand: Expression):
        return bools[isinstance(operand, Boolean) or isinstance(operand, Number)
                     or isinstance(operand, Symbol) or operand is Nil]


@global_attr("boolean?")
class IsBoolean(SingleOperandPrimitive):
    def execute_simple(self, operand: Expression):
        return bools[isinstance(operand, Boolean)]


@global_attr("integer?")
class IsInteger(SingleOperandPrimitive):
    def execute_simple(self, operand: Expression):
        return bools[isinstance(operand, Number) and isinstance(operand.value, int)]


@global_attr("list?")
class IsList(SingleOperandPrimitive):
    def execute_simple(self, operand: Expression):
        if isinstance(operand, Pair):
            try:
                pair_to_list(operand)
                return SingletonTrue
            except OperandDeduceError:
                return SingletonFalse
        else:
            return SingletonFalse


@global_attr("number?")
class IsNumber(SingleOperandPrimitive):
    def execute_simple(self, operand: Expression) -> Expression:
        return bools[isinstance(operand, Number)]


@global_attr("null?")
class IsNull(SingleOperandPrimitive):
    def execute_simple(self, operand: Expression) -> Expression:
        if operand is Nil:
            return SingletonTrue
        else:
            return SingletonFalse


@global_attr("pair?")
class IsPair(SingleOperandPrimitive):
    def execute_simple(self, operand: Expression) -> Expression:
        return bools[isinstance(operand, Pair)]


@global_attr("procedure?")
class IsProcedure(SingleOperandPrimitive):
    def execute_simple(self, operand: Expression):
        return bools[isinstance(operand, LambdaObject) or
                     isinstance(operand, MuObject) or
                     isinstance(operand, MacroObject)]


@global_attr("string?")
class IsString(SingleOperandPrimitive):
    def execute_simple(self, operand: Expression) -> Expression:
        return bools[isinstance(operand, String)]


@global_attr("symbol?")
class IsSymbol(SingleOperandPrimitive):
    def execute_simple(self, operand: Expression) -> Expression:
        return bools[isinstance(operand, Symbol)]


# EECS 390 additions

@global_attr("char?")
class IsChar(SingleOperandPrimitive):
    def execute_simple(self, operand: Expression) -> Expression:
        return bools[isinstance(operand, Character)]

@global_attr("vector?")
class IsVector(SingleOperandPrimitive):
    def execute_simple(self, operand: Expression) -> Expression:
        return bools[isinstance(operand, Vector)]

@global_attr("complex?")
class IsComplex(SingleOperandPrimitive):
    def execute_simple(self, operand: Expression) -> Expression:
        return bools[isinstance(operand, Number)]

@global_attr("real?")
class IsReal(SingleOperandPrimitive):
    def execute_simple(self, operand: Expression) -> Expression:
        return bools[isinstance(operand, Number)]


@global_attr("rational?")
class IsRational(SingleOperandPrimitive):
    def execute_simple(self, operand: Expression):
        return bools[isinstance(operand, Number) and isinstance(operand.value, int)]


@global_attr("input-port?")
class IsInputPort(SingleOperandPrimitive):
    def execute_simple(self, operand: Expression) -> Expression:
        return bools[0]  # ports not supported


@global_attr("output-port?")
class IsInputPort(SingleOperandPrimitive):
    def execute_simple(self, operand: Expression) -> Expression:
        return bools[0]  # ports not supported


@global_attr("eof-object?")
class IsEOFObject(SingleOperandPrimitive):
    def execute_simple(self, operand: Expression) -> Expression:
        return bools[0]  # I/O not supported
