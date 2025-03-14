from typing import List, Optional, Type

import log
from arithmetic import IsEqual
from datamodel import Expression, Symbol, Pair, SingletonTrue, SingletonFalse, Nil, Undefined, Promise, NilType, String
from environment import global_attr
from environment import special_form
from evaluate_apply import Frame, evaluate, Callable, evaluate_all, Applicable
from execution_parser import get_expression
from helper import pair_to_list, verify_exact_callable_length, verify_min_callable_length, \
    make_list, dotted_pair_to_list
from lexer import TokenBuffer
from lists import Memv
from log import Holder, VisualExpression, return_symbol, logger
from scheme_exceptions import OperandDeduceError, IrreversibleOperationError, LoadError, SchemeError, TypeMismatchError, \
    CallableResolutionError, UnsupportedOperationError


class ProcedureObject(Callable):
    evaluates_operands: bool
    lexically_scoped: bool
    name: str

    def __init__(self,
                 params: List[Symbol],
                 var_param: Optional[Symbol],
                 body: List[Expression],
                 frame: Frame,
                 name: str=None):
        super().__init__()
        self.params = params
        self.var_param = var_param
        self.body = body
        self.frame = frame
        self.name = name if name is not None else f"[{self.name}]"

    def execute(self, operands: List[Expression], frame: Frame, gui_holder: Holder, eval_operands=True):
        new_frame = Frame(self.name, self.frame if self.lexically_scoped else frame)

        if eval_operands and self.evaluates_operands:
            operands = evaluate_all(operands, frame, gui_holder.expression.children[1:])

        if self.var_param:
            verify_min_callable_length(self, len(self.params), len(operands))
        else:
            verify_exact_callable_length(self, len(self.params), len(operands))

        if len(self.body) > 1:
            body = [Pair(Symbol("begin"), make_list(self.body))]
        else:
            body = self.body

        for param, value in zip(self.params, operands):
            new_frame.assign(param, value)

        if self.var_param:
            new_frame.assign(self.var_param, make_list(operands[len(self.params):]))

        out = None
        gui_holder.expression.set_entries(
            [VisualExpression(expr, gui_holder.expression.display_value) for expr in body])

        gui_holder.apply()

        for i, expression in enumerate(body):
            out = evaluate(expression,
                           new_frame,
                           gui_holder.expression.children[i],
                           self.evaluates_operands and i == len(body) - 1,
                           log_stack=len(self.body) == 1)

        new_frame.assign(return_symbol, out)

        if not self.evaluates_operands:
            gui_holder.expression.set_entries([VisualExpression(out, gui_holder.expression.display_value)])
            out = evaluate(out, frame, gui_holder.expression.children[i], True)

        return out

    def __repr__(self):
        if self.var_param is not None:
            if logger.dotted:
                varparams = " . " + self.var_param.value
            else:
                varparams = " (variadic " + self.var_param.value + ")"
        else:
            varparams = ""
        params = " ".join(map(repr, self.params))
        if self.params:
            params = " " + params
        return f"({self.name}{params}{varparams}) [parent = {self.frame.id}]"

    def __str__(self):
        return f"#[{self.name}]"


class LambdaObject(ProcedureObject, Applicable):
    evaluates_operands = True
    lexically_scoped = True
    name = "lambda"


class MuObject(ProcedureObject, Applicable):
    evaluates_operands = True
    lexically_scoped = False
    name = "mu"


class MacroObject(ProcedureObject, Callable):
    evaluates_operands = False
    lexically_scoped = True
    name = "macro"


class ProcedureBuilder(Callable):
    procedure: Type[ProcedureObject]

    def execute(self, operands: List[Expression], frame: Frame, gui_holder: Holder, name: str = None):
        verify_min_callable_length(self, 2, len(operands))
        params = operands[0]
        if not logger.dotted and not isinstance(params, (Pair, NilType)):
            raise OperandDeduceError(f"Expected Pair as parameter list, received {params}.")
        params, var_param = dotted_pair_to_list(params)
        param_set = set()
        for i, param in enumerate(params):
            if (logger.dotted or i != len(params) - 1) and not isinstance(param, Symbol):
                raise OperandDeduceError(f"Expected Symbol in parameter list, received {param}.")
            if isinstance(param, Pair):
                param_vals = pair_to_list(param)
                if len(param_vals) != 2 or \
                        not isinstance(param_vals[0], Symbol) or \
                        not isinstance(param_vals[1], Symbol) or \
                        param_vals[0].value != "variadic":
                    raise OperandDeduceError(f"Each member of a parameter list must be a Symbol or a variadic "
                                             f"parameter, not {param}.")
                param = var_param = param_vals[1]
                params.pop()
            if param.value in param_set:
                raise OperandDeduceError(f"Duplicate name in parameter list: {param}.")
            param_set.add(param.value)

        name_arg = (name,) if name else ()
        return self.procedure(params, var_param, operands[1:], frame, *name_arg)


