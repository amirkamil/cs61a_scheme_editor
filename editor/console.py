from typing import List

import log
from datamodel import Character, Expression, Undefined, String
from environment import global_attr
from evaluate_apply import Frame
from helper import verify_exact_callable_length
from primitives import SingleOperandPrimitive, BuiltIn, UnsupportedSingleOperandPrimitive, UnsupportedBuiltIn
from scheme_exceptions import OperandDeduceError, UnsupportedOperationError


@global_attr("write")
class Write(BuiltIn):
    def execute_evaluated(self, operands: List[Expression], frame: Frame) -> Expression:
        if len(operands) == 2:
            raise UnsupportedOperationError("the two-argument version of write")
        verify_exact_callable_length(self, 1, len(operands))
        log.logger.out(operands[0], end="")
        return Undefined


@global_attr("display")
class Display(BuiltIn):
    def execute_evaluated(self, operands: List[Expression], frame: Frame) -> Expression:
        if len(operands) == 2:
            raise UnsupportedOperationError("the two-argument version of display")
        verify_exact_callable_length(self, 1, len(operands))
        if isinstance(operands[0], (String, Character)):
            log.logger.raw_out(operands[0].value)
        else:
            log.logger.out(operands[0], end="")
        return Undefined


@global_attr("newline")
class Newline(BuiltIn):
    def execute_evaluated(self, operands: List[Expression], frame: Frame) -> Expression:
        if len(operands) == 1:
            raise UnsupportedOperationError("the one-argument version of newline")
        verify_exact_callable_length(self, 0, len(operands))
        log.logger.raw_out("\n")
        return Undefined


# EECS 390 additions

@global_attr("write-char")
class WriteChar(BuiltIn):
    def execute_evaluated(self, operands: List[Expression], frame: Frame) -> Expression:
        if len(operands) == 2:
            raise UnsupportedOperationError("the two-argument version of write-char")
        verify_exact_callable_length(self, 1, len(operands))
        if not isinstance(operands[0], Character):
            raise OperandDeduceError(f"write-char expects a character, received: {operands[0]}.")
        log.logger.raw_out(operands[0].value)
        return Undefined


@global_attr("call-with-input-file")
class CallWithInputFile(UnsupportedBuiltIn):
    pass  # unimplemented


@global_attr("call-with-output-file")
class CallWithOutputFile(UnsupportedBuiltIn):
    pass  # unimplemented


@global_attr("current-input-port")
class CurrentInputPort(UnsupportedBuiltIn):
    pass  # unimplemented


@global_attr("current-output-port")
class CurrentOutputPort(UnsupportedBuiltIn):
    pass  # unimplemented


@global_attr("with-input-from-file")
class WithInputFromFile(UnsupportedBuiltIn):
    pass  # unimplemented


@global_attr("with-output-to-file")
class WithOutputToFile(UnsupportedBuiltIn):
    pass  # unimplemented


@global_attr("open-input-file")
class OpenInputFile(UnsupportedSingleOperandPrimitive):
    pass  # unimplemented


@global_attr("open-output-file")
class OpenOutputFile(UnsupportedSingleOperandPrimitive):
    pass  # unimplemented


@global_attr("close-input-port")
class CloseInputPort(UnsupportedSingleOperandPrimitive):
    pass  # unimplemented


@global_attr("close-output-port")
class CloseOutputPort(UnsupportedSingleOperandPrimitive):
    pass  # unimplemented


@global_attr("read")
class Read(UnsupportedBuiltIn):
    pass  # unimplemented


@global_attr("read-char")
class ReadChar(UnsupportedBuiltIn):
    pass  # unimplemented


@global_attr("peek-char")
class PeekChar(UnsupportedBuiltIn):
    pass  # unimplemented


@global_attr("char-ready?")
class IsCharReady(UnsupportedBuiltIn):
    pass  # unimplemented
