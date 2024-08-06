## Overview and Terminology
### Expressions and Environments

Scheme works by evaluating **expressions** in **environments**. Every expression
evaluates to a **value**. Some expressions are **self-evaluating**, which means
they are both an expression and a value, and that it evaluates to itself.

A **frame** is a mapping from symbols (names) to values, as well as an optional
parent frame. The current environment refers to the current frame, as well as a
chain of parent frames up to the **global frame** (which has no parent). When
looking up a symbol in an environment, Scheme first checks the current frame and
returns the corresponding value if it exists. If it doesn't, it repeats this
process on each subsequent parent frame, until either the symbol is found, or
there are no more parent frames to check.

### Atomic Expressions

There are several **atomic** or **primitive** expressions. Numbers, booleans,
strings, and the empty list (`nil`) are all both atomic and self-evaluating.
Symbols are atomic, but are not self-evaluating (they instead evaluate to a
value that was previously bound to it in the environment).

### Call Expressions

The Scheme expressions that are not atomic are called **combinations**, and
consist of one or more **subexpressions** between parentheses. Most forms are
evaluated as **call expressions**, which has three evaluation steps:

1. Evaluate the first subexpression (the operator), which must evaluate to a
**procedure** (see below).
2. Evaluate the remaining subexpressions (the operands) in order.
3. Apply the procedure from step 1 to the evaluated operands (**arguments**) from
step 2.

These steps mirror those in Python and other languages.

### Special Forms

However, not all combinations are call expressions. Some are **special forms**.
The interpreter maintains a set of particular symbols (sometimes called
**keywords**) that signal that a combination is a special form when they are the
first subexpression. Each special form has it's own procedure for which operands
to evaluate and how (described below). The interpreter always checks the first
subexpression of a combination first. If it matches one of the keywords, the
corresponding special form is used. Otherwise, the combination is evaluated as a
call expression.

### Symbolic Programming

Scheme's core data type is the **list**, built out of pairs as described below.
Scheme code is actually built out of these lists. This means that the code
`(+ 1 2)` is constructed as a list of the `+` symbol, the number 1, and the
number 2, which is then evaluated as a call expression.

Since lists are normally evaluated as combinations, we need a special form to
get the actual, unevaluated list. `quote` is a special form that takes a single
operand expression and returns it, unevaluated. Therefore, `(quote (+ 1 2))`
returns the actual list of the symbol `+`, the number 1, and the number 2,
rather than evaluating the expression to get the number 3. This also works for
symbols. `a` is looked up in the current environment to get the corresponding
value, while `(quote a)` evaluates to the literal symbol `a`.

Because `quote` is so commonly used in Scheme, the language has a shorthand way
of writing it: just put a single quote in front of the expression you want to
leave unevaluated. `'(+ 1 2)` and `'a` are equivalent to `(quote (+ 1 2))` and
`(quote a)`, respectively.

### Miscellaneous

Like R5RS, MiScheme is entirely case-insensitive (aside from strings
and characters). This specification will use lowercase characters in
symbols, but the corresponding uppercase characters may be used
interchangeably.

## Types of Values

### Numbers

Numbers are built on top of Python's number types and can thus support a
combination of arbitrarily-large integers and double-precision floating points.

The web interpreter attempts to replicate this when possible, though may deviate
from Python-based versions due to the different host language and the need to
work-around the quirks of JavaScript when running in a browser.

Any valid real number literal in the interpreter's host language should be
properly read. You should not count on consistent results when floating point
numbers are involved in any calculation or on any numbers with true division.

### Booleans

There are two boolean values: `#t` and `#f`. Scheme booleans may be input either
as their canonical `#t` or `#f` or as the words `true` or `false`.

Any expression may be evaluated in a boolean context, but `#f` is the only value
that is false. All other values are treated as true in a boolean context.

Some interpreters prior to Spring 2018 displayed the words `true` and `false`
when booleans were output, but this should not longer be the case in any
interpreter released/updated since then.

### Symbols

Symbols are used as identifiers in Scheme. Valid symbols consist of some
combination of alphanumeric characters and/or the following special characters:

    !$%&*/:<=>?@^_~+-.

All symbols should be internally stored with lowercase letters. Symbols must not
form a valid integer or floating-point number.

### Strings

Strings can be entered into the intepreter as a sequence of characters
inside double quotes, with certain characters, such as line breaks and
double quotes escaped. As a general rule, if a piece of text would be
valid as a JSON key, it should work as a string in MiScheme. Strings
in MiScheme are immutable, in contrast to most other Scheme
implementations.

These differences in how strings behave are due to the status of strings in the
host languages: Python and Dart both have immutable strings.

### Pairs and Lists

Pairs are a built-in data structure consisting of two fields, a `car` and a
`cdr` (also sometimes called first and second, or first and rest).

`nil` is a special value in Scheme that represents the empty list. It can be
inputted by typing `nil` or `()` into the interpreter.

A **list** (or **proper list**) is defined as either `nil` or a pair
whose `cdr` is another list. Lists are displayed as a parenthesized,
space separated, sequence of the elements in the sequence they
represent. For example, `(cons (cons 1 nil) (cons 2 nil))` is
displayed as `((1) 2)`. This means that `cons` is asymmetric.

An **improper list** is a sequence of pairs that is not terminated by
`nil`. An improper list is displayed similarly to a proper list,
except that the final element is preceded by a dot. For example,
`(cons 1 (cons 2 3))` is displayed as `(1 2 . 3)`.

List and improper-list literals can be constructed through the quote
special form, so `(cons 1 (cons 'a nil))` and `'(1 a)` are equivalent.
The built-in `list` procedure also constructs a proper list, taking
any number of arguments. For example, `(list 1 'a -7)` results in the
list `(1 a -7)`.

### Procedures

Procedures represent some subroutine within a Scheme program. Procedures are
first-class in Scheme, meaning that they can be bound to names and passed
around just like any other Scheme value. Procedures are equivalent to functions
in most other languages, and the two terms are sometimes used interchangeably.

Procedures can be called on some number of arguments, performing some number
of actions and then returning some Scheme value.

A procedure call can be performed with the syntax `(<operator> <operand> ...)`,
where `<operator>` is some expression that evaluates to a procedure and each
`<operand>` (of which there can be any number, including 0) evaluates to one of
the procedure's arguments. The term "procedure call" is used interchangeably
with the term "call expression."

There are several types of procedures. Built-in procedures (or just built-ins)
are built-in to the interpreter and already bound to names when it is started
(though it is still possible for you to rebind these names). A list of all the
built-in procedures in the Python-based interpreter is available in the
[Scheme built-ins][] document.