@special_form("lambda")
class Lambda(ProcedureBuilder):
    procedure = LambdaObject


@special_form("mu")
class Mu(ProcedureBuilder):
    procedure = MuObject


class Macro(ProcedureBuilder):
    procedure = MacroObject


@special_form("define-macro")
class DefineMacro(Callable):
    def execute(self, operands: List[Expression], frame: Frame, gui_holder: Holder):
        verify_min_callable_length(self, 2, len(operands))
        params = operands[0]
        if not isinstance(params, Pair):
            raise OperandDeduceError(f"Expected a Pair, not {params}, as the first operand of define-macro.")
        name = params.first
        operands[0] = params.rest
        if not isinstance(name, Symbol):
            raise OperandDeduceError(f"Expected a Symbol, not {name}.")
        frame.assign(name, Macro().execute(operands, frame, gui_holder, name.value))
        return name


@special_form("define")
class Define(Callable):
    def execute(self, operands: List[Expression], frame: Frame, gui_holder: Holder):
        verify_min_callable_length(self, 2, len(operands))
        params = operands[0]
        if isinstance(params, Symbol):
            verify_exact_callable_length(self, 2, len(operands))
            frame.assign(params, evaluate(operands[1], frame, gui_holder.expression.children[2]))
            return params
        elif isinstance(params, Pair):
            name = params.first
            operands[0] = params.rest
            if not isinstance(name, Symbol):
                raise OperandDeduceError(f"Expected a Symbol, not {name}.")
            frame.assign(name, Lambda().execute(operands, frame, gui_holder, name.value))
            return name
        else:
            raise OperandDeduceError(f"Expected a Pair, not {params}, as the first operand of define-macro.")


@special_form("set!")
class Set(Callable):
    def execute(self, operands: List[Expression], frame: Frame, gui_holder: Holder):
        verify_exact_callable_length(self, 2, len(operands))
        name = operands[0]
        if not isinstance(name, Symbol):
            raise OperandDeduceError(f"Expected a Symbol, not {name}, as the first operand of set!")
        frame.mutate(name, evaluate(operands[1], frame, gui_holder.expression.children[2]))
        return Undefined


@special_form("begin")
class Begin(Callable):
    def execute(self, operands: List[Expression], frame: Frame, gui_holder: Holder):
        verify_min_callable_length(self, 1, len(operands))
        out = None
        for i, (operand, holder) in enumerate(zip(operands, gui_holder.expression.children[1:])):
            out = evaluate(operand, frame, holder, i == len(operands) - 1)
        return out


@special_form("if")
class If(Callable):
    def execute(self, operands: List[Expression], frame: Frame, gui_holder: Holder):
        verify_min_callable_length(self, 2, len(operands))
        if len(operands) > 3:
            verify_exact_callable_length(self, 3, len(operands))
        if evaluate(operands[0], frame, gui_holder.expression.children[1]) is SingletonFalse:
            if len(operands) == 2:
                return Undefined
            else:
                return evaluate(operands[2], frame, gui_holder.expression.children[3], True)
        else:
            return evaluate(operands[1], frame, gui_holder.expression.children[2], True)


@special_form("quote")
class Quote(Callable):
    def execute(self, operands: List[Expression], frame: Frame, gui_holder: Holder):
        verify_exact_callable_length(self, 1, len(operands))
        return operands[0]


@global_attr("eval")
class Eval(Applicable):
    def execute(self, operands: List[Expression], frame: Frame, gui_holder: Holder, eval_operands=True):
        if len(operands) == 2:
            raise UnsupportedOperationError("the standard eval procedure; it implements "
                                            "a non-standard version that takes in just "
                                            "an expression without an environment")
        verify_exact_callable_length(self, 1, len(operands))
        if eval_operands:
            operand = evaluate(operands[0], frame, gui_holder.expression.children[1])
        else:
            operand = operands[0]
        gui_holder.expression.set_entries([VisualExpression(operand, gui_holder.expression.display_value)])
        gui_holder.apply()
        return evaluate(operand, frame, gui_holder.expression.children[0], True)


