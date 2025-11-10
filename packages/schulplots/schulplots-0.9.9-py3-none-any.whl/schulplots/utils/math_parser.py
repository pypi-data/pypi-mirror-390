## Code in this file is heavily based on the fourFn example from pyparsing
## (https://github.com/pyparsing/pyparsing/blob/master/examples/fourFn.py)
## The original copiright notice is repoduced below.

## Changes: 
## - add an object-oriented interface
## - add boolean operators, trying to reproduce the python semantics of these operators
## - same for comparison operators
## - include (some) numpy ufuncs

# fourFn.py
#
# Demonstration of the pyparsing module, implementing a simple 4-function expression parser,
# with support for scientific notation, and symbols for e and pi.
# Extended to add exponentiation and simple built-in functions.
# Extended test cases, simplified pushFirst method.
# Removed unnecessary expr.suppress() call (thanks Nathaniel Peterson!), and added Group
# Changed fnumber to use a Regex, which is now the preferred method
# Reformatted to latest pypyparsing features, support multiple and variable args to functions
#
# Copyright 2003-2019 by Paul McGuire
#

# Permission is hereby granted, free of charge, to any person obtaining
# a copy of this software and associated documentation files (the
# "Software"), to deal in the Software without restriction, including
# without limitation the rights to use, copy, modify, merge, publish,
# distribute, sublicense, and/or sell copies of the Software, and to
# permit persons to whom the Software is furnished to do so, subject to
# the following conditions:
# 
# The above copyright notice and this permission notice shall be
# included in all copies or substantial portions of the Software.
# 
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
# MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
# IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY
# CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT,
# TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE
# SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
#%%
from pyparsing import (
    Literal,
    Word,
    Group,
    Forward,
    alphas,
    alphanums,
    Regex,
    ParseException,
    CaselessKeyword,
    Suppress,
    delimitedList,
)
import math
import operator
from typing import Any, Optional
import numpy as np

vardict_t = Optional[dict[str, Any]]

# map operator symbols to corresponding arithmetic operations
epsilon = 1e-12
opn = {
    "**": operator.pow,
    "+": operator.add,
    "-": operator.sub,
    "*": operator.mul,
    "/": operator.truediv,
    "^": operator.pow,
    "and": operator.and_,
    "or": operator.or_,
    "xor": operator.xor,
    "not": operator.not_,
    "~": operator.not_,
    "<=": operator.le,
    "<": operator.lt,
    ">=": operator.ge,
    ">": operator.gt,
    "==": operator.eq,
    "!=": operator.ne,
}

# NumPy ufuncs with one argument
fn = {key: val for (key, val) in np.__dict__.items() 
      if isinstance(val, np.ufunc) 
      if ("e->e" in val.types) or ("ee->e" in val.types)}
    
    
    