Lambda procedures are defined using the `lambda` or `define` special forms (see
below) and create a new frame whose parent is the frame in which the lambda was
defined in when called. The expressions in the lambda's body are than evaluated
in this new environment. Mu procedures are similar, but the new frame's parent
is the frame in which the `mu` is called, not the frame in which it was created.

MiScheme also has macro procedures, which must be defined with the
`define-macro` special form (MiScheme does not support the standard
`define-syntax` and `syntax-rules`). Macros work similarly to lambdas,
except that they pass the argument expressions in the call expression
into the macro instead of the evaluated arguments and they then
evaluate the expression the macro returns in the calling environment
afterwards. The modified process for evaluating macro call expressions
is:

1. Evaluate the operator. If it is not a macro procedure, follow the normal call
expression steps.
2. Apply the macro procedure from step 1 to the unevaluated operands.
3. Once the macro returns, evaluate that value in the calling environment.

Macros effectively let the user define new special forms. Macro procedures take
in unevaluated operand expressions and should generally return a piece of Scheme
code that the macro is equivalent to.

### Promises

Promises represent the delayed evaluation of an expression in an environment.
They can be constructed by passing an expression into the `delay` special form.
The evaluation of a promise can be forced by passing it into the `force`
built-in. The expression of a promise will only ever be evaluated once. The
first call of `force` will store the result, which will be immediately returned
on subsequent calls of `force` on the same promise. If `force` errors
for any reason, the promise remains unforced.

For example

```scheme
scm> (define p (delay (begin (display "hi") (newline) (/ 1 0))))
p
scm> p
#[promise]
scm> (force p)
hi
Error
scm> p
#[promise]
scm> (force p)
hi
Error
```

Or, for an example with type errors:

```scheme
scm> (define p (delay (begin (display "hi") (newline) (+ 2 'a))))
p
scm> p
#[promise]
scm> (force p)
hi
Error
scm> p
#[promise]
scm> (force p)
hi
Error
```

> A note for those familiar with promises in languages like JavaScript: although
Scheme promises and JS-style promises originate from the
[same general concept][promise wiki], JS promises are best described as a
placeholder for a value that is computed asynchronously. The
Python-based MiScheme interpreter has no concept of asynchrony, so its
promises only represent delayed evaluation.

  [promise wiki]: https://en.wikipedia.org/wiki/Futures_and_promises

## Special Forms

In all of the syntax definitions below, `<x>` refers to a required element `x`
that can vary, while `[x]` refers to an optional element `x`. Ellipses
indicate that there can be more than one of the preceding element.

### **`define`**

    (define <name> <expression>)

Evaluates `<expression>` and binds the value to `<name>` in the current
environment. `<name>` must be a valid Scheme symbol.

    (define (<name> [param] ...) <body> ...)

Constructs a new lambda procedure with `param`s as its parameters and the `body`
expressions as its body and binds it to `name` in the current environment.
`name` must be a valid Scheme symbol. Each `param` must be a unique valid Scheme
symbol. This shortcut is equivalent to:

    (define <name> (lambda ([param] ...) <body> ...))

However, some interpreters may give lambdas created using the shortcut an
intrinsic name of `name` for the purpose of visualization or debugging.

In either case, the return value is the symbol `<name>`.

```scheme
scm> (define x 2)
x
scm> (define (f x) x)
f
```

#### Variadic functions

In this implementation of the scheme language, you can define a function that takes a variable number of arguments by using the `variadic` special form. The construct `variadic` constructs a "variadic symbol" that is bound to multiple rather than a single variable. This is only allowed at the end of an arguments list

```scheme
scm> (define (f x (variadic y)) (append y (list x)))
f
scm> (f 1 2 3)
(2 3 1)
scm> (define (f (variadic y) x) (append y (list x)))
Error
```

This is also possible in lambdas:

```scheme
scm> (define f (lambda (x (variadic y)) (append y (list x))))
f
scm> (f 1 2 3)
(2 3 1)
scm> (define my-list (lambda ((variadic x)) x))
my-list
scm> (my-list 2 3 4)
(2 3 4)
```

You can use the special symbol `.` to construct the `variadic` special form:

```scheme
scm> (define (f x . y) (append y (list x)))
f
scm> (f 1 2 3)
(2 3 1)
scm> '. x
(variadic x)
```

This is analogous to `,` for `unquote`.

> This is pretty much the same as `*args` in python, except that you can't call a function using `variadic`, you instead have to use the `#[apply]` built-in function.

### **`if`**

    (if <predicate> <consequent> [alternative])

Evaluates `predicate`. If true, the `consequent` is evaluated and returned.
Otherwise, the `alternative`, if it exists, is evaluated and returned (if no
`alternative` is present in this case, the return value is undefined).

### **`cond`**

    (cond <clause> ...)

Each `clause` may be of the following form:

    (<test> [expression] ...)

The last `clause` may instead be of the form `(else <expression>
...)`, which is equivalent to `(#t <expression> ...)`.

Starts with the first `clause`. Evaluates `test`. If true, evaluate
the `expression`s in order, returning the result of the last one. If
there are none, return what `test` evaluated to instead. If `test` is
false, proceed to the next `clause`. If there are no more `clause`s,
the return value is undefined.

### **`case`**

    (case <key> <clause> ...)

The `key` can be any expression. Each `clause` may be of the following
form:

    (([value] ...) <expression> ...)

The last `clause` may instead be of the form `(else <expression>
...)`.

Evaluates `key`. Then, starting with the first `clause`, checks if a
clause has a `value` that is equivalent (according to the `eqv?`
procedure) to the result of evaluating `key`. Evaluates the
`expression`s of the first matching clause in order, returning the
result of the last one. If there are no matching clauses, evaluates
the `expression`s of the else clause, if present. The return value is
undefined if there are no matching clauses and no else clause.

### **`and`**

    (and [test] ...)

Evaluate the `test`s in order, returning the first false value. If no `test`
is false, return the last `test`. If no arguments are provided, return `#t`.

### **`or`**

    (or [test] ...)

Evaluate the `test`s in order, returning the first true value. If no `test`
is true and there are no more `test`s left, return `#f`.

### **`let`**

    (let ([binding] ...) <body> ...)

Each `binding` is of the following form:

    (<name> <expression>)

First, the `expression` of each `binding` is evaluated in the current frame.
Next, a new frame that extends the current environment is created and each
`name` is bound to its corresponding evaluated `expression` in it.

Finally the `body` expressions are evaluated in order, returning the evaluated
last one.

### **`let*`**

    (let* ([binding] ...) <body> ...)

Similar to `let`, except that the `expression` of each `binding` is evaluated
in an environment that contains the preceding bindings. In other words,

```scheme
(let* (<binding1> <binding2> ... <bindingN>) <body> ...)
```

is equivalent to

```scheme
(let (<binding1>)
  (let (<binding2>)
    ...
      (let (<bindingN>)
        <body> ...
      )
    ...
  )
)
```

