
from .converter import converter
from .figure_description import FigureDescription
from .types import Size, cm
import argparse
from os import path, stat
from typing import Optional

try:
    from icecream import ic # pyright: ignore[reportMissingImports]
except ImportError:  # Graceful fallback if IceCream isn't installed.
    ic = lambda *a: None if not a else (a[0] if len(a) == 1 else a)  # noqa

def generate_plot(infile: str, outfile: Optional[str] = None):
    with open(infile, "r", encoding="utf-8") as f:
        fdsc = converter.loads(f.read(), FigureDescription)
        fdsc.figure.output_file = outfile
        fdsc.create_figure()
def main():
    parser = argparse.ArgumentParser(
        prog="schulplots", 
        description="Create function plots styled similar to the conventions used in German schools.\n"\
            "For documentation, see https://schulplots.hans-aschauer.de"
    )
    parser.add_argument("filename", help="Description of the figure, in YAML format")
    parser.add_argument("--output", "-o", 
                        help="Name out output file. If not provided (and --show is "\
                             "not given), store the figure in the current working "\
                             "directory.")
    parser.add_argument("--show", "-s", help="Show plot in interactive window. May not be used with --output.",
                        action="store_true", default=False)

    args = parser.parse_args()
    if args.output is not None and args.show:
        parser.print_help()
    elif args.output is not None and not args.show:
        generate_plot(args.filename, args.output)
        #fdsc.figure.output_file = args.output
    elif args.output is None and args.show:
        generate_plot(args.filename, None)
        #fdsc.figure.output_file = None
    elif args.output is None and not args.show:
        bname, _ = path.splitext(path.basename(args.filename))
        generate_plot(args.filename, bname + ".png")
        #fdsc.figure.output_file = bname + ".png"
        
    else:
        raise ValueError("Logic error: this should not happen")
    #fdsc.create_figure()

output_yaml = """
figure:
  height: {height}
  width: {width}
axes_descriptors:
- axes:
    height: {aheight}
    width: {awidth}
    x_min: {x_min}
    y_min: {y_min}
    show_legend: false
  bottom: 0.5cm
  left: 0.5cm
  items:"""

graph_yaml = """  - type: Graph
    function: {function}
    label: {function_label}"""

def create():
    parser = argparse.ArgumentParser(
        prog="schulplots-create", 
        description="Create a basic schulplots YAML file to get you started."
    )
    parser.add_argument("filename", help="Description of the figure, in YAML format")
    parser.add_argument("--function", "-f", action="append", 
                        default=["sin(x)"],
                        help = "Specify function to plot, e.g. '3*sin(x)'")
    parser.add_argument("--size", "-s", default="10cmx6cm",
                        help="Size of the figure (e.g. 8cmx5cm)")
    parser.add_argument("--force", action="store_true", default=False,
                        help="If set, overwrite output if it exists.")
    args = parser.parse_args()
    if len(args.function) > 1:
        del args.function[0] # remove default if function provided
    
    # check if file exists
    file_exists = True
    try:
        stat(args.filename)
    except FileNotFoundError:
        file_exists = False
    if file_exists and not args.force:
        print(f"Outup file {args.filename} exists. Provide '--force' option to overwrite it.")    
    else:
        with open(args.filename, "w") as f:    
            wh = args.size.split("x")
            assert len(wh) == 2
            w = Size(wh[0])
            h = Size(wh[1])
            
            print(output_yaml.format(
                width=w, height=h,
                awidth = Size.as_cm(w-1.5*cm), 
                aheight = Size.as_cm(h-1.5*cm),
                x_min = round(-(w/cm-1) / 2, 2),
                y_min = round(-(h/cm-1) / 2, 2)
            ), file=f)
            for i, function in enumerate(args.function):
                print(graph_yaml.format(
                    function=function,
                    function_label = f"$f_{{{i}}}(x)$"
                ),file=f)
            