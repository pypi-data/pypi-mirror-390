from dataclasses import dataclass, field
from typing import Any, ClassVar
import numpy as np

from .converter import register_model, register_impl
from .utils.math_expression import MathExpression

try:
    from icecream import ic # pyright: ignore[reportMissingImports]
except ImportError:  # Graceful fallback if IceCream isn't installed.
    ic = lambda *a: None if not a else (a[0] if len(a) == 1 else a)  # noqa

from .saxes import SAxes
from .types import cm, Size
    
default_plot_args_point: dict[str, Any] = dict(color="black")
default_plot_args_label: dict[str, Any] = dict(va="center", 
                                               ha="center",
                                               color="black")
@register_model  
@dataclass
class PointModel:
    class_id: ClassVar[str] = "Point"    
    x: MathExpression
    y: MathExpression
    label: str = ""
    angle: float = 90
    distance: Size = Size(0.5*cm)
    marker: str = "x"
    plot_args_point: dict[str, Any] = field(default_factory=dict)
    plot_args_label: dict[str, Any] = field(default_factory=dict)
@register_impl
class Point(PointModel):
    _saxes: SAxes
    def __init__(self, saxes: SAxes, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.set_saxes(saxes)
    def set_saxes(self, saxes: SAxes):
        self._saxes = saxes
        assert self._saxes.axes.figure is not None
        x = self._saxes.evaluate(self.x)
        y = self._saxes.evaluate(self.y)
        
        self.plot_args_point = default_plot_args_point | self.plot_args_point
        self._saxes.axes.scatter([x], [y], marker = self.marker, 
                                 zorder=20,
                                 **self.plot_args_point)
        
        # dx, dy: distance between point and label in inches
        dx = np.cos(self.angle * np.pi / 180) * self.distance
        dy = np.sin(self.angle * np.pi / 180) * self.distance
        
        # transform (x,y) to figure coordinates in "inches" 
        x_s, y_s = self._saxes.axes.transData.transform((x,y))
        x_i, y_i = self._saxes.axes.figure.dpi_scale_trans.inverted().transform((x_s, y_s))
        
        # translate by (dx, dy) and transform back to data coordinates
        x1, y1 = self._saxes.axes.transData.inverted().transform(
            self._saxes.axes.figure.dpi_scale_trans.transform((x_i + dx, y_i + dy)))
        
        self.plot_args_label = default_plot_args_label | self.plot_args_label
        self._saxes.axes.text(x1, y1, self.label, 
                              zorder = 30,
                              **self.plot_args_label)