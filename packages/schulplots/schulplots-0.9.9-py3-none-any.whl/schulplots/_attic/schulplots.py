
#%%
from dataclasses import dataclass, field
from typing import Optional, Any, Iterable, Callable, Union
from types import CodeType
from collections.abc import Iterable
from functools import total_ordering
import re
from enum import Enum, auto

import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from matplotlib.lines import Line2D
from matplotlib.axes import Axes
from matplotlib.ticker import MultipleLocator
from matplotlib.transforms import ScaledTranslation
import numpy as np
from numpy.typing import ArrayLike

try:
    from icecream import ic
except ImportError:  # Graceful fallback if IceCream isn't installed.
    ic = lambda *a: None if not a else (a[0] if len(a) == 1 else a)  # noqa


cm = 1./2.54 

size_re= re.compile(r"(-?[\d\.]+)(\s*)([a-z]+)")
units = {"cm": 1./2.54, 
         "mm": 0.1/2.54,
         "in": 1.}
#%%

class Size(float):
    def __new__(self, value: Union[float, str]):
        if isinstance(value, str):
            if value.isnumeric():
                value = float(value)
            else:
                m = size_re.match(value)
                if m is None: 
                    raise ValueError("Invalid size")
                val, _, unit = m.groups()
                value = float(val) * units[unit]
        return float.__new__(self, value)
    def __init__(self, value: Union[float, str]):
        self._init_as = str(value)
    def __repr__(self):
        return self._init_as
    __str__ = __repr__

@dataclass(frozen=True)
class Point:
    x: Size
    y: Size
    def args(self):
        return self.x, self.y
    
#%%
class FigAction(Enum):
    INTERACT = auto()
    SAVE = auto()
#%%
@dataclass
class SFigureModel:
    width: Size = 21.0 * cm
    height: Size = 29.7 * cm
    grid: Size = 0.5 * cm
    grid_options: dict[str, Any] = field(default_factory=lambda: dict(alpha=0.2, lw=0.5))
    output_file: Optional[str] = None
    dpi: int = 300
    #action: FigAction = FigAction.INTERACT
        
class SFigure(SFigureModel):
    saxes: Iterable["SAxes"]
    figure: Optional[Figure]
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.saxes = []
        self.figure = None
    def set_figure(self, f: Optional[Figure] = None):
        if f is None:
            f = plt.figure()
        self.figure = f
        self.figure.set_size_inches((self.width, self.height))
        self.draw_grid(**self.grid_options)
    
    def draw_grid(self, **kwargs):
        xx = np.arange(0, self.width+self.grid, self.grid)
        yy = np.arange(0, self.height+self.grid, self.grid)
        x_min = min(xx)
        x_max = max(xx)
        y_min = min(yy)
        y_max = max(yy)
        for x in xx:
            self.figure.add_artist(Line2D((x,x), (y_min, y_max), transform = self.figure.dpi_scale_trans, **kwargs))
        for y in yy:
            self.figure.add_artist(Line2D((x_min, x_max), (y,y), transform = self.figure.dpi_scale_trans, **kwargs))
        
    def add_axes(self, axes: "SAxes", left: Size = 0, bottom: Size = 0):
        axes.setup(self.figure, left, bottom)
        self.saxes.append(axes)
    
    def __enter__(self) -> "SFigure":
        return self
    def __exit__(self,exc_type, exc_val, exc_tb):
        for sax in self.saxes:
            sax.finalize()
        if self.output_file is None:
            plt.show()
        else:
            self.figure.savefig(self.output_file, dpi=self.dpi)
        
@dataclass
class SAxesModel:
    x_min: float
    y_min: float
    width: Size = 10 * cm
    height: Size = 8 * cm
    x_label: str = "x"
    y_label: str = "y"
    x_tick_distance: float = 1
    y_tick_distance: float = 1
    unit:Size = 1*cm
    show_legend: bool = True
    legend_options: dict[str, Any] = field(default_factory=dict)    
    n_points = 3000
    x_label_offset: Point = Point(0,0)
    y_label_offset: Point = Point(0, 0)

    def __post_init__(self):
        self.x_max: float = self.x_min + self.width/self.unit
        self.y_max: float = self.y_min + self.height/self.unit
        self._x = np.linspace(self.x_min, self.x_max, self.n_points)
    
