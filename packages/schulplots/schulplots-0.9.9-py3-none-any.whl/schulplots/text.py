from dataclasses import dataclass, field
from typing import Optional, Any, ClassVar
import numpy as np

from .converter import register_model, register_impl
from .utils.math_expression import MathExpression
try:
    from icecream import ic
except ImportError:  # Graceful fallback if IceCream isn't installed.
    ic = lambda *a: None if not a else (a[0] if len(a) == 1 else a)  # noqa

from .saxes import SAxes
    
@register_model  
@dataclass
class TextModel:
    class_id: ClassVar[str] = "Text"   
    text: str
    x: MathExpression
    y: MathExpression
    rotation: MathExpression = MathExpression(0)
    text_args: dict[str, Any] = field(default_factory=lambda: dict(zorder=100))
@register_impl
class Text(TextModel):
    
    _saxes: SAxes
    def __init__(self, saxes: SAxes, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.set_saxes(saxes)
        # print(f"in {self.class_id}.__init__", self)
    def set_saxes(self, saxes: SAxes):
        self._saxes = saxes
        x = self._saxes.evaluate(self.x)
        y = self._saxes.evaluate(self.y)
        rotation = self._saxes.evaluate(self.rotation)
        self._saxes.axes.text(x,y, self.text, rotation=rotation, 
                                 **self.text_args)
