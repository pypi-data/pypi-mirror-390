from dataclasses import dataclass
from typing import ClassVar, TYPE_CHECKING

from .converter import register_model, register_impl
try:
    from icecream import ic # pyright: ignore[reportMissingImports]
except ImportError:  # Graceful fallback if IceCream isn't installed.
    ic = lambda *a: None if not a else (a[0] if len(a) == 1 else a)  # noqa

if TYPE_CHECKING:
    from .saxes import SAxes
from .utils.math_expression import MathExpression

@register_model
@dataclass
class SFunctionModel:
    class_id: ClassVar[str] = "Function"
    function: MathExpression
    name: str
    
@register_impl
class SFunction(SFunctionModel):
    def __init__(self, saxes: "SAxes", *args, **kwargs):
        self._saxes = saxes
        super().__init__(*args, **kwargs)
        def f_x(x):
            return self.function.evaluate(dict(x=x), force_reeval=True)
        self._saxes.axes_functions.update({self.name: f_x})