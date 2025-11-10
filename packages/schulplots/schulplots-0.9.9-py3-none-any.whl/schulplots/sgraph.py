from dataclasses import dataclass, field
from typing import Optional, Any, Union, ClassVar
from enum import Enum, unique

import numpy as np
from .converter import register_model, register_impl
try:
    from icecream import ic # pyright: ignore[reportMissingImports]
except ImportError:  # Graceful fallback if IceCream isn't installed.
    ic = lambda *a: None if not a else (a[0] if len(a) == 1 else a)  # noqa

from .saxes import SAxes
from .utils.math_expression import MathExpression

@unique
class DiscontinuityBelongsTo(Enum):
    GREATER = "x>x0"
    SMALLER = "x<x0"
    NONE    = "none"
@dataclass 
class Discontinuity:
    x0: float
    belongs_to: DiscontinuityBelongsTo = DiscontinuityBelongsTo.GREATER

@register_model  
@dataclass
class SGraphModel:
    class_id: ClassVar[str] = "Graph"
    function: Union[MathExpression, list[MathExpression]]
    label: Optional[str] = None
    plot_args: dict[str, Any] = field(default_factory=dict)
    discontinuities: list[Discontinuity] = field(default_factory=list)
    condition   : Optional[MathExpression] = None
    max_y: float = 100
    min_y: float = -100
    var_prefix:str = ""
    def __post_init__(self):
        if not isinstance(self.function, list):
            self.function = [self.function]
        # print(self.function, type(self.function[0]))
        if self.label is None:
            self.label = None
            #self.label = self.function[0]

@register_impl
class SGraph(SGraphModel):
    _saxes: SAxes
    _cond_array: Optional[np.ndarray]
    _ys: list[np.ndarray]
    
    def __init__(self, saxes: SAxes, *args, **kwargs):
        self._saxes = saxes
        self._cond_array = None
        self._ys = [] 
        super().__init__(*args, **kwargs)
        self._current_color = "black"
        self.set_saxes(saxes)
        
            
        
    def set_saxes(self, saxes: SAxes):
        self._saxes = saxes
        self.x = self._saxes._x
        self._eval_functions()
        self._eval_condition()
        self.plot()
        
    def plot(self, **kwargs):
        args = self.plot_args.copy()
        args.update(kwargs)
        y = self._ys[0]
        if self._cond_array is not None:
            y[~self._cond_array] = np.nan
        
        line = self._saxes.plot(self.x, y, label=self.label, zorder=10, **args)[-1]
        self._current_color = line.get_color()
        length, = self.x.shape
        for dc in self.discontinuities:
            idx = int(np.argmin(np.abs(self.x - dc.x0)))
            if dc.belongs_to == DiscontinuityBelongsTo.NONE:
                idx1 = min(length-1, idx + 1)
                idx2 = max(0, idx - 1)
                self._saxes.plot([self.x[idx1]], [y[idx1]], "o", zorder=20, mfc="white", color=self._current_color)
                self._saxes.plot([self.x[idx2]], [y[idx2]], "o", zorder=20, mfc="white", color=self._current_color)
                continue
            elif dc.belongs_to == DiscontinuityBelongsTo.GREATER:
                idx2 = min(length-1, idx + 1)
                idx1 = max(0, idx - 1)
            else:
                idx1 = min(length-1, idx + 1)
                idx2 = max(0, idx - 1)
            self._saxes.plot([self.x[idx1]], [y[idx1]], "o", zorder=20, mfc="white", color=self._current_color)
            self._saxes.plot([self.x[idx2]], [y[idx2]], "o", zorder=20, color=self._current_color)
            
       
        
    def get_locals(self) -> dict[str, np.ndarray]:
        d1: dict[str, Any] =  dict(x=self.x, y=self._ys[0])
        d1.update(self._saxes.axes_variables)
        return d1
    
    def _eval_condition(self):
        if self.condition is None:
            return
        cond_array = self.condition.evaluate(self.get_locals())
        if not isinstance(cond_array, np.ndarray):
            print(f"Warning: condition '{self.condition}' does not evaluate to array.")
            return
        if not cond_array.dtype == np.bool_:
            print(f"Warning: condition '{self.condition}' does not evaluate to boolean expression")
            return
        self._cond_array = cond_array
    
    def _eval_functions(self):
        for i, f in enumerate(self.function):
            y = f.evaluate(dict(x=self.x), 
                           self._saxes.axes_functions)
            y = np.array(y, dtype=np.float64)
            y = np.broadcast_to(y, self.x.shape).copy()
            y[y>self.max_y] = np.inf
            y[y<self.min_y] = -np.inf
            if self._cond_array is not None:
                y[~self._cond_array] = np.nan
            for dc in self.discontinuities:
                idx = np.argmin(np.abs(self.x - dc.x0))
                y[idx] = np.inf
            self._ys.append(y)
            


@register_model  
class FillBetweenModel(SGraphModel):
    class_id: ClassVar[str] = "Area"
@register_impl
class FillBetween(SGraph, FillBetweenModel):
    def set_saxes(self, saxes: SAxes):
        self._saxes = saxes
        self.x = self._saxes._x
        self._eval_functions()
        self._eval_condition()
        y = self._ys[0].copy()
        if self._cond_array is not None:
            y[~self._cond_array] = np.nan
        y2 = self._ys[1].copy()
        if self._cond_array is not None:
            y2[~self._cond_array] = np.nan
        
        self._saxes.axes.fill_between(self.x, y, y2, 
                                      label=self.label, **self.plot_args)
        tmp_cond = self.condition
        self.condition=None
        y = self._ys[0]
        y2 = self._ys[1]
        idx = np.argwhere(np.diff(np.sign(y - y2))).flatten()
        self.intersects = self.x[idx]
        update_dict= {f"{self.var_prefix}sect_x_{i}": value for (i,value) in enumerate(self.intersects)}
        self._saxes.axes_variables.update(update_dict)
        update_dict= {f"{self.var_prefix}sect_y_{i}": value.evaluate(dict(x=self.intersects)) for (i,value) in enumerate(self.function)}
        self.condition = tmp_cond
        self._saxes.axes_variables.update(update_dict)
        
        
    def get_closest_intersect(self, x:float):
        #ic(self.intersects)
        return self.intersects[np.argmin(np.abs(self.intersects - x))]

    def get_locals(self) -> dict[str, np.ndarray]:
        d1: dict[str, Any] =  dict(x=self.x, y1=self._ys[0], y2=self._ys[1])
        d1.update(self._saxes.axes_variables)
        return d1