### **`begin`**

    (begin <expression> ...)

Evaluates each `expression` in order in the current environment, returning the
evaluated last one.

### **`lambda`**

    (lambda ([param] ...) <body> ...)

Creates a new lambda with `param`s as its parameters and the `body` expressions
as its body. When the procedure this form creates is called, the call frame
will extend the environment this lambda was defined in.

### **`mu`**

    (mu ([param] ...) <body> ...)

Creates a new mu procedure with `param`s as its parameters and the `body`
expressions as its body. When the procedure this form creates is called, the
call frame will extend the environment the mu is called in.

### **`quote`**

    (quote <expression>)

Returns the literal `expression` without evaluating it.

`'<expression>` is equivalent to the above form.

### **`delay`**

    (delay <expression>)

Returns a promise of `expression` to be evaluated in the current environment.

### **`set!`**

    (set! <name> <expression>)

Evaluates `expression` and binds the result to `name` in the first frame it can
be found in from the current environment. If `name` is not bound in the current
environment, this causes an error.

The return value is undefined.

### **`quasiquote`**

    (quasiquote <expression>)

Returns the literal `expression` without evaluating it, unless a subexpression
of `expression` is of the form:

    (unquote <expr2>)

in which case that `expr2` is evaluated and replaces the above form in the
otherwise unevaluated `expression`.