class SAxes(SAxesModel):
    axes: Optional[Axes] 
    axes_variables: dict[str, float] 
    
    def get_offset_x_ax(self, dx, dy):
        ax = self.axes
        tr1 = ax.get_yaxis_transform()
        tr2 = ax.figure.dpi_scale_trans.inverted()
        tr = tr1+tr2
        tx,ty = tr.transform((0,0))
        return tr.inverted().transform((tx+dx, ty+dy))
    
    def get_offset_y_ax(self, dx, dy):
        ax = self.axes
        tr1 = ax.get_xaxis_transform()
        tr2 = ax.figure.dpi_scale_trans.inverted()
        tr = tr1+tr2
        tx,ty = tr.transform((0,0))
        return tr.inverted().transform((tx+dx, ty+dy))
    
    def setup(self, figure: Figure, left: Size, bottom: Size):
        trf = figure.dpi_scale_trans + figure.transFigure.inverted()
        aw, ah = trf.transform((self.width, self.height))
        al, ab = trf.transform((left, bottom))
        rect = (al, ab, aw, ah)
        #ic(rect)
        #ic(self)
        self.axes_variables = dict()
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
        
        
        #self.axes.xaxis.label.set_position((1,0))
        #ic(self.axes.xaxis.get_label_coords())
        #self.axes.xaxis.set_label_coords(*self.x_label_pos.args())
        #my_transform = ScaledTranslation(1, 0.5, self.axes.get_yaxis_transform())
        #self.axes.xaxis.set_label_coords(*self.x_label_pos.args(), my_transform)
        #px,py = ic(self.axes.xaxis.label.get_position())

        #self.axes.yaxis.label.set_position((self.y_label_pos.x, self.y_label_pos.y))
        #my_transform = ScaledTranslation(0.3, 0.98, self.axes.get_xaxis_transform())
        #self.axes.yaxis.set_label_coords(*self.y_label_pos.args(), transform=my_transform)
        #px,py = ic(self.axes.yaxis.label.get_position())
    
    def finalize(self):
        if self.show_legend:
            self.axes.legend(**self.legend_options)

    def plot(self, *args, **kwargs):
        self.axes.plot(*args, **kwargs)
    def legend(self, *args, **kwargs):
        self.axes.legend(*args, **kwargs)
        
    
@dataclass
class VLineModel:
    x: float = np.inf
    x_var: str = ""
    y_min: float = 0
    y_max: float = 1
    plot_args: dict[str, Any] = field(default_factory=lambda: dict(alpha=0.5))
class VLine(VLineModel):
    _saxes: Optional[SAxes]
    def __init__(self, *args, **kwargs):
        self._saxes = None
        super().__init__(*args, **kwargs)
    def set_saxes(self, saxes: SAxes):
        self._saxes = saxes
        if self.x != np.inf:
            x = self.x
        if self.x_var:
            x = eval(self.x_var, {}, self._saxes.axes_variables)
        self._saxes.axes.axvline(x=x,ymin=self.y_min, ymax=self.y_max, 
                                 **self.plot_args)
@dataclass
class VSpanModel:
    x0: float
    x1: float
    y_min: float = 0
    y_max: float = 1
    plot_args: dict[str, Any] = field(default_factory=lambda: dict(alpha=0.3, lw=0))
class VSpan(VSpanModel):
    _saxes: Optional[SAxes]
    def __init__(self, *args, **kwargs):
        self._saxes = None
        super().__init__(*args, **kwargs)
    def set_saxes(self, saxes: SAxes):
        self._saxes = saxes
        self._saxes.axes.axvspan(xmin=self.x0, xmax=self.x1,ymin=self.y_min, 
                                 ymax=self.y_max, **self.plot_args)
        

