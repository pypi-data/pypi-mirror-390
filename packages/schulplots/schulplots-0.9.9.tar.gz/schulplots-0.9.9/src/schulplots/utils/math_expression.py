
#%%
from .math_parser import parser, vardict_t


class MathExpression(str):
    def __new__(cls, s):
        return super().__new__(cls, str(s))
    def __init__(self, s, **kwargs):
        super().__init__()
        self._evaluated = None
        self.value = s
        
    def evaluate(self, vars: vardict_t = None, 
                 functions: vardict_t = None, 
                 force_reeval=False):
        if vars is None:
            vars = {}
        if self._evaluated is None or force_reeval:
            self._evaluated = parser.evaluate_expression(self, vars, functions)
        return self._evaluated

# %%

# @dataclass
# class A:
#     m: MathExpression
#     b: int = 12
#     
#     def __post_init__(self):
#         self.m = MathExpression(self.m)
#     
# from cattrs.preconf.pyyaml import make_converter
# converter = make_converter()
# a = A(m="1+3*(3-2)")
# a1 = converter.structure(converter.unstructure(a), A)
# a1 == a

# %%