@global_attr("apply")
class Apply(Applicable):
    def execute(self, operands: List[Expression], frame: Frame, gui_holder: Holder, eval_operands=True):
        verify_min_callable_length(self, 2, len(operands))
        if eval_operands:
            operands = evaluate_all(operands, frame, gui_holder.expression.children[1:])
        func, args_mid, last_arg = operands[0], operands[1:-1], operands[-1]
        if not isinstance(func, Applicable):
            raise OperandDeduceError(f"Unable to apply {func}.")
        if not isinstance(last_arg, Pair) and last_arg is not Nil:
            raise OperandDeduceError(f"Expected last argument of apply to be a list, not {last_arg}.")
        args = args_mid + pair_to_list(last_arg)
        gui_holder.expression.set_entries([VisualExpression(Pair(func, make_list(args)), gui_holder.expression.display_value)])
        gui_holder.expression.children[0].expression.children = []
        gui_holder.apply()
        return func.execute(args, frame, gui_holder.expression.children[0], False)


@special_form("cond")
class Cond(Callable):
    def execute(self, operands: List[Expression], frame: Frame, gui_holder: Holder):
        verify_min_callable_length(self, 1, len(operands))
        for cond_i, cond in enumerate(operands):
            if not isinstance(cond, Pair):
                raise OperandDeduceError(f"Unable to evaluate clause of cond, as {cond} is not a Pair.")
            expanded = pair_to_list(cond)
            cond_holder = gui_holder.expression.children[cond_i + 1]
            eval_condition = SingletonTrue
            if not isinstance(expanded[0], Symbol) or expanded[0].value != "else":
                eval_condition = evaluate(expanded[0], frame, cond_holder.expression.children[0])
            elif cond_i != len(operands) - 1:
                raise OperandDeduceError(f"Else clause can only be the last clause of cond.")
            elif len(expanded) < 2:
                raise OperandDeduceError(f"Else clause needs to have an expression.")
            if (isinstance(expanded[0], Symbol) and expanded[0].value == "else") \
                    or eval_condition is not SingletonFalse:
                out = eval_condition
                for i, expr in enumerate(expanded[1:]):
                    out = evaluate(expr, frame, cond_holder.expression.children[i + 1], i == len(expanded) - 2)
                return out
        return Undefined


@special_form("and")
class And(Callable):
    def execute(self, operands: List[Expression], frame: Frame, gui_holder: Holder):
        value = None
        for i, expr in enumerate(operands):
            value = evaluate(expr, frame, gui_holder.expression.children[i + 1], i == len(operands) - 1)
            if value is SingletonFalse:
                return SingletonFalse
        return value if operands else SingletonTrue


@special_form("or")
class Or(Callable):
    def execute(self, operands: List[Expression], frame: Frame, gui_holder: Holder):
        for i, expr in enumerate(operands):
            value = evaluate(expr, frame, gui_holder.expression.children[i + 1], i == len(operands) - 1)
            if value is not SingletonFalse:
                return value
        return SingletonFalse


def _let_impl(receiver, kind, operands, frame, gui_holder, nest_frames=False):
    verify_min_callable_length(receiver, 2, len(operands))

    bindings = operands[0]
    if not isinstance(bindings, Pair) and bindings is not Nil:
        raise OperandDeduceError(f"Expected first argument of {kind} to be a Pair, not {bindings}.")

    old_frame = frame
    new_frame = Frame(f"anonymous {kind}", old_frame)

    bindings_holder = gui_holder.expression.children[1]

    bindings = pair_to_list(bindings)
    name_set = set()

    for i, binding in enumerate(bindings):
        if not isinstance(binding, Pair):
            raise OperandDeduceError(f"Expected binding to be a Pair, not {binding}.")
        binding_holder = bindings_holder.expression.children[i]
        binding = pair_to_list(binding)
        if len(binding) != 2:
            raise OperandDeduceError(f"Expected binding to be of length 2, not {len(binding)}.")
        name, expr = binding
        if not isinstance(name, Symbol):
            raise OperandDeduceError(f"Expected first element of binding to be a Symbol, not {name}.")
        if name.value in name_set:
            raise OperandDeduceError(f"Duplicate binding name in {kind}: {name}.")
        name_set.add(name.value)
        new_frame.assign(name, evaluate(expr, old_frame, binding_holder.expression.children[1]))
        if nest_frames and i < len(bindings) - 1:
            old_frame = new_frame
            new_frame = Frame(f"anonymous {kind}", old_frame)

    value = None

    for i, (operand, holder) in enumerate(zip(operands[1:], gui_holder.expression.children[2:])):
        value = evaluate(operand, new_frame, holder, i == len(operands) - 2)

    new_frame.assign(return_symbol, value)
    return value


