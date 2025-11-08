#from __future__ import annotations

import itertools
import tempfile
from contextlib import contextmanager
from pathlib import Path

import cairo
import numpy as np
from manim import VGroup, VMobject, constants
from manim.utils.family import extract_mobject_family_members

CAIRO_LINE_WIDTH_MULTIPLE: float = 0.01

__all__ = ["create_svg_from_vmobject", "create_svg_from_vgroup", "_get_cairo_context", "extract_mobject_family_members", "_create_svg_from_vmobject_internal"]

@contextmanager
def _get_cairo_context(file_name: str | Path, style) -> cairo.Context:
    view = style.view
    scale = view['scale']

    pw = int(view['width'])
    ph = int(view['height'])

    surface = cairo.SVGSurface(file_name, pw, ph)
    ctx = cairo.Context(surface)
    ctx.scale(pw, ph)
    ctx.set_matrix(cairo.Matrix(scale, 0, 0, -scale, view['xZero'], view['yZero']))
    yield ctx
    surface.finish()

def _set_cairo_context_color(ctx: cairo.Context, rgbas: np.ndarray, vmobject: VMobject):
    if len(rgbas) == 1:
        ctx.set_source_rgba(*rgbas[0])
    else:
        points = vmobject.get_gradient_start_and_end_points()
        pat = cairo.LinearGradient(*itertools.chain(*(point[:2] for point in points)))
        step = 1.0 / (len(rgbas) - 1)
        offsets = np.arange(0, 1 + step, step)
        for rgba, offset in zip(rgbas, offsets):
            pat.add_color_stop_rgba(offset, *rgba)
        ctx.set_source(pat)

def _apply_stroke(ctx: cairo.Context, vmobject: VMobject, style = None):
    width = vmobject.get_stroke_width()
    if width == 0: return
    
    _set_cairo_context_color(ctx, vmobject.get_stroke_rgbas(), vmobject)
    ctx.set_line_width(width * CAIRO_LINE_WIDTH_MULTIPLE)

    linecap = {
        None: cairo.LINE_CAP_BUTT,
        constants.CapStyleType.AUTO: cairo.LINE_CAP_BUTT,
        constants.CapStyleType.BUTT: cairo.LINE_CAP_BUTT,
        constants.CapStyleType.ROUND: cairo.LINE_CAP_ROUND,
        constants.CapStyleType.SQUARE: cairo.LINE_CAP_SQUARE
    }
    cap = vmobject.get_cap_style() if hasattr(vmobject, 'cap_style') else None
    ctx.set_line_cap(linecap[cap])
        
    joint_map = {
        None: cairo.LINE_JOIN_MITER,
        constants.LineJointType.AUTO: cairo.LINE_JOIN_MITER,
        constants.LineJointType.BEVEL: cairo.LINE_JOIN_BEVEL,
        constants.LineJointType.MITER: cairo.LINE_JOIN_MITER,
        constants.LineJointType.ROUND: cairo.LINE_JOIN_ROUND
    }
    
    ctx.set_line_join(joint_map[vmobject.joint_type])
    ctx.stroke_preserve()

def _apply_fill(ctx: cairo.Context, vmobject: VMobject, style = None):
    _set_cairo_context_color(ctx, vmobject.get_fill_rgbas(), vmobject)
    ctx.fill_preserve()

def _create_svg_from_vmobject_internal(vmobject: VMobject, ctx: cairo.Content, style = None):
    points = vmobject.points
    if len(points) == 0: return

    ctx.new_path()
    
    subpaths = vmobject.gen_subpaths_from_points_2d(points)
    for subpath in subpaths:
        quads = vmobject.gen_cubic_bezier_tuples_from_points(subpath)
        ctx.new_sub_path()
        start = subpath[0]
        ctx.move_to(*start[:2])
        for _p0, p1, p2, p3 in quads:
            ctx.curve_to(*p1[:2], *p2[:2], *p3[:2])
        if vmobject.consider_points_equals_2d(subpath[0], subpath[-1]):
            ctx.close_path()

    _apply_fill(ctx, vmobject, style = style)
    _apply_stroke(ctx, vmobject, style = style)

def create_svg_from_vmobject(vmobject: VMobject, file_name: str | Path = None, style = None) -> Path:
    if file_name is None:
        file_name = tempfile.mktemp(suffix=".svg")
    file_name = Path(file_name).absolute()

    with _get_cairo_context(file_name) as ctx:
        for _vmobject in extract_mobject_family_members([vmobject], True, True):
            _create_svg_from_vmobject_internal(_vmobject, ctx, style = style)
            
    return file_name

def create_svg_from_vgroup(vgroup: VGroup, file_name: str | Path = None, style = None) -> Path:
    if file_name is None:
        file_name = tempfile.mktemp(suffix=".svg")
    file_name = Path(file_name).absolute()
    
    with _get_cairo_context(file_name) as ctx:
        for _vmobject in extract_mobject_family_members(vgroup, True, True):
            _create_svg_from_vmobject_internal(_vmobject, ctx, style = style)

    return file_name