@dataclass
class SGraphModel:
    function: Union[str, list[str]]
    label: Optional[str] = None
    plot_args: dict[str, Any] = field(default_factory=dict)
    condition: Optional[str] = None
    max_y: float = 100
    min_y: float = -100
    var_prefix:str = ""
    
    def __post_init__(self):
        if self.label is None:
            self.label = self.function[0]
 
class SGraph(SGraphModel):
    _function_expr: list[str]
    _function_code: list[CodeType]
    _func: list[Callable]
    _saxes: Optional[SAxes]
    _condition_expr: str
    _condition_code: CodeType
    _cond: Callable
    
    def __init__(self, *args, **kwargs):
        self._saxes = None
        self._cond_array = None
        super().__init__(*args, **kwargs)
            
    def set_saxes(self, saxes: SAxes):
        self._saxes = saxes
        #self._condition_expr = ""
        #self.condition = None
        self._compile_condition()
        self._saxes.plot(self.x, self.y, label=self.label, **self.plot_args)
        
        
    def plot(self, **kwargs):
        args = self.plot_args.copy()
        args.update(kwargs)
        self._saxes.plot(self.x, self.y, label=self.label, **args)
        
    def get_locals(self) -> dict[str, np.ndarray]:
        return dict(x=self.x, y=self.y)
    
    def _compile_condition(self):
        if self._condition_expr is None:
            return
        self._condition_code = compile(self._condition_expr, "<condition expression string>", "eval")
        def _cond():
            ll = locals()
            ll.update(np.__dict__)
            ll.update(self.get_locals())
            return eval(self._condition_code, {}, ll)
        self._cond = _cond
        self._cond_array = _cond()
        
    @property
    def condition(self)->str:
        return self._condition_expr
    @condition.setter
    def condition(self, condition_expr):
        #ic("in condition setter")
        self._condition_expr = condition_expr
        if self._saxes is None:
            ic("do not set condition because self._saxes is None")
            return            
        if condition_expr is None:
            ic("condition expr is None")
            self._cond_array = np.full_like(self._saxes._x, True, dtype=np.bool_)
            return
        self._compile_condition()
    @property
    def function(self)->list[str]:
        return self._function_expr
    @function.setter
    def function(self, func_expr: Union[str, list[str]]):
        if not isinstance(func_expr, list):
            func_expr = [func_expr]
        self._function_expr = []
        self._function_code = []
        self._func = []
        for f in func_expr:
            f = str(f) # f could be an integer
            self._function_expr.append(f)
            #ic(f)
            f_code = compile(f, "<function expression string>", "eval")
            self._function_code.append(f_code)
            ll = np.__dict__
            # using the default argument is required to fix the f_code to the specific
            # value at this point in time.
            # see: https://stackoverflow.com/a/54289183
            def ff(x, f_code=f_code):
                ll = locals()
                ll.update(np.__dict__)
                return eval(f_code, {}, ll)
            self._func.append(ff)        
    @property
    def x(self) -> np.ndarray:
        if  self._cond_array is None:
            return self._saxes._x
        else:
            #ic("XXX", self._cond_array)
            return self._saxes._x[self._cond_array]

    @property
    def y(self) ->np.ndarray:
        y = self._func[0](self.x)
        y[y>self.max_y] = np.inf
        y[y<self.min_y] = -np.inf
        return y


class FillBetween(SGraph):
    def set_saxes(self, saxes: SAxes):
        self._saxes = saxes
        self.condition = self._condition_expr
        self._saxes.axes.fill_between(self.x, self.y, self.y2, 
                                      label=self.label, **self.plot_args)
        tmp_cond = self.condition
        self.condition=None
        greater = self.y > self.y2
        self.intersects = self.x[np.where(greater[:-1] ^ greater[1:])[0]]
        #ic(self.intersects)
        #ic(self._func[0](self.intersects))
        update_dict= {f"{self.var_prefix}sect_x_{i}": value for (i,value) in enumerate(self.intersects)}
        self._saxes.axes_variables.update(update_dict)
        update_dict= {f"{self.var_prefix}sect_y_{i}": value for (i,value) in enumerate(self._func[0](self.intersects))}
        self.condition = tmp_cond
        self._saxes.axes_variables.update(update_dict)
        
        
    def get_closest_intersect(self, x:float):
        #ic(self.intersects)
        return self.intersects[np.argmin(np.abs(self.intersects - x))]

    def get_locals(self) -> dict[str, np.ndarray]:
        return dict(x=self.x, y1=self.y, y2=self.y2)

    @property
    def y2(self) ->np.ndarray:
        return self._func[1](self.x)