@special_form("let")
class Let(Callable):
    def execute(self, operands: List[Expression], frame: Frame, gui_holder: Holder):
        return _let_impl(self, "let", operands, frame, gui_holder, False)


@special_form("variadic")
class Variadic(Callable):
    def execute(self, operands: List[Expression], frame: Frame, gui_holder: Holder):
        raise CallableResolutionError("Variadic type parameter must be within a parameter list.")


@special_form("unquote")
class Unquote(Callable):
    def execute(self, operands: List[Expression], frame: Frame, gui_holder: Holder):
        raise CallableResolutionError("Cannot evaluate unquote outside quasiquote.")


@special_form("unquote-splicing")
class UnquoteSplicing(Callable):
    def execute(self, operands: List[Expression], frame: Frame, gui_holder: Holder):
        raise CallableResolutionError("Cannot evaluate unquote-splicing outside quasiquote.")


@special_form("quasiquote")
class Quasiquote(Callable):
    def execute(self, operands: List[Expression], frame: Frame, gui_holder: Holder):
        verify_exact_callable_length(self, 1, len(operands))
        return Quasiquote.quasiquote_evaluate(operands[0], frame, gui_holder.expression.children[1])

    @classmethod
    def quasiquote_evaluate(cls, expr: Expression, frame: Frame, gui_holder: Holder, splicing=False):
        is_well_formed = False

        if isinstance(expr, Pair):
            try:
                lst = pair_to_list(expr)
            except OperandDeduceError:
                pass
            else:
                is_well_formed = not any(map(
                    lambda x: isinstance(x, Symbol) and x.value in ["unquote", "quasiquote", "unquote-splicing"], lst))

        visual_expression = gui_holder.expression
        if not is_well_formed:
            visual_expression.children[2:] = []

        if isinstance(expr, Pair):
            if isinstance(expr.first, Symbol) and expr.first.value in ("unquote", "unquote-splicing"):
                if expr.first.value == "unquote-splicing" and not splicing:
                    raise OperandDeduceError("Unquote-splicing must be in list template.")
                gui_holder.evaluate()
                verify_exact_callable_length(expr.first, 1, len(pair_to_list(expr)) - 1)
                out = evaluate(expr.rest.first, frame, visual_expression.children[1])
                visual_expression.value = out
                gui_holder.complete()
                return out
            elif isinstance(expr.first, Symbol) and expr.first.value == "quasiquote":
                visual_expression.value = expr
                gui_holder.complete()
                return expr
            else:
                if is_well_formed:
                    out = []
                    for sub_expr, holder in zip(pair_to_list(expr), visual_expression.children):
                        splicing = isinstance(sub_expr, Pair) and isinstance(sub_expr.first, Symbol) \
                                and sub_expr.first.value == "unquote-splicing"
                        evaluated = Quasiquote.quasiquote_evaluate(sub_expr, frame, holder, splicing)
                        if splicing:
                            if not isinstance(evaluated, (Pair, NilType)):
                                raise TypeMismatchError(f"Can only splice lists, not {evaluated}.")
                            out.extend(pair_to_list(evaluated))
                        else:
                            out.append(evaluated)
                    out = make_list(out)
                else:
                    if not logger.dotted:
                        raise OperandDeduceError(f"{expr} is an ill-formed quasiquotation.")
                    out = Pair(Quasiquote.quasiquote_evaluate(expr.first, frame, visual_expression.children[0]),
                               Quasiquote.quasiquote_evaluate(expr.rest, frame, visual_expression.children[1]))
                visual_expression.value = out
                gui_holder.complete()
                return out
        else:
            visual_expression.value = expr
            gui_holder.complete()
            return expr