class MathParser:
    def __init__(self):
        self.exprStack = []
        self.bnf = None
        self.init_BNF()

    def push_first(self, toks):
        self.exprStack.append(toks[0])


    def push_unary_minus(self, toks):
        for t in toks:
            if t == "-":
                self.exprStack.append("unary -")
            else:
                break
    def push_unary_not(self, toks):
        for t in toks:
            if t in ["~", "not"]:
                self.exprStack.append("unary not")
            else:
                break
            

    def init_BNF(self):
        """
        expop   :: '^'
        multop  :: '*' | '/'
        addop   :: '+' | '-'
        integer :: ['+' | '-'] '0'..'9'+
        atom    :: PI | E | real | fn '(' expr ')' | '(' expr ')'
        factor  :: atom [ expop factor ]*
        term    :: factor [ multop factor ]*
        expr    :: term [ addop term ]*
        
        
        ... not covered in this grammar, but present in the code below:
        - boolean operators
        - comparison operators
        """
        if self.bnf is None:
            # use CaselessKeyword for e and pi, to avoid accidentally matching
            # functions that start with 'e' or 'pi' (such as 'exp'); Keyword
            # and CaselessKeyword only match whole words
            e = CaselessKeyword("E")
            pi = CaselessKeyword("PI")
            # fnumber = Combine(Word("+-"+nums, nums) +
            #                    Optional("." + Optional(Word(nums))) +
            #                    Optional(e + Word("+-"+nums, nums)))
            # or use provided pyparsing_common.number, but convert back to str:
            # fnumber = ppc.number().addParseAction(lambda t: str(t[0]))
            fnumber = Regex(r"[+-]?\d+(?:\.\d*)?(?:[eE][+-]?\d+)?")
            ident = Word(alphas, alphanums + "_$")

            plus, minus, mult, div = map(Literal, "+-*/")
            le, less, ge, greater, equal, nequal = map(Literal, ["<=","<",">=",">","=","!="])
            and_, or_, xor, not_, not_alt = map(Literal, ["and", "or", "xor", "not", "~"])
            lpar, rpar = map(Suppress, "()")
            logicop = and_ | or_ | xor 
            compop = le | less | ge | greater | equal | nequal 
            addop = plus | minus
            notop = not_ | not_alt
            multop = mult | div
            expop = Literal("^") | Literal("**")

            logicexpr = Forward()
            compexpr = Forward()
            expr_list = delimitedList(Group(logicexpr)) 
            # add parse action that replaces the function identifier with a (name, number of args) tuple
            def insert_fn_argcount_tuple(t):
                fn = t.pop(0)
                num_args = len(t[0])
                t.insert(0, (fn, num_args))

            fn_call = (ident + lpar - Group(expr_list) + rpar).setParseAction(
                insert_fn_argcount_tuple
            )
            atom = (
                addop[...] 
                + (
                    (fn_call | pi | e | fnumber | ident).setParseAction(self.push_first)
                    | Group(lpar + logicexpr + rpar)
                )
            ).setParseAction(self.push_unary_minus)

            # by defining exponentiation as "atom [ ^ factor ]..." instead of "atom [ ^ atom ]...", we get right-to-left
            # exponents, instead of left-to-right that is, 2^3^2 = 2^(3^2), not (2^3)^2.
            factor = Forward()
            factor <<= atom + (expop + factor).setParseAction(self.push_first)[...]
            term = factor + (multop + factor).setParseAction(self.push_first)[...]
            expr = term + (addop + term).setParseAction(self.push_first)[...]
            compexpr  = (
                notop[...] + 
                expr + (compop + expr).setParseAction(self.push_first)[...]
            ).setParseAction(self.push_unary_not)
            logicexpr <<= compexpr + (logicop + compexpr).setParseAction(self.push_first)[...]
            self.bnf = logicexpr




    @staticmethod
    def evaluate_stack(s, var_dict: vardict_t = None,
                       func_dict: vardict_t = None):
        if var_dict is None:
            var_dict = dict()
        if func_dict is None:
            func_dict = fn
        else: 
            func_dict = func_dict.copy()
            func_dict.update(fn)
        op, num_args = s.pop(), 0
        if isinstance(op, tuple):
            op, num_args = op
        if op == "unary -":
            return -MathParser.evaluate_stack(s, var_dict, func_dict)
        if op == "unary not":
            return ~ MathParser.evaluate_stack(s, var_dict, func_dict)
        if op in opn:
            # note: operands are pushed onto the stack in reverse order
            op2 = MathParser.evaluate_stack(s, var_dict, func_dict)
            op1 = MathParser.evaluate_stack(s, var_dict, func_dict)
            return opn[op](op1, op2)
        elif op.lower() == "pi":
            return math.pi  # 3.1415926535
        elif op.lower() == "e":
            return math.e  # 2.718281828
        elif op in func_dict:
            # note: args are pushed onto the stack in reverse order
            args = reversed([MathParser.evaluate_stack(s, var_dict, func_dict) for _ in range(num_args)])
            return func_dict[op](*args)
        elif op.isidentifier():
            try:
                return var_dict[op]
            except KeyError:
                raise KeyError(f"unknown variable {op}")
        elif op[0].isalpha():
            raise Exception("invalid identifier '%s'" % op)
        else:
            # try to evaluate as int first, then as float if int fails
            try:
                return int(op)
            except ValueError:
                return float(op)
    def compile_expression(self, s: str):
        self.exprStack[:] = []
        if self.bnf is None:
            raise ValueError("This should not happen...")
        self.results = self.bnf.parseString(s, parseAll=True)
        return self.exprStack[:]
    def evaluate_compiled_expression(self, 
                                     expr_stack, 
                                     var_dict:vardict_t = None,
                                     func_dict:vardict_t = None):
        return self.evaluate_stack(expr_stack[:], var_dict, func_dict)
    def evaluate_expression(self, s: str, 
                            var_dict:vardict_t = None,
                             func_dict:vardict_t = None):
        stack = self.compile_expression(s)
        return self.evaluate_compiled_expression(stack, var_dict, func_dict)
    def evaluate_expression_(self, s: str, 
                             var_dict:vardict_t = None):
        if self.bnf is None:
            raise ValueError("This should not happen...")
        self.exprStack[:] = []
        self.results = self.bnf.parseString(s, parseAll=True)
        val = self.evaluate_stack(self.exprStack[:], var_dict)
        return val
    
    
parser=MathParser()

if __name__ == "__main__":
    import numpy as np
    p = MathParser()
    x = np.linspace(-1,1,10)
    print(p.evaluate_expression("sin(x_1222see)", dict(x_1222see=x)))


    def test(s, expected):
        try:
            val = p.evaluate_expression(s)
        except ParseException as pe:
            print(s, "failed parse:", str(pe))
        except Exception as e:
            print(s, "failed eval:", str(e), p.exprStack)
        else:
            if val == expected:
                print(s, "=", val, p.results, "=>", p.exprStack)
            else:
                print(s + "!!!", val, "!=", expected, p.results, "=>", p.exprStack)

    test("9", 9)
    test("-9", -9)
    test("--9", 9)
    test("-E", -math.e)
    test("9 + 3 + 6", 9 + 3 + 6)
    test("9 + 3 / 11", 9 + 3.0 / 11)
    test("(9 + 3)", (9 + 3))
    test("(9+3) / 11", (9 + 3.0) / 11)
    test("9 - 12 - 6", 9 - 12 - 6)
    test("9 - (12 - 6)", 9 - (12 - 6))
    test("2*3.14159", 2 * 3.14159)

