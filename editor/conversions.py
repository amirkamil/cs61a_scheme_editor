from environment import global_attr
from primitives import BuiltIn, SingleOperandPrimitive, UnsupportedBuiltIn, UnsupportedSingleOperandPrimitive


@global_attr("exact->inexact")
class ExactToInexact(UnsupportedSingleOperandPrimitive):
    pass  # unimplemented


@global_attr("inexact->exact")
class InexactToExact(UnsupportedSingleOperandPrimitive):
    pass  # unimplemented


@global_attr("number->string")
class NumberToString(UnsupportedBuiltIn):
    pass  # unimplemented


@global_attr("string->number")
class StringToNumber(UnsupportedBuiltIn):
    pass  # unimplemented


@global_attr("symbol->string")
class SymbolToString(UnsupportedSingleOperandPrimitive):
    pass  # unimplemented


@global_attr("string->symbol")
class StringToSymbol(UnsupportedSingleOperandPrimitive):
    pass  # unimplemented


@global_attr("char->integer")
class CharToInteger(UnsupportedSingleOperandPrimitive):
    pass  # unimplemented


@global_attr("integer->char")
class IntegerToChar(UnsupportedSingleOperandPrimitive):
    pass  # unimplemented


@global_attr("string->list")
class StringToList(UnsupportedSingleOperandPrimitive):
    pass  # unimplemented


@global_attr("list->string")
class ListToString(UnsupportedSingleOperandPrimitive):
    pass  # unimplemented


@global_attr("vector->list")
class VectorToList(UnsupportedSingleOperandPrimitive):
    pass  # unimplemented


@global_attr("list->vector")
class ListToVector(UnsupportedSingleOperandPrimitive):
    pass  # unimplemented