@global_attr("load")
class Load(Applicable):
    def execute(self, operands: List[Expression], frame: Frame, gui_holder: Holder, eval_operands=True):
        verify_exact_callable_length(self, 1, len(operands))
        if eval_operands:
            operands = evaluate_all(operands, frame, gui_holder.expression.children[1:])
        if not isinstance(operands[0], Symbol):
            raise OperandDeduceError(f"Load expected a Symbol, received {operands[0]}.")
        if logger.fragile:
            raise IrreversibleOperationError()
        try:
            with open(f"{operands[0].value}.scm") as file:
                code = "(begin-noexcept" + "\n".join(file.readlines()) + "\n)"
                buffer = TokenBuffer([code])
                expr = get_expression(buffer)
                gui_holder.expression.set_entries([VisualExpression(expr, gui_holder.expression.display_value)])
                gui_holder.apply()
                return evaluate(expr, frame, gui_holder.expression.children[0], True)
        except OSError as e:
            raise LoadError(e)


@global_attr("load-all")
class LoadAll(Applicable):
    def execute(self, operands: List[Expression], frame: Frame, gui_holder: Holder, eval_operands=True):
        verify_exact_callable_length(self, 1, len(operands))
        if eval_operands:
            operands = evaluate_all(operands, frame, gui_holder.expression.children[1:])
        if not isinstance(operands[0], String):
            raise OperandDeduceError(f"Load expected a String, received {operands[0]}.")
        if logger.fragile:
            raise IrreversibleOperationError()
        from os import listdir
        from os.path import join
        directory = operands[0].value
        try:
            targets = sorted(listdir(directory))
            targets = [join(directory, target) for target in targets if target.endswith(".scm")]
            exprs = [make_list([Symbol("load"), make_list([Symbol("quote"), Symbol(x[:-4])])]) for x in targets]
            equiv = make_list([Symbol("begin-noexcept")] + exprs)
            gui_holder.expression.set_entries([equiv])
            gui_holder.apply()
            return evaluate(equiv, frame, gui_holder.expression.children[0], True)
        except Exception as e:
            raise SchemeError(e)


@special_form("begin-noexcept")
class BeginNoExcept(Callable):
    def execute(self, operands: List[Expression], frame: Frame, gui_holder: Holder):
        out = Undefined
        for i, (operand, holder) in enumerate(zip(operands, gui_holder.expression.children[1:])):
            try:
                out = evaluate(operand, frame, holder, i == len(operands) - 1)
            except (SchemeError, RecursionError, ValueError, ZeroDivisionError) as e:
                logger.raw_out("LoadError: " + str(e) + "\n")
        return out


@special_form("delay")
class Delay(Callable):
    def execute(self, operands: List[Expression], frame: Frame, gui_holder: Holder):
        verify_exact_callable_length(self, 1, len(operands))
        return Promise(operands[0], frame)


@global_attr("force")
class Force(Applicable):
    def execute(self, operands: List[Expression], frame: Frame, gui_holder: Holder, eval_operands=True):
        verify_exact_callable_length(self, 1, len(operands))
        operand = operands[0]
        if eval_operands:
            operand = evaluate_all(operands, frame, gui_holder.expression.children[1:])[0]
        if not isinstance(operand, Promise):
            raise OperandDeduceError(f"Force expected a Promise, received {operand}")
        if operand.forced:
            return operand.expr
        if logger.fragile:
            raise IrreversibleOperationError()
        gui_holder.expression.set_entries([VisualExpression(operand.expr, gui_holder.expression.display_value)])
        gui_holder.apply()
        evaluated = evaluate(operand.expr, operand.frame, gui_holder.expression.children[0])
        if not logger.dotted and not isinstance(evaluated, (Pair, NilType)):
            raise TypeMismatchError(
                f"Unable to force a Promise evaluating to {operand.expr}, expected another Pair or Nil")
        operand.expr = evaluated
        operand.force()
        return operand.expr


@special_form("expect")
class Expect(Callable):
    def execute(self, operands: List[Expression], frame: Frame, gui_holder: Holder):
        verify_exact_callable_length(self, 2, len(operands))
        case = operands[0]
        operands[0] = evaluate(operands[0], frame, gui_holder.expression.children[1])
        if not IsEqual().execute_evaluated(operands, frame).value:
            log.logger.raw_out(f"Evaluated {case}, expected {operands[1]}, got {operands[0]}.\n")
        else:
            log.logger.raw_out(f"Evaluated {case}, got {operands[0]}, as expected.\n")
        return Undefined


