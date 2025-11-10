from dataclasses import dataclass, field
from typing import Optional, Any, TYPE_CHECKING, Callable

from matplotlib.axes import Axes
from matplotlib.ticker import MultipleLocator
import numpy as np

from .types import cm, Size, Point

if TYPE_CHECKING:
    from .sfigure import SFigure
    from .utils.math_expression import MathExpression
    from .utils.math_parser import vardict_t
try:
    from icecream import ic # pyright: ignore[reportMissingImports]
except ImportError:  # Graceful fallback if IceCream isn't installed.
    ic = lambda *a: None if not a else (a[0] if len(a) == 1 else a)  # noqa

        
@dataclass
class SAxesModel:
    x_min: float
    #x_max: float = field(init=False) # = self.x_min + self.width/self.unit
    y_min: float
    #y_max: float = field(init=False) # = self.y_min + self.height/self.unit
    width: Size = Size(10 * cm)
    height: Size = Size(8 * cm)
    x_label: str = "x"
    y_label: str = "y"
    x_tick_distance: float = 1
    y_tick_distance: float = 1
    unit:Size = Size(1*cm)
    show_legend: bool = True
    show_x_tick_labels: bool = True
    show_y_tick_labels: bool = True
    legend_options: dict[str, Any] = field(default_factory=dict)    
    n_points: int = 3000
    x_label_offset: Point = Point(Size(0.5*cm), Size(0))
    y_label_offset: Point = Point(Size(0),Size(0.5*cm))

    def __post_init__(self):
        self.x_max: float = self.x_min + self.width/self.unit
        self.y_max: float = self.y_min + self.height/self.unit
        self._x = np.linspace(self.x_min, self.x_max, self.n_points)
    
class SAxes(SAxesModel):
    axes: Axes
    axes_variables: dict[str, float] 
    axes_functions: dict[str, Callable]
    _sfigure: "SFigure"
    
    def __init__(self, figure: "SFigure", left: Size, bottom: Size, 
                 *args, **kwargs):
        self._sfigure = figure
        print("XXX", args, len(args), kwargs)
        super().__init__(*args, **kwargs)
        self.axes_variables = dict(pi=np.pi, e=np.e)
        self.axes_functions = {}
        self.setup(left, bottom)
        self._sfigure.add_axes(self)
    def get_offset_x_ax(self, dx, dy):
        ax = self.axes
        tr1 = ax.get_yaxis_transform()
        assert ax.figure is not None
        tr2 = ax.figure.dpi_scale_trans.inverted()
        tr = tr1+tr2
        tx,ty = tr.transform((0,0))
        return tr.inverted().transform((tx+dx, ty+dy))
    
    def get_offset_y_ax(self, dx, dy):
        ax = self.axes
        tr1 = ax.get_xaxis_transform()
        assert ax.figure is not None
        tr2 = ax.figure.dpi_scale_trans.inverted()
        tr = tr1+tr2
        tx,ty = tr.transform((0,0))
        return tr.inverted().transform((tx+dx, ty+dy))
    
    def setup(self, left: Size, bottom: Size):
        figure = self._sfigure.figure
        trf = figure.dpi_scale_trans + figure.transFigure.inverted()
        aw, ah = trf.transform((self.width, self.height))
        al, ab = trf.transform((left, bottom))
        rect = (al, ab, aw, ah)
        #ic(rect)
        #ic(self)
        self.axes = figure.add_axes(rect)
        self.axes.set_xlim(self.x_min, self.x_max)
        self.axes.set_ylim(self.y_min, self.y_max)
        
        self.axes.set_aspect("equal")
        self.axes.set_xlabel(self.x_label)
        self.axes.set_ylabel(self.y_label)
        maj_pos_y = MultipleLocator(base=self.x_tick_distance)
        maj_pos_x = MultipleLocator(base=self.y_tick_distance)

        self.axes.xaxis.set(major_locator=maj_pos_x)
        self.axes.yaxis.set(major_locator=maj_pos_y)
        self.axes.tick_params(axis='both', which='minor', length=0)   # remove minor tick lines

        spine_x = self.axes.spines["bottom"]
        spine_y = self.axes.spines["left"]
        spine_x.set_position(('data', 0))
        spine_y.set_position(('data', 0))
        self.axes.plot(1, 0, ">k", transform=self.axes.get_yaxis_transform(), clip_on=False)
        self.axes.plot(0, 1, "^k", transform=self.axes.get_xaxis_transform(), clip_on=False)

        if self.show_x_tick_labels is False:
            self.axes.set_xticklabels([])
        if self.show_y_tick_labels is False:
            self.axes.set_yticklabels([])

        self.axes.spines['top'].set_visible(False)
        self.axes.spines['right'].set_visible(False)

        dx, dy = self.x_label_offset.args()
        dx1, dy1 = self.get_offset_x_ax(dx, dy)
        self.axes.xaxis.set_label_coords(1+dx1, 0+dy1, 
                                         transform=self.axes.get_yaxis_transform())
        self.axes.yaxis.label.set(rotation="horizontal")
        dx, dy = self.y_label_offset.args()
        dx1, dy1 = self.get_offset_y_ax(dx, dy)
        self.axes.yaxis.set_label_coords(0+dx1, 1+dy1, 
                                         transform=self.axes.get_xaxis_transform())
        
    def evaluate(self, 
                 expr: "MathExpression", 
                 vars: Optional["vardict_t"] = None, 
                 functions: Optional["vardict_t"]= None):
        if vars is None:
            vars = {}
        vars = vars | self.axes_variables
        if functions is None:
            functions = {}
        functions = functions | self.axes_functions
        try:
            res = expr.evaluate(vars, functions)
        except Exception as e:
            print(f"Warning: got exception '{e}' in evaluation of '{expr}'.")
            res = 0
        return res
        
    
    def finalize(self):
        if self.show_legend:
            legend=self.axes.legend(**self.legend_options)
            legend.set_zorder(30)

    def plot(self, *args, **kwargs):
        return self.axes.plot(*args, **kwargs)
    def legend(self, *args, **kwargs):
        return self.axes.legend(*args, **kwargs)
        
