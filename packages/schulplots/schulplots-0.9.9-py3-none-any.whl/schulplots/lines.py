from dataclasses import dataclass, field
from typing import Optional, Any, ClassVar

from .converter import register_model, register_impl
from .utils.math_expression import MathExpression

try:
    from icecream import ic # pyright: ignore[reportMissingImports]
except ImportError:  # Graceful fallback if IceCream isn't installed.
    ic = lambda *a: None if not a else (a[0] if len(a) == 1 else a)  # noqa

from .saxes import SAxes
    
@register_model  
@dataclass
class VLineModel:
    class_id: ClassVar[str] = "VLine"    
    x: MathExpression = MathExpression(0)
    y_min: float = 0.
    y_max: float = 1.
    plot_args: dict[str, Any] = field(default_factory=lambda: dict(alpha=0.5))
@register_impl
class VLine(VLineModel):
    _saxes: SAxes
    def __init__(self, saxes: SAxes, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.set_saxes(saxes)
    def set_saxes(self, saxes: SAxes):
        self._saxes = saxes
        x = self._saxes.evaluate(self.x)
        self._saxes.axes.axvline(x=x,ymin=self.y_min, ymax=self.y_max, 
                                 **self.plot_args)
@register_model  
@dataclass
class HLineModel:
    class_id: ClassVar[str] = "HLine"    
    y: MathExpression = MathExpression(0)
    x_min: float = 0.
    x_max: float = 1.
    plot_args: dict[str, Any] = field(default_factory=lambda: dict(alpha=0.5))
@register_impl
class HLine(HLineModel):
    _saxes: SAxes
    def __init__(self, saxes: SAxes, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.set_saxes(saxes)
    def set_saxes(self, saxes: SAxes):
        self._saxes = saxes
        y = self._saxes.evaluate(self.y)
        self._saxes.axes.axhline(y=y,xmin=self.x_min, xmax=self.x_max, 
                                 **self.plot_args)
@register_model  
@dataclass
class VSpanModel:
    class_id: ClassVar[str] = "VSpan"    
    x0: MathExpression = MathExpression(0)
    x1: MathExpression = MathExpression(0)
    y_min: float = 0
    y_max: float = 1
    plot_args: dict[str, Any] = field(default_factory=lambda: dict(alpha=0.3, lw=0))

@register_impl
class VSpan(VSpanModel):
    _saxes: Optional[SAxes]
    def __init__(self, saxes: SAxes, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.set_saxes(saxes)
    def set_saxes(self, saxes: SAxes):
        self._saxes = saxes
        x0 = self._saxes.evaluate(self.x0)
        x1 = self._saxes.evaluate(self.x1)
        self._saxes.axes.axvspan(xmin=x0, xmax=x1,ymin=self.y_min, 
                                 ymax=self.y_max, **self.plot_args)
        
@register_model  
@dataclass
class HSpanModel:
    class_id: ClassVar[str] = "HSpan"    
    y0: MathExpression = MathExpression(0)
    y1: MathExpression = MathExpression(0)
    x_min: float = 0
    x_max: float = 1
    plot_args: dict[str, Any] = field(default_factory=lambda: dict(alpha=0.3, lw=0))

@register_impl
class HSpan(HSpanModel):
    _saxes: Optional[SAxes]
    def __init__(self, saxes: SAxes, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.set_saxes(saxes)
    def set_saxes(self, saxes: SAxes):
        self._saxes = saxes
        y0 = self._saxes.evaluate(self.y0)
        y1 = self._saxes.evaluate(self.y1)
        self._saxes.axes.axhspan(ymin=y0, ymax=y1,xmin=self.x_min, 
                                 xmax=self.x_max, **self.plot_args)
        
@register_model  
@dataclass
class ArrowModel:
    class_id: ClassVar[str] = "Arrow" 
    x: MathExpression = MathExpression(0)
    y: MathExpression = MathExpression(0)
    dx: MathExpression = MathExpression(0)
    dy: MathExpression = MathExpression(-1)
    width: float = 0.08
    length_includes_head: bool = True
    
    plot_args: dict[str, Any] = field(default_factory=lambda: dict(linewidth=0))

@register_impl
@dataclass
class Arrow(ArrowModel):
    def __init__(self, saxes, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._saxes = saxes
        self.setup_saxes(self._saxes)
    def setup_saxes(self, saxes: SAxes):
        self._saxes = saxes
        x = self._saxes.evaluate(self.x)
        y = self._saxes.evaluate(self.y)
        dx = self._saxes.evaluate(self.dx)
        dy = self._saxes.evaluate(self.dy)
        if "width" in self.plot_args:
            #logger.info("'width' may not be included in plot_args")
            del self.plot_args["width"]
        self._saxes.axes.arrow(x+dx,y+dy, -dx, -dy, 
                               length_includes_head=self.length_includes_head,
                               width=self.width, **self.plot_args)
        