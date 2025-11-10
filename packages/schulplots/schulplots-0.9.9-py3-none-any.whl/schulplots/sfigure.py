from dataclasses import dataclass, field
from typing import Optional, Any, TYPE_CHECKING, IO, Literal
from os import PathLike

import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from matplotlib.lines import Line2D
import numpy as np

from .types import cm, Size

if TYPE_CHECKING:
    from .saxes import SAxes


try:
    from icecream import ic  # pyright: ignore[reportMissingImports]
except ImportError:  # Graceful fallback if IceCream isn't installed.
    ic = lambda *a: None if not a else (a[0] if len(a) == 1 else a)  # noqa


@dataclass
class SFigureModel:
    width: Size = Size(21.0 * cm)
    height: Size = Size(29.7 * cm)
    grid: Size = Size(0.5 * cm)
    grid_options: dict[str, Any] = field(
        default_factory=lambda: dict(alpha=0.2, lw=0.5)
    )
    output_file: Optional[str | PathLike[str] | IO[bytes]] = None
    dpi: int = 300
    output_format: Literal["png", "pdf", "svg"] | None = None
    # action: FigAction = FigAction.INTERACT


class SFigure(SFigureModel):
    saxes: list["SAxes"]
    figure: Figure

    def __init__(self, *args, f: Optional[Figure] = None, **kwargs):
        super().__init__(*args, **kwargs)
        self.saxes = []
        self.set_figure(f)

    def set_figure(self, f: Optional[Figure] = None):
        if f is None:
            f = plt.figure()
        self.figure = f
        self.figure.set_size_inches((self.width, self.height))
        self.draw_grid(**self.grid_options)

    def draw_grid(self, **kwargs):
        xx = np.arange(0, self.width + self.grid, self.grid)
        yy = np.arange(0, self.height + self.grid, self.grid)
        x_min = min(xx)
        x_max = max(xx)
        y_min = min(yy)
        y_max = max(yy)
        for x in xx:
            self.figure.add_artist(
                Line2D(
                    (x, x),
                    (y_min, y_max),
                    transform=self.figure.dpi_scale_trans,
                    **kwargs,
                )
            )
        for y in yy:
            self.figure.add_artist(
                Line2D(
                    (x_min, x_max),
                    (y, y),
                    transform=self.figure.dpi_scale_trans,
                    **kwargs,
                )
            )

    def add_axes(self, axes: "SAxes"):
        # axes.setup(self.figure, left, bottom)
        self.saxes.append(axes)

    def __enter__(self) -> "SFigure":
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        for sax in self.saxes:
            sax.finalize()
        if self.output_file is None:
            plt.show()
        else:
            self.figure.savefig(
                self.output_file, dpi=self.dpi, format=self.output_format
            )