@global_attr("error")
class Error(Applicable):
    def execute(self, operands: List[Expression], frame: Frame, gui_holder: Holder, eval_operands=True):
        verify_exact_callable_length(self, 1, len(operands))
        if eval_operands:
            operands = evaluate_all(operands, frame, gui_holder.expression.children[1:])
        raise SchemeError(operands[0])


# EECS 390 additions

@special_form("let*")
class LetStar(Callable):
    def execute(self, operands: List[Expression], frame: Frame, gui_holder: Holder):
        return _let_impl(self, "let*", operands, frame, gui_holder, True)


@special_form("case")
class Case(Callable):
    def execute(self, operands: List[Expression], frame: Frame, gui_holder: Holder):
        verify_min_callable_length(self, 2, len(operands))
        key = evaluate(operands[0], frame, gui_holder.expression.children[1])
        for case_i, case in enumerate(operands[1:]):
            if not isinstance(case, Pair):
                raise OperandDeduceError(f"Unable to evaluate clause of case, as {case} is not a Pair.")
            expanded = pair_to_list(case)
            case_holder = gui_holder.expression.children[case_i + 2]  # skip key
            eval_condition = SingletonTrue
            if (not isinstance(expanded[0], Symbol) or expanded[0].value != "else") \
                   and isinstance(expanded[0], Pair):
                eval_condition = Memv().execute_evaluated([key, expanded[0]], frame)
            elif not isinstance(expanded[0], Symbol) or expanded[0].value != "else":
                raise OperandDeduceError(f"Case clause expected list, received {expanded[0]}")
            elif case_i != len(operands) - 2:  # exclude key from count
                raise OperandDeduceError(f"Else clause can only be the last clause of case.")
            if len(expanded) < 2:
                raise OperandDeduceError(f"Case clause needs to have a length of at least two, received {case}.")
            if (isinstance(expanded[0], Symbol) and expanded[0].value == "else") \
                    or eval_condition is not SingletonFalse:
                out = eval_condition
                for i, expr in enumerate(expanded[1:]):
                    out = evaluate(expr, frame, case_holder.expression.children[i + 1], i == len(expanded) - 2)
                return out
        return Undefined


class UnsupportedCallable(Callable):
    def execute(self, operands: List[Expression], frame: Frame, gui_holder: Holder):
        raise UnsupportedOperationError(self)


@special_form("letrec")
class Letrec(UnsupportedCallable):
    pass  # unimplemented


@special_form("do")
class Do(UnsupportedCallable):
    pass  # unimplemented


@special_form("let-syntax")
class LetSyntax(UnsupportedCallable):
    pass  # unimplemented


@special_form("letrec-syntax")
class LetrecSyntax(UnsupportedCallable):
    pass  # unimplemented


@special_form("syntax-rules")
class SyntaxRules(UnsupportedCallable):
    pass  # unimplemented


@special_form("define-syntax")
class DefineSyntax(UnsupportedCallable):
    pass  # unimplemented


@global_attr("for-each")
class ForEach(UnsupportedCallable):
    pass  # unimplemented


@global_attr("call-with-current-continuation")
@global_attr("call/cc")
class CallCC(UnsupportedCallable):
    pass  # unimplemented


@global_attr("values")
class Values(UnsupportedCallable):
    pass  # unimplemented


@global_attr("call-with-values")
class CallWithValues(UnsupportedCallable):
    pass  # unimplemented


@global_attr("dynamic-wind")
class DynamicWind(UnsupportedCallable):
    pass  # unimplemented


@global_attr("scheme-report-environment")
class SchemeReportEnvironment(UnsupportedCallable):
    pass  # unimplemented


@global_attr("null-environment")
class NullEnvironment(UnsupportedCallable):
    pass  # unimplemented


@global_attr("interaction-environment")
class InteractionEnvironment(UnsupportedCallable):
    pass  # unimplemented


@global_attr("transcript-on")
class TranscriptOn(UnsupportedCallable):
    pass  # unimplemented


@global_attr("transcript-off")
class TranscriptOff(UnsupportedCallable):
    pass  # unimplemented