@dataclass
class AxesWithGraphs:
    axes: SAxes
    graphs: list[SGraph] = field(default_factory=list)
    areas: list[FillBetween] = field(default_factory=list)
    vlines: list[VLine] = field(default_factory=list)
    vspans: list[VSpan] = field(default_factory=list)
    left: Size = 0
    bottom: Size = 0
    templates: dict = field(default_factory=dict)
    
    def setup(self):
        for g in self.graphs:
            g.set_saxes(self.axes)
        for a in self.areas:
            a.set_saxes(self.axes)
        for a in self.vlines:
            a.set_saxes(self.axes)
        for a in self.vspans:
            a.set_saxes(self.axes)

@dataclass
class FigureDescription:
    figure: SFigure
    axes_descriptors: list[AxesWithGraphs]
    
    def create_figure(self):
        with self.figure:
            self.figure.set_figure()
            for ax in self.axes_descriptors:
                self.figure.add_axes(ax.axes, left=ax.left, bottom=ax.bottom)
                ax.setup()    


from cattrs.preconf.pyyaml import make_converter
converter = make_converter(omit_if_default=True)
converter.register_structure_hook(Size, lambda val, _: Size(val))
converter.register_unstructure_hook(Size, str)
def structure_list_of_strings(value, _):
    if isinstance(value, str):
        value = [value]
    return value
converter.register_structure_hook(Union[str, list[str]], structure_list_of_strings)
converter.register_structure_hook(FigAction, lambda val, _: FigAction._member_map_[val])
converter.register_unstructure_hook(FigAction, lambda s: s.name)
print("reload...")      
if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(
        prog="schulplots.py", 
        description="Create function plots styled similar to the conventions used in German schools."
    )
    parser.add_argument("filename", help="Description of the figure, in YAML format")
    parser.add_argument("--output", "-o", help="name out output file. If not provided, an interactive window is shown.")

    args = parser.parse_args()
    fdsc = converter.loads(open(args.filename, "r").read(), FigureDescription)
    if args.output is not None:
        fdsc.figure.output_file = args.output
    fdsc.create_figure()
    
    if False:
        ax1 = SAxes(-1, -1, Size("8cm"), Size("10cm"), show_legend=True, unit=Size("2cm"))
        g1 = SGraph("sin(x)", label= "$\sin(x)$")
        g2 = SGraph("x**2", label="$x^2$")

        f1 = FillBetween(["sin(x)", "x**2"], condition="y1 >= y2",
                         plot_args=dict(alpha=0.2),
                         label="$\int_0^{x_0} sin(x) - x^2 \, dx$")
        awg1 = AxesWithGraphs(ax1, [g1,g2], [f1], left=Size("1cm"), bottom=Size("1cm"))
        
        
        
        ax2 = SAxes(-3, -2, Size("8cm"), Size("10cm"), show_legend=True)
        g3 = SGraph("x**3", label="$x^3$")
        g4 = SGraph("1/x", label="$1/x$")
        
        f2 = FillBetween(["minimum(x**3, 1/x)", "0*x"], condition="x>0", label="A")
        awg2 = AxesWithGraphs(ax2, [g3, g4],[f2], left=Size("9.5 cm"), bottom=Size("1cm"))
        
        fdsc = FigureDescription(SFigure(width=Size("18 cm"), height=Size("12 cm")), [awg1, awg2])
        print(f1.get_closest_intersect(1))

        #print("XXXXXXXXX")
        print(converter.dumps(fdsc))
        
        

# %%