```<expression>`` is equivalent to the above form.

### **`unquote`**

See above. `,<expr2>` is equivalent to the form mentioned above.

### **`unquote-splicing`**

    (unquote-splicing <expr2>)

Similar to `unquote`, except that `expr2` must evaluate to a list, which is
then spliced into the structure containing it in `expression`.

`,@<expr2>` is equivalent to the above form.

### **`define-macro`**

    (define-macro (<name> [param] ...) <body> ...)

> This special form is implemented as an extension in lieu of standard macros.

Constructs a new macro procedure with `param`s as its parameters and the `body`
expressions as its body and binds it to `name` in the current environment.
`name` must be a valid Scheme symbol. Each `param` must be a unique valid Scheme
symbol. `(<name> [param] ...)` can be [variadic](#variadic-functions).

Macro procedures are lexically scoped, like lambda procedures.

## Core Interpreter

<a class='builtin-header' id='apply'>**`apply`**</a>

```scheme
(apply <procedure> [arg1] ... <args>)
```

Calls `procedure` with the given set of arguments. `args` must be list.

```scheme
scm> (apply + '(1 2 3))
6
scm> (apply + 1 2 '(3))
6
```

On macros, this has the effect of calling the macro without the initial quoting
or final evaluation. Thus, `apply` treats a macro as if it were a function.

<a class='builtin-header' id='display'>**`display`**</a>

```scheme
(display <val>)
```

Prints `val`. If `val` is a Scheme string, it will be output without quotes.

A new line will not be automatically included.

<a class='builtin-header' id='error'>**`error`**</a>

```scheme
(error [msg])
```

Raises a `SchemeError` with `msg` as it's message. If there is no `msg`,
the error's message will be empty.

<a class='builtin-header' id='eval'>**`eval`**</a>

```scheme
(eval <expression>)
```

Evaluates `expression` in the current environment. This differs from
the standard form of `eval`, which takes an additional environment
argument.

```scheme
scm> (eval '(cons 1 (cons 2 nil)))
(1 2)
```

<a class='builtin-header' id='exit'>**`exit`**</a>

```scheme
(exit)
```

Exits the interpreter. In the web interpreter, this does nothing.

<a class='builtin-header' id='load'>**`load`**</a>

```scheme
(load <filename>)
```

Loads the contents of the file with `filename` and evaluates the code within.
`filename` must be a symbol. If that file is not found, `filename`.scm will
be attempted.

The web interpreter does not currently support `load`.

<a class='builtin-header' id='newline'>**`newline`**</a>

```scheme
(newline)
```

Prints a new line.

<a class='builtin-header' id='write'>**`write`**</a>

```scheme
(write <val>)
```

Prints the Scheme representation of `val`. Unlike `display`, this will include
the outer quotes on a Scheme string.

## Type Checking

<a class='builtin-header' id='atom?'>**`atom?`**</a>

```scheme
(atom? <arg>)
```

Returns true if `arg` is a boolean, number, symbol, string, or nil;
false otherwise.

<a class='builtin-header' id='boolean?'>**`boolean?`**</a>

```scheme
(boolean? <arg>)
```

Returns true if `arg` is a boolean; false otherwise.

<a class='builtin-header' id='char?'>**`char?`**</a>

```scheme
(char? <arg>)
```

Returns true if `arg` is a character; false otherwise.

<a class='builtin-header' id='complex?'>**`complex?`**</a>

```scheme
(complex? <arg>)
```

Returns true if `arg` is a number; false otherwise.

<a class='builtin-header' id='eof-object?'>**`eof-object?`**</a>

```scheme
(eof-object? <arg>)
```

Returns true if `arg` is an EOF object; false otherwise. This
implementation does not support EOF objects, so this will always
return false.

<a class='builtin-header' id='input-port?'>**`input-port?`**</a>

```scheme
(input-port? <arg>)
```

Returns true if `arg` is an input port; false otherwise. This
implementation does not support input ports, so this will always
return false.

<a class='builtin-header' id='integer?'>**`integer?`**</a>

```scheme
(integer? <arg>)
```

Returns true if `arg` is a integer; false otherwise.

<a class='builtin-header' id='list?'>**`list?`**</a>

```scheme
(list? <arg>)
```

Returns true if `arg` is a proper list (i.e., is nil or a sequence of
pairs terminated by nil); false otherwise. If the list has a cycle,
this may cause an error or infinite loop.

```scheme
scm> (list? '(1 2 3))
#t
scm> (list? '(1 2 . 3))
#f
```

<a class='builtin-header' id='number?'>**`number?`**</a>

```scheme
(number? <arg>)
```

Returns true if `arg` is a number; false otherwise.

<a class='builtin-header' id='null?'>**`null?`**</a>

```scheme
(null? <arg>)
```

Returns true if `arg` is `nil` (the empty list); false otherwise.

<a class='builtin-header' id='output-port?'>**`output-port?`**</a>

```scheme
(output-port? <arg>)
```

Returns true if `arg` is an output port; false otherwise. This
implementation does not support output ports, so this will always
return false.

<a class='builtin-header' id='pair?'>**`pair?`**</a>

```scheme
(pair? <arg>)
```

Returns true if `arg` is a pair; false otherwise.

<a class='builtin-header' id='procedure?'>**`procedure?`**</a>

```scheme
(procedure? <arg>)
```

Returns true if `arg` is a procedure; false otherwise.

<a class='builtin-header' id='promise?'>**`promise?`**</a>

```scheme
(promise? <arg>)
```

Returns true if `arg` is a promise; false otherwise.

<a class='builtin-header' id='rational?'>**`rational?`**</a>

```scheme
(rational? <arg>)
```

Returns true if `arg` is a rational number (only integers are rational
in this implementation); false otherwise.

<a class='builtin-header' id=real?'>**`real?`**</a>

```scheme
(real? <arg>)
```

Returns true if `arg` is a real number (all numbers are real in this
implementation); false otherwise.

<a class='builtin-header' id='string?'>**`string?`**</a>

```scheme
(string? <arg>)
```

Returns true if `arg` is a string; false otherwise.

<a class='builtin-header' id='symbol?'>**`symbol?`**</a>

```scheme
(symbol? <arg>)
```

Returns true if `arg` is a symbol; false otherwise.

<a class='builtin-header' id='vector?'>**`vector?`**</a>

```scheme
(vector? <arg>)
```

Returns true if `arg` is a vector; false otherwise.

## Type Conversions

<a class='builtin-header' id='number->string'>**`number->string`**</a>

```scheme
(number->string <num> [radix])
```

Returns a string representation of `num`, using `radix` as the base.
If `radix` is not given, it defaults to 10. `num` must be a number. If
`num` is an integer, then `radix` must be one of 2, 8, 10, or 16. If
`num` is a floating-point number, then `radix` must be 10.

<a class='builtin-header' id='string->number'>**`string->number`**</a>

```scheme
(string->number <str> [radix])
```

Parses `str`, which must be a string representation of a number, and
returns the resulting number. Uses `radix` as the base if the base is
not explicitly part of the string representation. `radix` must be one
of 2, 8, 10, or 16 if the string represents an integer, or 10 if the
string represents a floating-point number, and it defaults to 10 if it
is not provided. Note that this interpreter parses string
representations of numbers using Python notation rather than Scheme
notation for numeric literals. It is an error if the given string is
not a valid Python representation of a number in the given `radix`.

<a class='builtin-header' id='symbol->string'>**`symbol->string`**</a>

```scheme
(symbol->string <sym>)
```

Returns a string corresponding to `sym`, which must be a symbol. For
any symbol `sym`, it is guaranteed that `(eq? sym (string->symbol
(symbol->string sym)))` is true.

<a class='builtin-header' id='string->symbol'>**`string->symbol`**</a>

```scheme
(string->symbol <str>)
```

Returns a symbol corresponding to `str`, which must be a string. For
any string `str`, it is guaranteed that `(string=? str (symbol->string
(string->symbol str)))` is true. Note that it is possible to produce
symbols via `string->symbol` that cannot be typed in by the user. The
representation of such a symbol is implementation-dependent.

<a class='builtin-header' id='char->integer'>**`char->integer`**</a>

```scheme
(char->integer <char>)
```

Returns an integer value corresponding to `char`, which must be a
character. For any character `char`, it is guaranteed that `(char=?
char (integer->char (char->integer char)))` is true.

<a class='builtin-header' id='integer->char'>**`integer->char`**</a>

```scheme
(integer->char <num>)
```

Returns the character value corresponding to `num`, which must be an
integer that corresponds to some character. In other words, there is
some character `char` for which `(= num (char->integer char))` is
true. For any such integer `num`, it is guaranteed that `(= num
(char->integer (integer->char num)))` is true.

<a class='builtin-header' id='string->list'>**`string->list`**</a>

```scheme
(string->list <str>)
```

Returns a list of the characters in `str`, which must be a string.

<a class='builtin-header' id='list->string'>**`list->string`**</a>

```scheme
(list->string <lst>)
```

Returns a string constructed from the characters in `lst`, which must
be a list of characters. Equivalent to `(apply string lst)`.

<a class='builtin-header' id='vector->list'>**`vector->list`**</a>

```scheme
(vector->list <vec>)
```

Returns a list containing the elements from `vec`, which must be a
vector.

<a class='builtin-header' id='list->vector'>**`list->vector`**</a>

```scheme
(list->vector <lst>)
```

Returns a vector containing the elements from `lst`, which must be a
proper list. Equivalent to `(apply vector lst)`.

## Pair and List Manipulation

<a class='builtin-header' id='append'>**`append`**</a>

```scheme
(append [lst] ...)
```

Returns the result of appending the items of all `lst`s in order into a single
list. Returns `nil` if no `lst`s. The last argument can be any value, but
the preceding arguments must be proper lists.

```scheme
scm> (append '(1 2 3) '(4 5 6))
(1 2 3 4 5 6)
scm> (append)
()
scm> (append '(1 2 3) '(a b c) '(foo bar baz))
(1 2 3 a b c foo bar baz)
scm> (append '(1 2 3) 4)
(1 2 3 . 4)
scm> (append 4 '(1 2 3))
Error
```

<a class='builtin-header' id='assoc'>**`assoc`**</a>

```scheme
(assoc <item> <lst>)
```

Returns the result of searching `lst` for the first pair whose `car`
is equivalent to `item` according to the `equal?` procedure. `lst`
must be a list of pairs. If no matching pair is found, returns `#f`.

```scheme
scm> (assoc 'a '((b 3) (a 4) (c 2) (a -1)))
(a 4)
scm> (assoc 'd '((b 3) (a 4) (c 2) (a -1)))
#f
```

<a class='builtin-header' id='assq'>**`assq`**</a>

```scheme
(assq <item> <lst>)
```

Similar to `assoc`, except that `assq` uses `eq?` to compare items
rather than `equal?`.

<a class='builtin-header' id='assv'>**`assv`**</a>

```scheme
(assv <item> <lst>)
```

Similar to `assoc`, except that `assv` uses `eqv?` to compare items
rather than `equal?`.

<a class='builtin-header' id='car'>**`car`**</a>

```scheme
(car <pair>)
```

Returns the `car` of `pair`. Errors if `pair` is not a pair.

<a class='builtin-header' id='cdr'>**`cdr`**</a>

```scheme
(cdr <pair>)
```

Returns the `cdr` of `pair`. Errors if `pair` is not a pair.

The interpreter also provides compositions of `car` and `cdr` up to
four levels deep. For instance, `(cadr <pair>)` is equivalent to `(car
(cdr <pair>))`, and `(cadadr <pair>)` is equivalent to `(car (cdr (car
(cdr <pair>))))`.

<a class='builtin-header' id='cons'>**`cons`**</a>

```scheme
(cons <first> <rest>)
```

Returns a new pair with `first` as the `car` and `rest` as the `cdr`

<a class='builtin-header' id='length'>**`length`**</a>

```scheme
(length <arg>)
```

Returns the length of `arg`. If `arg` is not a list, this
will cause an error.

<a class='builtin-header' id='list'>**`list`**</a>

```scheme
(list [item] ...)
```

Returns a list with the `item`s in order as its elements.

<a class='builtin-header' id='list-tail'>**`list-tail`**</a>

```scheme
(list-tail <lst> <num>)
```

Return the sublist of `lst` that excludes the first `num` elements.
`num` must be an integer greater than or equal to zero, and less than
or equal to the length of the list.

<a class='builtin-header' id='list-ref'>**`list-ref`**</a>

```scheme
(list-ref <lst> <num>)
```

Return the element at index `num` in `lst`, with indices starting at
zero. `num` must be an integer greater than or equal to zero, and
strictly less than the length of the list.

<a class='builtin-header' id='map'>**`map`**</a>

```scheme
(map <proc> <lsts> ...)
```

Returns a list constructed by calling `proc` on the respective items
at the same position in the given lists. `proc` must take as many
arguments as there are lists. If more than one list is given, they
must all have the same length.

```scheme
scm> (map car '((a b) (c d) (e f)))
(a c e)
scm> (map + '(1 2 3) '(4 5 6))
(5 7 9)
```

<a class='builtin-header' id='member'>**`member`**</a>

```scheme
(member <item> <lst>)
```

Returns the first sublist of `lst` whose `car` is equivalent to `item`
according to the `equal?` procedure. `lst` must be a proper list. If
no matching element is found, returns `#f`.

```scheme
scm> (member 'a '(c a b a))
(a b a)
scm> (member 'd '(c a b a))
#f
```

<a class='builtin-header' id='memq'>**`memq`**</a>

```scheme
(memq <item> <lst>)
```

Similar to `member`, except that `memq` uses `eq?` to compare items
rather than `equal?`.

<a class='builtin-header' id='memv'>**`memv`**</a>

```scheme
(memv <item> <lst>)
```

Similar to `member`, except that `memv` uses `eqv?` to compare items
rather than `equal?`.

<a class='builtin-header' id='reverse'>**`reverse`**</a>

```scheme
(reverse <lst>)
```

Returns a new list consisting of the elements in `lst` in reverse
order. `lst` must be a proper list.

```scheme
scm> (reverse '(1 2 3))
(3 2 1)
scm> (reverse '(1 2 . 3))
Error
```

### Mutation

<a class='builtin-header' id='set-car!'>**`set-car!`**</a>

```scheme
(set-car! <pair> <value>)
```

Sets the `car` of `pair` to `value`. `pair` must be a pair.

<a class='builtin-header' id='set-cdr!'>**`set-cdr!`**</a>

```scheme
(set-cdr! <pair> <value>)
```

Sets the `cdr` of `pair` to `value`. `pair` must be a pair.

## Arithmetic Operations

<a class='builtin-header' id='+'>**`+`**</a>

```scheme
(+ [num] ...)
```

Returns the sum of all `num`s. Returns 0 if there are none. If any `num` is not
a number, this will error.

<a class='builtin-header' id='-'>**`-`**</a>

```scheme
(- <num> ...)
```

If there is only one `num`, return its negation. Otherwise, return the first
`num` minus the sum of the remaining `num`s. If any `num` is not a number, this
will error.

<a class='builtin-header' id='*'>**`*`**</a>

```scheme
(* [num] ...)
```

Returns the product of all `num`s. Returns 1 if there are none. If any `num` is
not a number, this will error.

<a class='builtin-header' id='/'>**`/`**</a>

```scheme
(/ <dividend> [divisor] ...)
```

If there are no `divisor`s, return 1 divided by `dividend`. Otherwise, return
`dividend` divided by the product of the `divisors`. This built-in does true
division, not floor division. `dividend` and all `divisor`s must be numbers.

```scheme
scm> (/ 4)
0.25
scm> (/ 7 2)
3.5
scm> (/ 16 2 2 2)
2
```

<a class='builtin-header' id='abs'>**`abs`**</a>

```scheme
(abs <num>)
```

Returns the absolute value of `num`, which must be a number.

<a class='builtin-header' id='expt'>**`expt`**</a>

```scheme
(expt <base> <power>)
```

Returns the `base` raised to the `power` power. Both must be numbers.

<a class='builtin-header' id='max'>**`max`**</a>

```scheme
(max <num> ...)
```

Returns the maximum of the given arguments, which must be numbers.

<a class='builtin-header' id='min'>**`min`**</a>

```scheme
(min <num> ...)
```

Returns the minimum of the given arguments, which must be numbers.

<a class='builtin-header' id='modulo'>**`modulo`**</a>

```scheme
(modulo <a> <b>)
```

Returns `a` modulo `b`. Both must be numbers.

```scheme
scm> (modulo 7 3)
1
scm> (modulo -7 3)
2
```

<a class='builtin-header' id='quotient'>**`quotient`**</a>

```scheme
(quotient <dividend> <divisor>)
```

Returns `dividend` integer divided by `divisor`. Both must be numbers.

```scheme
scm> (quotient 7 3)
2
```

<a class='builtin-header' id='remainder'>**`remainder`**</a>

```scheme
(remainder <dividend> <divisor>)
```

Returns the remainder that results when `dividend` is integer divided by
`divisor`. Both must be numbers. Differs from `modulo` in behavior when
negative numbers are involved.

```scheme
scm> (remainder 7 3)
1
scm> (remainder -7 3)
-1
```

<a class='builtin-header' id='round'>**`round`**</a>

```scheme
(round <num>)
```

Returns the closest integer to `num`, which must be a number. If `num` is
halfway between two integers, returns the even one.

```scheme
scm> (round -5.3)
-5
scm> (round 3.5)
4
scm> (round 4.5)
4
```

### Additional Math Procedures

The Python-based interpreter adds the following additional procedures whose
behavior exactly match the corresponding Python functions in the
[math module](https://docs.python.org/3/library/math.html).

- `acos`
- `asin`
- `atan`
- `cos`
- `exp`
- `floor`
- `gcd`
- `lcm`
- `log`
- `sin`
- `sqrt`
- `tan`

In addition, the interpreter implements the `ceiling` and `truncate`
procedures to match the behavior of Python's `ceil` and `trunc`
functions.

## Boolean Operations

### General

<a class='builtin-header' id='eqv?'>**`eqv?`**</a>

```scheme
(eqv? <a> <b>)
```

If `a` and `b` are both numbers, characters, booleans, or symbols, return true if
they are equivalent; false otherwise.

Otherwise, return true if `a` and `b` both refer to the same object in memory;
false otherwise.

```scheme
scm> (eqv? '(1 2 3) '(1 2 3))
#f
scm> (define x '(1 2 3))
scm> (eqv? x x)
#t
```

<a class='builtin-header' id='eq?'>**`eq?`**</a>

```scheme
(eq? <a> <b>)
```

If `a` and `b` are both booleans or symbols, return true if they are
equivalent; false otherwise.

Otherwise, return true if `a` and `b` both refer to the same object in memory;
false otherwise.

This function is essentially equivalent to Python's `is` operator.  Generally,
we will not be using `eq?` in this course, since `eqv?` is usually the
operator we want.

```scheme
scm> (eq? '(1 2 3) '(1 2 3))
#f
scm> (define x '(1 2 3))
scm> (eq? x x)
#t
>scm ; (eq? 1000000 1000000)  ; #t or #f: not well-defined.
```

<a class='builtin-header' id='equal?'>**`equal?`**</a>

```scheme
(equal? <a> <b>)
```

Returns true if `a` and `b` are equivalent. For two pairs, they are equivalent
if their `car`s are equivalent and their `cdr`s are equivalent. For two vectors,
they are equivalent if they have the same length, and their corresponding
elements are equivalent.

```scheme
scm> (equal? '(1 2 3) '(1 2 3))
#t
```

<a class='builtin-header' id='not'>**`not`**</a>

```scheme
(not <arg>)
```

Returns true if `arg` is false-y or false if `arg` is truthy.

### On Numbers

<a class='builtin-header' id='='>**`=`**</a>

```scheme
(= <num1> <num2> ...)
```

Returns true if the given numbers are equal. All arguments must be numbers.

<a class='builtin-header' id='<'>**`<`**</a>

```scheme
(< <num1> <num2> ...)
```

Returns true if the given numbers are monotonically increasing. All
arguments must be numbers.

<a class='builtin-header' id='>'>**`>`**</a>

```scheme
(> <num1> <num2> ...)
```

Returns true if the given numbers are monotonically decreasing. All
arguments must be numbers.

<a class='builtin-header' id='<='>**`<=`**</a>

```scheme
(<= <num1> <num2> ...)
```

Returns true if the given numbers are monotonically nondecreasing. All
arguments must be numbers.

<a class='builtin-header' id='>='>**`>=`**</a>

```scheme
(>= <num1> <num2> ...)
```

Returns true if the given numbers are monotonically nonincreasing. All
arguments must be numbers.

<a class='builtin-header' id='even?'>**`even?`**</a>

```scheme
(even? <num>)
```

Returns true if `num` is even. `num` must be a number.

<a class='builtin-header' id='exact?'>**`exact?`**</a>

```scheme
(exact? <num>)
```

Returns true if `num` is an exact number (an integer in this
implementation).

<a class='builtin-header' id='inexact?'>**`inexact?`**</a>

```scheme
(inexact? <num>)
```

Returns true if `num` is an inexact number (a floating-point number in
this implementation).

<a class='builtin-header' id='negative?'>**`negative?`**</a>

```scheme
(negative? <num>)
```

Returns true if `num` is negative. `num` must be a number.

<a class='builtin-header' id='odd?'>**`odd?`**</a>

```scheme
(odd? <num>)
```

Returns true if `num` is odd. `num` must be a number.

<a class='builtin-header' id='positive?'>**`positive?`**</a>

```scheme
(positive? <num>)
```

Returns true if `num` is positive. `num` must be a number.

<a class='builtin-header' id='zero?'>**`zero?`**</a>

```scheme
(zero? <num>)
```

Returns true if `num` is zero. `num` must be a number.

## Characters

<a class='builtin-header' id='char=?'>**`char=?`**</a>

```scheme
(char=? <char1> <char2>)
```

Returns true if `char1` and `char2` represent the same character
value. `char1` and `char2` must be characters.

<a class='builtin-header' id='char<?'>**`char<?`**</a>

```scheme
(char<? <char1> <char2>)
```

Returns true if `char1` has a numeric value that is less than that of
`char2`. In this implementation, it is equivalent to `(<
(char->integer char1) (char->integer char2))`. `char1` and `char2`
must be characters.

<a class='builtin-header' id='char>?'>**`char>?`**</a>

```scheme
(char>? <char1> <char2>)
```

Returns true if `char1` has a numeric value that is greater than that
of `char2`. In this implementation, it is equivalent to `(>
(char->integer char1) (char->integer char2))`. `char1` and `char2`
must be characters.

<a class='builtin-header' id='char<=?'>**`char<=?`**</a>

```scheme
(char<=? <char1> <char2>)
```

Returns true if `char1` has a numeric value that is less than or equal
to that of `char2`. In this implementation, it is equivalent to `(<=
(char->integer char1) (char->integer char2))`. `char1` and `char2`
must be characters.

<a class='builtin-header' id='char>=?'>**`char<?`**</a>

```scheme
(char>=? <char1> <char2>)
```

Returns true if `char1` has a numeric value that is greater than or
equal to that of `char2`. In this implementation, it is equivalent to
`(>= (char->integer char1) (char->integer char2))`. `char1` and
`char2` must be characters.

<a class='builtin-header' id='char-ci=?'>**`char-ci=?`**</a>

```scheme
(char-ci=? <char1> <char2>)
```

Returns true if `char1` and `char2` represent the same character
value, ignoring case for alphabetic characters. In this
implementation, it is equivalent to `(char=? (char-downcase char1)
(char-downcase char2)). `char1` and `char2` must be characters.

<a class='builtin-header' id='char-ci<?'>**`char-ci<?`**</a>

```scheme
(char-ci<? <char1> <char2>)
```

Returns true if `char1` has a numeric value that is less than that of
`char2`, ignoring case for alphabetic characters. In this
implementation, it is equivalent to `(char<? (char-downcase char1)
(char-downcase char2))`. `char1` and `char2` must be characters.

<a class='builtin-header' id='char-ci>?'>**`char-ci>?`**</a>

```scheme
(char-ci>? <char1> <char2>)
```

Returns true if `char1` has a numeric value that is greater than that
of `char2`, ignoring case for alphabetic characters. In this
implementation, it is equivalent to `(char>? (char-downcase char1)
(char-downcase char2))`. `char1` and `char2` must be characters.

<a class='builtin-header' id='char-ci<=?'>**`char-ci<=?`**</a>

```scheme
(char-ci<=? <char1> <char2>)
```

Returns true if `char1` has a numeric value that is less than or equal
to that of `char2`, ignoring case for alphabetic characters. In this
implementation, it is equivalent to `(char<=? (char-downcase char1)
(char-downcase char2))`. `char1` and `char2` must be characters.

<a class='builtin-header' id='char-ci>=?'>**`char-ci>=?`**</a>

```scheme
(char-ci>=? <char1> <char2>)
```

Returns true if `char1` has a numeric value that is greater than or
equal to that of `char2`, ignoring case for alphabetic characters. In
this implementation, it is equivalent to `(char>=? (char-downcase
char1) (char-downcase char2))`. `char1` and `char2` must be
characters.

<a class='builtin-header' id='char-alphabetic?'>**`char-alphabetic?`**</a>

```scheme
(char-alphabetic? <char>)
```

Returns true if `char` is an alphabetic character. `char` must be a
character.

<a class='builtin-header' id='char-numeric?'>**`char-numeric?`**</a>

```scheme
(char-numeric? <char>)
```

Returns true if `char` is a numeric character. `char` must be a
character.

<a class='builtin-header' id='char-whitespace?'>**`char-whitespace?`**</a>

```scheme
(char-whitespace? <char>)
```

Returns true if `char` is a whitespace character. `char` must be a
character.

<a class='builtin-header' id='char-lower-case?'>**`char-lower-case?`**</a>

```scheme
(char-lower-case? <char>)
```

Returns true if `char` is a lowercase alphabetic character. `char`
must be a character.

<a class='builtin-header' id='char-upper-case?'>**`char-upper-case?`**</a>

```scheme
(char-upper-case? <char>)
```

Returns true if `char` is an uppercase alphabetic character. `char`
must be a character.

<a class='builtin-header' id='char-upcase'>**`char-upcase`**</a>

```scheme
(char-upcase <char>)
```

If `char` represents a lowercase letter, returns its uppercase
counterpart. Otherwise returns `char` itself. `char` must be a
character.

<a class='builtin-header' id='char-downcase'>**`char-downcase`**</a>

```scheme
(char-downcase <char>)
```

If `char` represents an uppercase letter, returns its lowercase
counterpart. Otherwise returns `char` itself. `char` must be a
character.

## Strings

<a class='builtin-header' id='make-string'>**`make-string`**</a>

```scheme
(make-string <num> <char>)
```

Returns a string of length `num` in which all characters have the
value of `char`. `num` must be an integer, and `char` must be a
character. Note that this interpreter does not support the standard
single-argument form of `make-string` -- strings are immutable in this
implementation, so a string containing unspecified values would not be
useful.

<a class='builtin-header' id='string'>**`string`**</a>

```scheme
(string [char] ...)
```

Returns a string consisting of the given characters. Each `char` must
be a character.

<a class='builtin-header' id='string-length'>**`string-length`**</a>

```scheme
(string-length <str>)
```

Returns the length of the given string. `str` must be a string.

<a class='builtin-header' id='string-ref'>**`string-ref`**</a>

```scheme
(string-ref <str> <num>)
```

Returns the character value at the given index in the string. `str`
must be a string, and `num` must be an integer between 0 and one less
than the length of `str`.

<a class='builtin-header' id='string=?'>**`string=?`**</a>

```scheme
(string=? <str1> <str2>)
```

Returns whether or not `str1` and `str2` have the same length and
contents. `str1` and `str2` must be strings.

<a class='builtin-header' id='string-ci=?'>**`string-ci=?`**</a>

```scheme
(string-ci=? <str1> <str2>)
```

Returns whether or not `str1` and `str2` have the same length and
contents, ignoring case for alphabetic characters. `str1` and `str2`
must be strings.

<a class='builtin-header' id='string<?'>**`string<?`**</a>

```scheme
(string<? <str1> <str2>)
```

Returns whether or not `str1` is lexicographically less than `str2`,
using the ordering of the numeric values of the characters in each
string. `str1` and `str2` must be strings.

<a class='builtin-header' id='string-ci<?'>**`string-ci<?`**</a>

```scheme
(string-ci<? <str1> <str2>)
```

Returns whether or not `str1` is lexicographically less than `str2`,
using the ordering of the numeric values of the characters in each
string, but treating corresponding lowercase and uppercase alphabetic
characters as the same. `str1` and `str2` must be strings.

<a class='builtin-header' id='string<=?'>**`string<=?`**</a>

```scheme
(string<=? <str1> <str2>)
```

Returns whether or not `str1` is lexicographically less than or equal
to `str2`, using the ordering of the numeric values of the characters
in each string. `str1` and `str2` must be strings.

<a class='builtin-header' id='string-ci<=?'>**`string-ci<=?`**</a>

```scheme
(string-ci<=? <str1> <str2>)
```

Returns whether or not `str1` is lexicographically less than or equal
to `str2`, using the ordering of the numeric values of the characters
in each string, but treating corresponding lowercase and uppercase
alphabetic characters as the same. `str1` and `str2` must be strings.

<a class='builtin-header' id='string>?'>**`string>?`**</a>

```scheme
(string>? <str1> <str2>)
```

Returns whether or not `str1` is lexicographically greater than `str2`,
using the ordering of the numeric values of the characters in each
string. `str1` and `str2` must be strings.

<a class='builtin-header' id='string-ci>?'>**`string-ci>?`**</a>

```scheme
(string-ci>? <str1> <str2>)
```

Returns whether or not `str1` is lexicographically greater than
`str2`, using the ordering of the numeric values of the characters in
each string, but treating corresponding lowercase and uppercase
alphabetic characters as the same. `str1` and `str2` must be strings.

<a class='builtin-header' id='string>=?'>**`string>=?`**</a>

```scheme
(string>=? <str1> <str2>)
```

Returns whether or not `str1` is lexicographically greater than or
equal to `str2`, using the ordering of the numeric values of the
characters in each string. `str1` and `str2` must be strings.

<a class='builtin-header' id='string-ci>=?'>**`string-ci>=?`**</a>

```scheme
(string-ci>=? <str1> <str2>)
```

Returns whether or not `str1` is lexicographically greater than or
equal to `str2`, using the ordering of the numeric values of the
characters in each string, but treating corresponding lowercase and
uppercase alphabetic characters as the same. `str1` and `str2` must be
strings.

<a class='builtin-header' id='substring'>**`substring`**</a>

```scheme
(substring <str> <start> <end>)
```

Returns a new string with the subset of characters from `str` starting
at `start` (inclusive) and ending at `end` (exclusive). `str` must be
string, `start` and `end` must be integers, `start` must be at least 0
and at most `end`, and `end` must be at least `start` and at most the
length of `str`.

<a class='builtin-header' id='string-append'>**`string-append`**</a>

```scheme
(string-append [str] ...)
```

Returns a new string that is the concatenation of the contents of the
given strings. Each `str` must be a string.

<a class='builtin-header' id='string-copy'>**`string-copy`**</a>

```scheme
(string-copy <str>)
```

Returns a new string that is contains the same contents as `str`, such
that `(string=? str (string-copy str))` is true but `(eq? str
(string-copy str))` is false. `str` must be a string.

## Vectors

<a class='builtin-header' id='make-vector'>**`make-vector`**</a>

```scheme
(make-vector <num> [item])
```

Returns a vector of length `num`, which must be a nonnegative integer.
If `item` is provided, each element of the vector is set to `item`.
Otherwise, the contents of the vector are unspecified.

<a class='builtin-header' id='vector'>**`vector`**</a>

```scheme
(vector [item] ...)
```

Returns a vector consisting of the given items.

<a class='builtin-header' id='vector-length'>**`vector-length`**</a>

```scheme
(vector-length <vec>)
```

Returns the length of the given vector. `vec` must be a vector.

<a class='builtin-header' id='vector-ref'>**`vector-ref`**</a>

```scheme
(vector-ref <vec> <num>)
```

Returns the item at the given index in the vector. `vec` must be a
vector, and `num` must be an integer between 0 and one less than the
length of `vec`.

<a class='builtin-header' id='vector-set!'>**`vector-set!`**</a>

```scheme
(vector-set! <vec> <num> <item>)
```

Replaces the element at index `num` in `vec` with `item`. `vec` must
be a vector, and `num` must be an integer between 0 and one less than
the length of `vec`. The return value is unspecified.

<a class='builtin-header' id='vector-fill!'>**`vector-fill!`**</a>

```scheme
(vector-fill! <vec> <item>)
```

Replaces all elements in `vec` with `item`. `vec` must be a vector.
The return value is unspecified.

## Promises

<a class='builtin-header' id='force'>**`force`**</a>

```scheme
(force <promise>)
```

Returns the evaluated result of `promise`. If `promise` has already been
forced, its expression will not be evaluated again. Instead, the result from
the previous evaluation will be returned. `promise` must be a promise.

## Turtle Graphics

<a class='builtin-header' id='backward'>**`backward`**</a>

```scheme
(backward <n>)
```

Moves the turtle backward `n` units in its current direction from its current
position.

*Aliases: `back`, `bk`*

<a class='builtin-header' id='begin_fill'>**`begin_fill`**</a>

```scheme
(begin_fill)
```

Starts a sequence of moves that outline a shape to be filled.
Call `end_fill` to complete the fill.

<a class='builtin-header' id='bgcolor'>**`bgcolor`**</a>

```scheme
(bgcolor <c>)
```

Sets the background color of the turtle window to a color `c` (same rules as
when calling `color`).

<a class='builtin-header' id='circle'>**`circle`**</a>

```scheme
(circle <r> [extent])
```

Draws a circle of radius `r`, centered `r` units to the turtle's left.
If `extent` exists, draw only the first `extent` degrees of the circle.
If `r` is positive, draw in the counterclockwise direction. Otherwise, draw
in the clockwise direction.

<a class='builtin-header' id='clear'>**`clear`**</a>

```scheme
(clear)
```

Clears the drawing, leaving the turtle unchanged.

<a class='builtin-header' id='color'>**`color`**</a>

```scheme
(color <c>)
```

Sets the pen color to `c`, which is a Scheme string such as "red" or "#ffc0c0".

<a class='builtin-header' id='end_fill'>**`end_fill`**</a>

```scheme
(end_fill)
```

Fill in shape drawn since last call to `begin_fill`.

<a class='builtin-header' id='exitonclick'>**`exitonclick`**</a>

```scheme
(exitonclick)
```

In pillow-turtle mode, this exits the current program. In tk-turtle mode, it exits the current program
when the window is clicked. In the web interpreter, it does nothing.

In the local interpreter, you can pass `--turtle-save-path PATH` to also effectively call
`(save-to-file PATH)` right before exit.

<a class='builtin-header' id='forward'>**`forward`**</a>

```scheme
(forward <n>)
```

Moves the turtle forward `n` units in its current direction from its current
position.

*Alias: `fd`*

<a class='builtin-header' id='hideturtle'>**`hideturtle`**</a>

```scheme
(hideturtle)
```

Makes the turtle invisible.

*Alias: `ht`*

<a class='builtin-header' id='left'>**`left`**</a>

```scheme
(left <n>)
```

Rotates the turtle's heading `n` degrees counterclockwise.

*Alias: `lt`*

<a class='builtin-header' id='pendown'>**`pendown`**</a>

```scheme
(pendown)
```

Lowers the pen so that the turtle starts drawing.

*Alias: `pd`*

<a class='builtin-header' id='penup'>**`penup`**</a>

```scheme
(penup)
```

Raises the pen so that the turtle does not draw.

*Alias: `pu`*

<a class='builtin-header' id='pixel'>**`pixel`**</a>

```scheme
(pixel <x> <y> <c>)
```

Draws a box filled with pixels starting at (`x`, `y`) in color `c` (same rules
as in `color`). By default the box is one pixel, though this can be changed
with `pixelsize`.

<a class='builtin-header' id='pixelsize'>**`pixelsize`**</a>

```scheme
(pixelsize <size>)
```

Changes the size of the box drawn by `pixel` to be `size`x`size`.

<a class='builtin-header' id='rgb'>**`rgb`**</a>

```scheme
(rgb <r> <g> <b>)
```

Returns a color string formed from `r`, `g`, and `b` values between 0 and 1.

<a class='builtin-header' id='right'>**`right`**</a>

```scheme
(right <n>)
```

Rotates the turtle's heading `n` degrees clockwise.

*Alias: `rt`*

<a class='builtin-header' id='save-to-file'>**`save-to-file`**</a>

    (save-to-file <f>)

Saves the current canvas to a file specified by `f`, with an added file extension.

For example, `(save-to-file "hi")`

- saves to `./hi.png` in the local interpreter using the pillow-turtle
- saves to `./hi.ps` in the local interpreter using the tk-turtle  (default)
- has no effect in the web interpreter

<a class='builtin-header' id='screen_width'>**`screen_width`**</a>

```scheme
(screen_width)
```

Returns the width of the turtle screen in pixels of the current size.

<a class='builtin-header' id='screen_height'>**`screen_height`**</a>

```scheme
(screen_height)
```

Returns the height of the turtle screen in pixels of the current size.

<a class='builtin-header' id='setheading'>**`setheading`**</a>

```scheme
(setheading <h>)
```

Sets the turtle's heading `h` degrees clockwise from the north.

*Alias: `seth`*

<a class='builtin-header' id='setposition'>**`setposition`**</a>

```scheme
(setposition <x> <y>)
```

Moves the turtle to position (`x`, `y`) without changing its heading.

*Aliases: `setpos`, `goto`*

<a class='builtin-header' id='showturtle'>**`showturtle`**</a>

```scheme
(showturtle)
```

Makes the turtle visible.

*Alias: `st`*

<a class='builtin-header' id='speed'>**`speed`**</a>

```scheme
(speed <s>)
```

Sets the turtle's animation speed to some value between 0 and 10 with 0
indicating no animation and 1-10 indicating faster and faster movement.

> On the local interpreter in tk-turtle mode, this changes the animation speed.
> This feature has no effect on the web interpreter and
> on the gui-less pillow-turtle mode.
