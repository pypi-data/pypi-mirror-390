from dataclasses import dataclass, field, fields
from typing import Any

try:
    from icecream import ic  # pyright: ignore[reportMissingImports]
except ImportError:  # Graceful fallback if IceCream isn't installed.
    ic = lambda *a: None if not a else (a[0] if len(a) == 1 else a)  # noqa

from .saxes import SAxes, SAxesModel
from .sgraph import SGraphModel , FillBetween, SGraph
from .lines import VLineModel, VSpanModel, VLine, VSpan
from .types import Size
from .sfigure import SFigure
from .functions import SFunction
from .utils.math_expression import MathExpression
from .converter import AxesAddable, impl_for_type

def to_dict(datainstance:Any) -> dict:
    dd = {f.name: getattr(datainstance, f.name) for f in fields(datainstance)}
    return dd


@dataclass
class AxesWithGraphs:
    axes: SAxesModel
    graphs: list[SGraphModel] = field(default_factory=list)
    areas: list[SGraphModel] = field(default_factory=list)
    vlines: list[VLineModel] = field(default_factory=list)
    vspans: list[VSpanModel] = field(default_factory=list)
    functions: dict[str, MathExpression] = field(default_factory=dict)
    items: list[AxesAddable] = field(default_factory=list)
    left: Size = Size(0)
    bottom: Size = Size(0)
    templates: dict = field(default_factory=dict)
    
    def setup(self, saxes: SAxes):
        for name, func in self.functions.items():
            SFunction(saxes, function=func, name=name)
        for a in self.items:
            impl_for_type(a.class_id)(saxes, **to_dict(a))
        for g in self.graphs:
            SGraph(saxes, **to_dict(g))
            #g.set_saxes(self.axes)
        for a in self.areas:
            FillBetween(saxes, **to_dict(a))
            #a.set_saxes(self.axes)
        for a in self.vlines:
            #pprint(to_dict(a))
            VLine(saxes, **to_dict(a))
            #a.set_saxes(self.axes)
        for a in self.vspans:
            VSpan(saxes, **to_dict(a))
            #a.set_saxes(self.axes)

@dataclass
class FigureDescription:
    figure: SFigure
    axes_descriptors: list[AxesWithGraphs]
    
    def create_figure(self):
        with self.figure:
            #self.figure.set_figure()
            for ax in self.axes_descriptors:
                saxes = SAxes(self.figure, ax.left, ax.bottom, 
                              **to_dict(ax.axes))
                #self.figure.add_axes(ax.axes, left=ax.left, bottom=ax.bottom)
                ax.setup(saxes)    
