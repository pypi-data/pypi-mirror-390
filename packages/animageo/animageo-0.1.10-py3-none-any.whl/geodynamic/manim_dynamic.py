import re
import os
import json
import numpy as np
import tempfile
from contextlib import contextmanager

from .geo import construction as geo
from manim import *
from manim.utils.space_ops import normalize, angle_between_vectors
from manim.utils.iterables import adjacent_n_tuples, adjacent_pairs

from .parsers.svg_parser import *
from .parsers import short_parser, ggb_parser

import xml.etree.ElementTree as ET

#--------------------------------------------------------------------------
    # Преобразуем все точки в numpy массивы
    
def round_corners_vmobject(points, radius=0.5, components_per_rounded_corner=8):
    """
    Создает VMobject со скругленными углами для незамкнутой ломаной
    
    Parameters:
    points: список точек ломаной
    radius: радиус скругления углов
    components_per_rounded_corner: количество точек для аппроксимации дуги скругления
    """
    points = [np.array(p) for p in points]
    
    if len(points) < 3 or radius <= 0:
        return VMobject().set_points_as_corners(points)
    
    result = VMobject()
    new_points = []
    
    # Обрабатываем первую точку
    new_points.append(points[0])
    
    # Обрабатываем промежуточные точки со скруглением
    for i in range(1, len(points) - 1):
        v_prev = points[i-1]
        v_curr = points[i]
        v_next = points[i+1]
        
        # Векторы от текущей точки к соседним
        vec_in = v_prev - v_curr
        vec_out = v_next - v_curr
        
        # Нормализуем векторы
        norm_in = np.linalg.norm(vec_in)
        norm_out = np.linalg.norm(vec_out)
        
        if norm_in < 1e-6 or norm_out < 1e-6:
            new_points.append(v_curr)
            continue
            
        unit_in = vec_in / norm_in
        unit_out = vec_out / norm_out
        
        # Вычисляем угол между векторами
        dot_product = np.clip(np.dot(unit_in, unit_out), -1.0, 1.0)
        angle = np.arccos(dot_product)
        
        # Вычисляем расстояние от вершины до точек скругления
        d = radius / np.tan(angle / 2)
        
        # Ограничиваем d чтобы не выходить за границы отрезков
        d = min(d, norm_in * 0.75, norm_out * 0.75)
        
        # Точки начала и конца скругления
        start_round = v_curr + unit_in * d
        end_round = v_curr + unit_out * d
        
        # Определяем направление дуги с помощью векторного произведения
        cross_vec = np.cross(unit_in, unit_out)
        sign = np.sign(cross_vec[2]) if abs(cross_vec[2]) > 1e-8 else 1.0
        
        # Создаем дугу скругления
        arc = ArcBetweenPoints(
            start_round, 
            end_round, 
            angle=-sign * (PI - angle),
            num_components=components_per_rounded_corner
        )
        
        # Добавляем отрезок до начала скругления
        if not np.allclose(new_points[-1], start_round):
            new_points.append(start_round)
        
        # Добавляем точки дуги (пропускаем первую точку дуги, так как она уже добавлена)
        new_points.extend(arc.points[1:])
    
    # Обрабатываем последнюю точку
    new_points.append(points[-1])
    
    # Устанавливаем точки для VMobject
    result.set_points_as_corners(new_points)
    return result

    
#--------------------------------------------------------------------------

def isnan(x):
    if isinstance(x, (int, float)): return False
    else:
        try:
            y = float(x)
            return False
        except:
            return True
 
def rgba(arr):
    if isinstance(arr, str): arr = arr.split(' ')
    
    try:
        if len(arr) == 1:
            return ManimColor(arr[0]).to_rgb()
        elif len(arr) == 2:
            if arr[1] is None: return ManimColor(arr[0]).to_rgb()
            else: return ManimColor(arr[0], arr[1]).to_rgba()
        elif len(arr) == 3:
            return ManimColor(arr).to_rgb()
        elif len(arr) == 4:
            return ManimColor(arr).to_rgba()
    except Exception as e:
        #print('RBGA:', arr)
        #print('EXCEPTION:', e)
        return None
    return None

def equal(arr1, arr2, eps = None):
    if len(arr1) != len(arr2): return False

    if eps is None:
        for i in range(len(arr1)):
            if arr1[i] != arr2[i]: return False
    else:
        for i in range(len(arr1)):
            if np.abs(arr1[i] - arr2[i]) > eps: return False

    return True

def getColorFromDict(dict, col, eps = 0.01):
    col = rgba(col)
    if col is None: return None
    
    for key in dict:
        col_value = rgba(key)
        if equal(col, col_value, eps): 
            return rgba(dict[key])
    
    return None

def CorrectSVG(svg_path):
    #tree = ET.parse(svg_path)

    #for elem in tree.findall(f'.//{xmlns}text'):
    #    elem.set('font-style', 'italic')

    #tree.write(svg_path, encoding = "UTF-8", xml_declaration = False)
    return

class GeoStyle:
    def __init__(self, style_json_file = None, px_size = [1920, 1080]):
        self.dot_size = 0.17   
        self.line_width = 6   
        self.ang_width = 0.75 * self.line_width
        self.strich_rshift = 0.14
        self.ang_rshift = 0.75 * self.strich_rshift
        self.label_r_offset = 0.45
        
        self.arrow_height = 0.35
        self.arrow_width = 0.32
        
        self.strich_len = 0.45
        self.strich_width = 6
        self.ang_rdefault = 0.8
        self.ang_right = 0.65
        
        self.font_size = 50
        
        self.background = WHITE
        self.strong = BLACK
        self.col_gray = '#eeeeee'

        self.col = '#6688c2'
        self.col_light = '#dee7f5'
        self.col_accent = '#d05456'
        self.col_accent_light = '#f6e0db'
        
        self.technic = {}
        self.ggb_export = {}

        if style_json_file is not None:
            style_json = json.loads(open(style_json_file, 'r').read())
            self.convert_from_json(style_json)            
        
        #параметры окна отображения 
        # размеры width и height в px
        # положение начала координат xZero и yZero
        # масштаб scale в px для 0.5 unit
        self.view = {}
        if px_size is not None:
            q = self.technic['scale_export'] if 'scale_export' in self.technic else 1
            self.view['width'] = float(px_size[0]) * q if not isnan(px_size[0]) else None
            self.view['height'] = float(px_size[1]) * q if not isnan(px_size[1]) else None

    def convert_from_json(self, style_map):
        style = style_map['style']
        
        self.dot_size = 0.02 * style['dot']['main']
        self.line_width = 2 * style['line']['main']
        self.ang_width = 2 * style['angle']['line']
        self.ang_rshift = 0.02 * style['angle']['r_shift']
        self.ang_rdefault = 0.02 * style['angle']['r_default']
        self.ang_right = 0.02 * style['angle']['r_right']
        self.strich_width = 2 * style['strich']['width']
        self.strich_len = 0.02 * style['strich']['len']
        self.strich_rshift = 0.02 * style['strich']['shift']
               
        self.arrow_height = 0.02 * style['arrow']['length']  
        self.arrow_width = 0.02 * style['arrow']['width']
        
        self.label_r_offset = 0.02 * self.label_r_offset
        
        self.background = '#ffffff'
        self.col = style['color']['main']
        self.col_light = style['color']['light']
        self.col_accent = style['color']['acc']
        self.col_accent_light = style['color']['acc_light']
        self.col_gray = '#eeeeee'
        
        self.font_size = style['font']['size'] * 50 / 25.9
        
        self.technic = style_map['technic']
        self.ggb_export = style_map['ggb_export']
        
        if 'colors' in self.ggb_export:
            for key in self.ggb_export['colors']:
                value = self.ggb_export['colors'][key]
                arr = value.split(' ')
                if arr[0] in style['color']:
                    self.ggb_export['colors'][key] = style['color'][arr[0]]
                    if len(arr) > 1: self.ggb_export['colors'][key] += ' ' + ' '.join(arr[1:])
        
        if 'line' in self.ggb_export: 
            for key in self.ggb_export['line']:
                value = str(self.ggb_export['line'][key])
                if value in style['line']:
                    self.ggb_export['line'][key] = style['line'][value]
       
        if 'dot' in self.ggb_export:
            for key in self.ggb_export['dot']:
                value = str(self.ggb_export['dot'][key])
                if value in style['dot']:
                    self.ggb_export['dot'][key] = style['dot'][value]

    def setViewByGeo(self, geoView):
        w0, h0 = self.view['width'], self.view['height']
        w, h = geoView['width'], geoView['height']
        if isnan(w0) & isnan(h0): 
            print("ERROR: width and heigth haven't been set")
            return
        elif isnan(w0):
            #print(w0, h0, w, h)
            w0 = float(h0) * w / h
            self.view['width'] = w0
        elif isnan(h0):
            #print(w0, h0, w, h)
            h0 = float(w0) * h / w
            self.view['height'] = h0
            
        q = min(w0/w, h0/h)
        
        self.view['scale'] = geoView['scale'] * q
        self.view['xZero'] = geoView['xZero'] * q + (w0 - q * w) / 2
        self.view['yZero'] = geoView['yZero'] * q + (h0 - q * h) / 2
        
        
def MakeGeoStyle(color = "blue", theme = "light", px_size = [1920, 1080]):
    style = GeoStyle(px_size = px_size)
    
    if theme == 'dark':
        style.background = BLACK
        style.strong = WHITE
        style.col_gray = '#282828'

        if color == 'white':
            style.col = '#ffffff'
            style.col_light = '#333333'
            style.col_accent = '#db4251'
            style.col_accent_light = '#68383f'
        elif color == 'purple':
            style.background = '#151324'
            style.col = '#9f9fdd'
            style.col_light = '#3c3766'
            style.col_accent = '#db4251'
            style.col_accent_light = '#542f36'
            style.col_gray = '#211f2f'

    else:
        style.background = WHITE
        style.strong = BLACK
        style.col_gray = '#eeeeee'

        if color == 'green':
            style.col = '#80be8c'
            style.col_light = '#e3efdb'
            style.col_accent = '#d05456'
            style.col_accent_light = '#f6e0db'
        elif color == 'orange':
            style.col = '#d97c2c'
            style.col_light = '#fae7ca'
            style.col_accent = '#72a6d9'
            style.col_accent_light = '#d8edfb'
        elif color == 'purple':
            style.col = '#8670ac'
            style.col_light = '#e8e3f0'
            style.col_accent = '#d05456'
            style.col_accent_light = '#f6e0db'
        else: #blue
            style.col = '#6688c2'
            style.col_light = '#dee7f5'
            style.col_accent = '#d05456'
            style.col_accent_light = '#f6e0db'
            
    return style

def updateMin(minX, x):
    if isnan(minX): return x
    if isnan(x): return minX
    return min(minX, x)
      
def updateMax(maxX, x):
    if isnan(maxX): return x
    if isnan(x): return maxX
    return max(maxX, x)

#--------------------------------------------------------------------------
import time

def reorder_objects_by_name(scene, name_order):
    ordered_objects = []
    other_objects = []
    
    for obj in scene.mobjects:
        if hasattr(obj, 'name') and obj.name in name_order:
            ordered_objects.append(obj)
        else:
            other_objects.append(obj)
    
    ordered_objects.sort(key=lambda x: name_order.index(x.name))
    scene.mobjects = ordered_objects + other_objects

# class GeoDynamic(ThreeDScene):
class GeoDynamic(MovingCameraScene):
    style_default = MakeGeoStyle(color = 'blue', theme = 'light')

    def __init__(self):
        super().__init__()
        self.geo = geo.Construction()
        self.style = GeoStyle()

        self._styles_back = {}
        self._gray_mobjects = {}

        self.cuts = 0

    def mobject(self, name): 
        for mobj in self.mobjects: 
            if mobj.name == name: return mobj
        return None
    
    def element(self, name):
        return self.geo.element(name)
    
    #----------------------------------
    
    def addOrdered(self, mobj):
        name_order = [elem.name for elem in self.geo.elements]
        if mobj.name not in name_order:
            self.add(mobj)
            return
        
        # Находим позицию для вставки
        # insert_index = len(self.mobjects)
        # current_index = name_order.index(obj.name)
        
        # for i, existing_obj in enumerate(self.mobjects):
        #     if not hasattr(existing_obj, 'name'): continue
        #     if existing_obj.name not in name_order: continue
            
        #     existing_index = name_order.index(existing_obj.name)
            
        #     if current_index < existing_index:
        #         insert_index = i
        #         break
        
        self.add(mobj)
        # self.mobjects.insert(insert_index, obj)
        # reorder_objects_by_name(self, name_order)
    
    def addGeoElement(self, elem):
        mobj = CreateMObject(elem, z_auto = True)
        if mobj is not None and elem.visible:
            self.add(mobj)

    def addAllGeometry(self, show = False):
        if not show:
            for el in self.geo.elements: el.visible = False
        element_types = [
            [geo.CircleSector, geo.Polygon],
            [geo.Angle],
            [geo.Circle, geo.Arc, geo.Segment, geo.Vector],
            [geo.Point]
        ]

        for el_types in element_types:
            for el in self.geo.elements: 
                if type(el.data) in el_types: self.addGeoElement(el) 
 
    def getAllGeometryBounds(self, scale = 1):
        bounds = [None,None,None,None]
        for elem in self.geo.elements: 
            if elem.visible:
                mobj = CreateMObject(elem, z_auto = True)
                if mobj is not None:
                    bounds[0] = updateMin(bounds[0], mobj.get_left()[0])
                    bounds[1] = updateMin(bounds[1], mobj.get_bottom()[1])
                    bounds[2] = updateMax(bounds[2], mobj.get_right()[0])
                    bounds[3] = updateMax(bounds[3], mobj.get_top()[1])
        
        for i in range(4): bounds[i] *= scale
                    
        return bounds

    #пауза для обрезки видео + отображение ярлыка слева
    def waitCut(self, msg = None, **kwargs):
        self.cuts += 1

        rect = Rectangle(color = RED, fill_opacity = 1, height = self.camera.frame_height, width = self.camera.frame_width/4).move_to(self.camera.frame_center).shift( (3/8) * self.camera.frame_width * LEFT)
        txt = Text(str(msg) if msg is not None else str(self.cuts)).set_color(BLACK).scale(3).move_to(rect)
        
        self.add(rect, txt)
        self.wait(**kwargs)

        self.remove(rect)
        self.remove(txt)
        
    #----------------------------------
    
    def updateAllGeometry(self):
        self.updateGeoElements()
    
    def updateGeoElements(self, updates = None):
        for elem in self.geo.elements:
            if updates: 
                if elem.name not in updates: continue

            mobj = self.mobject(elem.name)   
            mobj_new = CreateMObject(elem)
            
            # print(elem.name, type(elem.data), ", mobj:", hex(id(mobj)), ", mobj_new:", hex(id(mobj_new)))
            
            if mobj is None and mobj_new is None: continue
         
            needRemove = False if mobj is None     else (mobj_new is None) or (type(elem.data) == geo.Polygon) or (not elem.visible)
            needAdd = False    if mobj_new is None else (mobj is None)     or (type(elem.data) == geo.Polygon)
            
            # needRemove = False if mobj is None     else (mobj_new is None) or (not elem.visible)
            # needAdd = False    if mobj_new is None else (mobj is None)
            
            if needRemove: 
                mobj.set_opacity(0)
                # if type(elem.data) == geo.Polygon:
                #     mobj[0].set_fill(opacity=0)
                #     print('Polygon!!')
                # self.remove(mobj[0])
                # mobj.remove()
                self.remove(mobj)
            if needAdd:
                self.addOrdered(mobj_new)
            if not needRemove and not needAdd:
                # print("become:", mobj.name, ", type:", type(mobj).__name__)
                mobj.become(mobj_new)

    #----------------------------------
        
    def addVarTracker(self, name, value):
        new_tracker = ValueTracker(value)
        self.add(new_tracker)
        if not self.geo.var(name):
            self.geo.add(geo.Var(name, value))
        else:
            self.geo.var(name).data = value
        self.geo.rebuild(full = True)
        # self.updateGeoElements()
        return new_tracker
    
    def addUpdater(self, tracker, name):
        self.add_updater(lambda v, self = self: self.updateGeoVar(tracker, name))

    def loadGeometry(self, filepath, update = False, debug = False):
        short_parser.loadCode(self.geo, filepath, update = update, debug = debug)
        self.geo.rebuild(debug = debug)

    def loadGeoGebra(self, filepath, style_json_file = None, px_size = None, debug = False):
        self.geo = ggb_parser.load(filepath, debug = debug) 
        self.geo.rebuild(debug = debug, full = True)
        
        style = GeoStyle(style_json_file = style_json_file, px_size = px_size)
        
        if 'polygon_boundary_layer' in style.technic:
            if style.technic['polygon_boundary_layer'] == 'top':
                for comm in self.geo.commands:
                    if comm.name == 'Polygon':
                        for segm in comm.outputs[1:]:
                            self.geo.element(segm).style['z_index'] = 10
                            
        if 'colors' in style.ggb_export:
            ggb_colors = style.ggb_export['colors']
            for elem in self.geo.elements:
                col = getParamFromDict(elem.style, 'stroke', None)
                col_opacity = getParamFromDict(elem.style, 'stroke_opacity', None)
                col_new = getColorFromDict(ggb_colors, [col, col_opacity])
                if col_new is not None: 
                    elem.style['stroke'] = col_new
                    if len(col_new) > 3:
                        elem.style['stroke_opacity'] = col_new[3]
            
                col = getParamFromDict(elem.style, 'fill', None)
                col_opacity = getParamFromDict(elem.style, 'fill_opacity', None)
                col_new = getColorFromDict(ggb_colors, [col, col_opacity])
                if col_new is not None: 
                    elem.style['fill'] = col_new
                    if len(col_new) > 3:
                        elem.style['fill_opacity'] = col_new[3]
                        
        if 'line' in style.ggb_export:
            ggb_line = style.ggb_export['line']
            for elem in self.geo.elements:
                wid = getParamFromDict(elem.style, 'stroke_width', None)
                wid_new = getParamFromDict(ggb_line, str(wid), None)
                if wid_new is not None: 
                    elem.style['stroke_width'] = 2 * wid_new
        
        if 'crop_padding' in style.technic:
            bounds = self.getAllGeometryBounds(self.geo.style['view']['scale'])
            padding = style.technic['crop_padding']
            
            self.geo.style['view']['width'] = bounds[2] - bounds[0] + 2 * padding
            self.geo.style['view']['height'] = bounds[3] - bounds[1] + 2 * padding
            self.geo.style['view']['xZero'] = -bounds[0] + padding
            self.geo.style['view']['yZero'] = bounds[3] + padding
        
        if px_size is not None:
            style.setViewByGeo(self.geo.style['view'])
        else:
            style.view = self.geo.style['view']

        view = style.view
        scale = view['scale']
        scale_export = style.technic['scale_export'] if 'scale_export' in style.technic else 1
        q = 50 * scale_export / scale
        for key in ['dot_size', 'line_width', 'ang_width', 'ang_rdefault', 'ang_right', 'ang_rshift', 'strich_width', 'strich_rshift', 'strich_len', 'font_size', 'arrow_width', 'arrow_height']:
            setattr(style, key, getattr(style, key) * q)

        for elem in self.geo.elements:
            for key in ['stroke_width', 'label_r_offset']:
                val = getParamFromDict(elem.style, key, None)
                if val is not None: 
                    elem.style[key] = float(val) * q
            
        ratio = 1920/1080
        if view['width'] / view['height'] >= ratio:
            #! todo для 3d-сцены переделать
            self.camera.frame.set(width = view['width'] / scale)
            dx = self.camera.frame.width / 2 - view['xZero'] / scale
            dy = view['height'] / (2 * scale) - view['yZero'] / scale      
            self.camera.frame.shift(dx * RIGHT + dy * DOWN)
        else:
            #! todo для 3d-сцены переделать
            self.camera.frame.set(width = ratio * view['height'] / scale)
            dx = view['width'] / (2 * scale) - view['xZero'] / scale
            dy = self.camera.frame.height / 2 - view['yZero'] / scale      
            self.camera.frame.shift(dx * RIGHT + dy * DOWN)
    
        self.setStyle(style)
        self.addAllGeometry(show = True)

    def updateGeoVar(self, x, var_name):
        if self.geo.var(var_name).data != x.get_value():
            self.geo.update(var_name, float(x.get_value()))
            updates = self.geo.rebuild(full = True)
            self.updateGeoElements(updates)
        # else:
        #     print("updateGeoVar: NO CHANGES: x =", x.get_value())

    def setStyle(self, style):
        self.style = style
        GeoDynamic.style_default = style
        self.camera.background_color = GeoDynamic.style_default.background
        Text.set_default(color = self.style.strong)
        MathTex.set_default(color = self.style.strong)

    def Hide(self, names, **kwargs):
        plays = []

        for name in names:
            elem = self.element(name)
            if not elem: continue
            if not elem.visible: continue
            
            elem.visible = False
            
            mobj = self.mobject(name)
            self.remove(mobj)
            
            if mobj: plays.append(FadeOut(mobj))
        return plays

    def Update(self, names, **kwargs):
        plays = []

        for name in names:
            elem = self.element(name)
            if not elem: continue
            
            mobj = self.mobject(name)
            self.remove(mobj)
            
            if mobj: plays.append(FadeOut(mobj))

            mobj_new = CreateMObject(elem)
            if mobj_new: self.addOrdered(mobj_new)
            
            if mobj_new: plays.append(FadeIn(mobj_new))
            
        return plays

    def Show(self, names, mode = 'Fade', **kwargs):
        plays = []

        for name in names:
            elem = self.element(name)
            if not elem: continue
            if elem.visible: continue
            
            elem.visible = True

            mobj_new = CreateMObject(elem)
            if mobj_new: self.addOrdered(mobj_new)
            
            if mobj_new: 
                plays.append(Create(mobj_new, **kwargs) if mode == 'Create' else FadeIn(mobj_new, **kwargs))
            
        return plays

    def playHide(self, names, **kwargs):
        plays = self.Hide(names, **kwargs)
        if plays: self.play(*plays)
        
    def playUpdate(self, names, **kwargs):
        plays = self.Update(names, **kwargs)
        if plays: self.play(*plays)

    def playShow(self, names, mode = 'Fade', **kwargs):
        plays = self.Show(names, mode, **kwargs)
        if plays: self.play(*plays)

    def playGrayStyle(self, names, mode = 'Fade', **kwargs):
        self.play(*GrayStyleObjs(self, names, mode, **kwargs))

    def playBackStyle(self, names, mode = 'Fade', **kwargs):
        self.play(*BackStyleObjs(self, names, mode, **kwargs))

    #----------------------------------

    def exportSVG(self, filepath):
        if filepath is None:
            filepath = tempfile.mkstemp(suffix=".svg")
        filepath = os.path.abspath(filepath)
        
        with _get_cairo_context(filepath, self.style) as ctx:
            for mobj in extract_mobject_family_members(self.mobjects, True, True):
                if isinstance(mobj, ValueTracker): continue
                _create_svg_from_vmobject_internal(mobj, ctx, style = self.style)
    
    def addGrid(self, x_range=(-10, 10, 1), y_range=(-10, 10, 1)):
        grid = NumberPlane(
            x_range = x_range,
            y_range = y_range,
            x_length = x_range[1] - x_range[0],
            y_length = y_range[1] - y_range[0],
            background_line_style = {
                "stroke_color": BLACK,
                "stroke_width": self.style.ang_width,
                "stroke_opacity": 0.1
            },
            x_axis_config = {"stroke_opacity": 0},
            y_axis_config = {"stroke_opacity": 0}
        )

        self.add(grid.shift(-grid.get_origin()))

#--------------------------------------------------------------------------

def getParamFromDict(dict, key, paramDefault = None, check = True):
    if not check: return paramDefault
    if key not in dict: return paramDefault
    if dict[key] is None: 
        return paramDefault
    else: 
        return dict[key]

def hasParam(dict, key):
    if key not in dict: return False
    if not dict[key]: return False
    return True

def ShowObjs(scene, names, mode = None, **kwargs):
    plays = []
    for name in names:
        elem = scene.geo.element(name)
        if not elem: continue
        
        elem.visible = True
        mobj = scene.mobject(name)
        if mobj is None: continue

        op_s = getParamFromDict(elem.style, 'stroke_opacity', 1)
        op_f = getParamFromDict(elem.style, 'fill_opacity', 0 if (type(elem.data) != geo.Point) else 1)
        
        hasLabel = hasParam(elem.style, 'show_label')

        if type(elem.data) == geo.Segment:
            if hasLabel: 
                for m in mobj[:-1]:
                    m.set_stroke(opacity = op_s)
            else: mobj.set_stroke(opacity = op_s)

            plays.append(Create(mobj, **kwargs) if mode == 'Create' else FadeIn(mobj, **kwargs))

        elif type(elem.data) == geo.Angle:
            mobj[0].set_fill(opacity = op_f)

            if hasLabel:
                for m in mobj[1:-1]: 
                    m.set_fill(opacity = 0).set_stroke(opacity = op_s)
            else:
                for m in mobj[1:]: 
                    m.set_fill(opacity = 0).set_stroke(opacity = op_s)

            plays.append(FadeIn(mobj[0], **kwargs))
            plays.append(Create(mobj[1:], **kwargs) if mode == 'Create' else FadeIn(mobj[1:], **kwargs))

        else:
            if (type(elem.data) == geo.Polygon) | (type(elem.data) == geo.Circle) | (type(elem.data) == geo.Arc):
                mobj[0].set_stroke(opacity = 0).set_fill(opacity = op_f)  
                mobj[1].set_stroke(opacity = op_s).set_fill(opacity = 0)
            else:
                mobj[0].set_stroke(opacity = op_s).set_fill(opacity = op_f)  
        
            plays.append(Create(mobj, **kwargs) if mode == 'Create' else FadeIn(mobj, **kwargs))

    if len(plays) == 0:
        print('ShowObjs: NO OBJECTS found from ', names)

    return plays

def GrayStyleObjs(scene, names, **kwargs):
    plays = []
    for name in names:
        mobj = scene.mobject(name)
        if not mobj: continue
        elem = scene.geo.element(name)
        if not elem: continue

        scene._styles_back[name] = {}

        if getParamFromDict(elem.style, 'z_index'): 
            scene._styles_back[name]['z_index'] = elem.style['z_index']
            elem.style['z_index'] = 0

        if getParamFromDict(elem.style, 'stroke'): 
            scene._styles_back[name]['stroke'] = elem.style['stroke']
            elem.style['stroke'] = GeoDynamic.style_default.col_gray

        if getParamFromDict(elem.style, 'fill'):
            scene._styles_back[name]['fill'] = elem.style['fill']
            elem.style['fill'] = GeoDynamic.style_default.col_gray

        if getParamFromDict(elem.style, 'show_label'):
            scene._styles_back[name]['label_color'] = elem.style['label_color'] if ('label_color' in elem.style) else GeoDynamic.style_default.strong
            elem.style['label_color'] = GeoDynamic.style_default.col_gray

        if type(elem.data) == geo.Point:
            scene._styles_back[name]['fill_opacity'] = elem.style['fill_opacity'] if ('fill_opacity' in elem.style) else 1
            elem.style['fill_opacity'] = 0

        scene._gray_mobjects['_gray_' + name] = CreateMObject(elem, debug = True)
        #plays.append(mobj.animate.become(CreateMObject(elem)))
        plays.extend(HideObjs(scene, [name], **kwargs))
        plays.append(FadeIn(scene._gray_mobjects['_gray_' + name], **kwargs))

    return plays

def BackStyleObjs(scene, names, **kwargs):
    plays = []
    for name in names:
        mobj = scene.mobject(name)
        if not mobj: continue
        if name not in scene._styles_back: continue
        elem = scene.geo.element(name)
        style_back = scene._styles_back[name]
        if (not elem) or (not style_back): continue

        for key in style_back: elem.style[key] = style_back[key]

        #plays.append(mobj.animate.become(CreateMObject(elem)))
        plays.extend(ShowObjs(scene, [name], **kwargs))
        plays.append(FadeOut(scene._gray_mobjects['_gray_' + name], **kwargs))
        del scene._gray_mobjects['_gray_' + name]

    return plays

#--------------------------------------------------------------------------

def correctedLabel(label):
    texsymb = {
        '\\cdot': '·', '\\times':  '×', '\\neq': '≠', '\\approx': '≈', '\\sim': '~', '\\leqslant': '⩽', '\\geqslant': '⩾',
        '\\degree': '°', '\\Rightarrow': '⇒', '\\Leftarrow': '⇐', '\\rightarrow': '→', '\\to': '→', '\\gets': '←',
        '\\mathbf': '∠', '\\triangle': '△', '\\perp': '⊥', '\\parallel': '∥', '\\nparralel': '∦',
        '\\in': '∈', '\\notin': '∉', '\\cap': '∩', '\\cup': '∪', '\\subset': '⊂', '\\supset': '⊃', '\\subseteq': '⊆', '\\supseteq': '⊇', '\\forall': '∀', '\\exists': '∃',
        '\\Longleftrightarrow': '⟺', '\\Leftrightarrow': '⟺', '\\pm': '±', '\\varnothing': '∅', '\\infty': '∞',
        '\\mathrm A': 'Α', '\\alpha': 'α',
        '\\mathrm B': 'Β', '\\beta': 'β',
        '\\Gamma': 'Γ', '\\gamma': 'γ',
        '\\Delta': 'Δ', '\\delta': 'δ',
        '\\mathrm E': 'Ε', '\\varepsilon': 'ε',
        '\\mathrm Z': 'Ζ', '\\zeta': 'ζ',
        '\\mathrm H': 'Η', '\\eta': 'η',
        '\\Theta': 'Θ', '\\theta': 'ϑ', '\\vartheta': 'ϑ',
        '\\mathrm I': 'Ι', '\\iota': 'ι',
        '\\mathrm K': 'Κ', '\\kappa': 'κ',
        '\\Lambda': 'Λ', '\\lambda': 'λ',
        '\\mathrm M': 'Μ', '\\mu': 'μ',
        '\\mathrm N': 'Ν', '\\nu': 'ν',
        '\\Xi': 'Ξ', '\\xi': 'ξ',
        '\\mathrm O': 'Ο', '\\mathrm o': 'ο',
        '\\Pi': 'Π', '\\pi': 'π', '\\varpi': 'ϖ',
        '\\mathrm P': 'Ρ', '\\rho': 'ρ',
        '\\Sigma': 'Σ', '\\sigma': 'σ', '\\varsigma': 'ς',
        '\\mathrm T': 'Τ', '\\tau': 'τ',
        '\\Upsilon': 'Υ', '\\upsilon': 'υ',
        '\\Phi': 'Φ', '\\varphi': 'φ',
        '\\mathrm X': 'Χ', '\\chi': 'χ',
        '\\Psi': 'Ψ', '\\psi': 'ψ',
        '\\Omega': 'Ω', '\\omega': 'ω'
    }

    for tex in texsymb:
        label = re.sub(texsymb[tex], re.sub(r'\\', r'\\\\', tex), label)

    return label

def getAngRadius(ang: geo.Angle, style = None):
    if style is None: style = GeoDynamic.style_default
    r = style.ang_rdefault
    max_r = min(np.linalg.norm(ang.v1), np.linalg.norm(ang.v2))*0.65
    if ang.angle > 0.01:
        return min(max_r, r / ang.angle**0.25)
    else:
        return min(max_r, r / 0.01**0.25)
        
def getRightAngSize(ang: geo.Angle, style = None):
    if style is None: style = GeoDynamic.style_default
    r = style.ang_right
    max_r = min(np.linalg.norm(ang.v1), np.linalg.norm(ang.v2))*0.65
    return min(max_r, r)

class CustomArrowTip(ArrowTip, Polygon):
    def __init__(self, length = 0.35, **kwargs):
        w = kwargs['width'] * 0.5 if 'width' in kwargs else length * 0.45
        h = kwargs['height'] if 'height' in kwargs else length

        Polygon.__init__(self, [0, h, 0], [-w, 0, 0], [w, 0, 0])
        
        if 'fill' in kwargs:
            self.set_fill(color = kwargs['fill'], opacity = 1)
        if 'stroke' in kwargs:   
            self.set_stroke(color = kwargs['stroke'], opacity = 1)
        else:
            self.set_stroke(width = 0, opacity = 0)

def CreateMObject(elem, z_auto = False, style = None, debug = False):
    try:
        if not elem.visible: return None
        
        if style is None: style = GeoDynamic.style_default

        label_roff = getParamFromDict(elem.style, 'label_r_offset', style.label_r_offset)
        dash = getParamFromDict(elem.style, 'stroke_dash', None)
        cap = getParamFromDict(elem.style, 'stroke_cap', getParamFromDict(style.technic, 'line_caps', None))
        ra_joint = getParamFromDict(elem.style, 'right_angle_joint', getParamFromDict(style.technic, 'right_angle_joint', 'auto'))
        joint_map = {
            None: LineJointType.AUTO,
            "auto": LineJointType.AUTO,
            "bevel": LineJointType.BEVEL,
            "miter": LineJointType.MITER,
            "round": LineJointType.ROUND
        }
        cap_map = {
            None: CapStyleType.AUTO,
            "auto": CapStyleType.AUTO,
            "round": CapStyleType.ROUND,
            "butt": CapStyleType.BUTT,
            "square": CapStyleType.SQUARE
        }

        col_s = ManimColor(getParamFromDict(elem.style, 'stroke', style.strong))
        col_f = ManimColor(getParamFromDict(elem.style, 'fill', style.background if type(elem.data) != geo.Point else style.strong))
        op_s = getParamFromDict(elem.style, 'stroke_opacity', 1)
        op_f = getParamFromDict(elem.style, 'fill_opacity', 1)
        lw = getParamFromDict(elem.style, 'stroke_width', style.line_width) #, type(elem.data) == geo.Arc)
        col_label = ManimColor(getParamFromDict(elem.style, 'label_color', style.strong))
        font_size = getParamFromDict(elem.style, 'font_size', style.font_size)

        zz = getParamFromDict(elem.style, 'z_index')
        zz_fill = 0.01
        zz_stroke = 5
        zz_label = 50

        if (zz is None) and z_auto:
            if type(elem.data) == geo.Polygon: zz = 0.01
            elif type(elem.data) == geo.CircleSector: zz, zz_fill = 0.01, 0.001
            elif type(elem.data) == geo.Angle: zz = 3
            elif type(elem.data) == geo.Segment: zz = 5
            elif type(elem.data) == geo.Circle: zz = 5
            elif type(elem.data) == geo.Arc: zz = 5
            elif type(elem.data) == geo.Point: zz = 50

        if zz is None: zz = 0.01
        if zz == 0.01: zz_label = 0.1

        if type(elem.data) == geo.Polygon:
            pp = [[p[0], p[1], 0] for p in elem.data.points]
            poly_fill = Polygon(*pp, color = col_s, fill_color = col_f, fill_opacity = op_f, stroke_width = 0, stroke_opacity = 0).set_z_index(zz)
            poly_stroke = Polygon(*pp, joint_type = LineJointType.ROUND, color = col_s, fill_opacity = 0, stroke_width = lw, stroke_opacity = op_s).set_z_index(max(zz_stroke, zz + 0.1))
            
            return VGroup(poly_fill, poly_stroke, name = elem.name)
            
        if type(elem.data) == geo.Angle: 
            arr = []
            r = getAngRadius(elem.data, style) + elem.style['r_offset'] + (elem.style['lines'] - 1) * style.ang_rshift
            p = [elem.data.p[0], elem.data.p[1], 0]
            line1 = Line([p[0], p[1], 0], [p[0] + elem.data.v1[0], p[1] + elem.data.v1[1], 0])
            line2 = Line([p[0], p[1], 0], [p[0] + elem.data.v2[0], p[1] + elem.data.v2[1], 0])    

            right_mark = np.isclose(elem.data.angle, PI/2) if 'right_mark' not in elem.style else elem.style['right_mark']

            if right_mark:
                r = getRightAngSize(elem.data, style)
                n1 = elem.data.v1 * (r / np.linalg.norm(elem.data.v1))
                n2 = elem.data.v2 * (r / np.linalg.norm(elem.data.v2))
                p1 = [p[0] + n1[0], p[1] + n1[1], 0]
                p2 = [p1[0] + n2[0], p1[1] + n2[1], 0]
                p3 = [p[0] + n2[0], p[1] + n2[1], 0]
                arr.append(Polygon(p, p1, p2, p3, 
                                    color = col_f, stroke_width = 0, fill_opacity = op_f).set_z_index(zz))
                arr.append(VMobject(color = col_s, fill_opacity = 0, stroke_width = style.ang_width, stroke_opacity = op_s, joint_type = joint_map[ra_joint])
                           .set_points_as_corners([p1, p2, p3]).set_z_index(zz + 0.1))
            else:
                arr.append(AnnularSector(inner_radius = 0, outer_radius = r, angle = elem.data.angle, 
                                color = col_f, fill_opacity = op_f).set_z_index(zz)
                                .rotate(elem.data.start_angle, about_point=ORIGIN).shift ([p[0], p[1], 0]))
                for i in range(elem.style['lines']):
                    arr.append(Angle(line1, line2, radius = r - i * style.ang_rshift, other_angle = False, 
                                color = col_s, fill_opacity = 0, stroke_width = style.ang_width, stroke_opacity = op_s).set_z_index(zz + 0.1))

            if hasParam(elem.style, 'show_label'):
                #if hasParam(elem.style, 'label_r_offset'): r += elem.style['label_r_offset']
                r += label_roff
                label = elem.style['label'] if hasParam(elem.style, 'label') else '$' + elem.name + '$'
                tex = Tex(correctedLabel(label), color = col_label).set_z_index(zz_label).set(font_size = font_size)
                tex.move_to(Angle(line1, line2, radius = r).point_from_proportion(0.5))
                arr.append(tex)
                if hasParam(elem.style, 'offset'):
                    tex.shift([elem.style['offset'][0], elem.style['offset'][1], 0])

            return VGroup(*arr, name = elem.name)

        if type(elem.data) == geo.Segment:
            p1, p2 = elem.data.end_points
            m = (p1 + p2) / 2
            arr = []

            if dash: arr.append(DashedLine([p1[0], p1[1], 0], [p2[0], p2[1], 0], 
                            color = col_s, stroke_opacity = op_s, stroke_width = lw, cap_style = cap_map[cap], dash_length = 0.17, dashed_ratio = dash).set_z_index(zz))
            else: arr.append(Line([p1[0], p1[1], 0], [p2[0], p2[1], 0], 
                            color = col_s, stroke_opacity = op_s, stroke_width = lw, cap_style = cap_map[cap]).set_z_index(zz))

            if 'lines' in elem.style:
                num = elem.style['lines']
                dn = elem.data.n * style.strich_len / 2
                v = (p2 - p1) / np.linalg.norm(p2 - p1)
                
                if elem.style.get('lines_type') == 'wave':                    
                    s = style.strich_rshift * 1.7
                    l = style.strich_len * 0.8
                    radius = elem.style.get('lines_radius', s * 0.45)
                    
                    t = (l - 2 * radius) / (s - 2 * radius)
                    offset = t * s / 2
                    sign = 1
                                        
                    # Создаем точки для волнообразной линии
                    points = []
                    d = s * ((1 - num) * 0.5) + s/2 - l/(2*t)
                    points.append(list(m + v * d + elem.data.n * (l/2) * sign) + [0])
                    sign = -sign
                    for i in range(1, num, 1):
                        d = s * ((1 - num) * 0.5 + i)
                        points.append(list(m + v * d + elem.data.n * offset * sign) + [0])
                        sign = -sign
                    d = s * ((1 + num) * 0.5) - s/2 + l/(2*t)
                    points.append(list(m + v * d + elem.data.n * (l/2) * sign) + [0])

                    # Создаем волнообразную линию со скругленными углами
                    wave = round_corners_vmobject(
                        points, 
                        radius=radius,
                        components_per_rounded_corner=8,
                    ).set_stroke(color = col_s, width = style.strich_width, opacity = op_s).set_z_index(zz)
                    
                    arr.append(wave)
                else:
                    line = Line([m[0] + dn[0], m[1] + dn[1], 0], [m[0] - dn[0], m[1] - dn[1], 0],
                                color = col_s, stroke_width = style.strich_width, stroke_opacity = op_s).set_z_index(zz)

                    for i in range(num):
                        d = style.strich_rshift * ((1 - num) * 0.5 + i)
                        arr.append(line.copy().shift([v[0] * d, v[1] * d, 0]))       

            if hasParam(elem.style, 'show_label'):
                label = elem.style['label'] if hasParam(elem.style, 'label') else '$' + elem.name + '$'
                tex = Tex(correctedLabel(label), color = col_label).set_z_index(zz_label).set(font_size = font_size)
                tex.move_to([m[0], m[1], 0])
                arr.append(tex)
                if hasParam(elem.style, 'offset'):
                    tex.shift([elem.style['offset'][0], elem.style['offset'][1], 0])
            
            return VGroup(*arr, name = elem.name)
        
        if type(elem.data) == geo.Vector:
            p1, p2 = elem.data.end_points
            m = (p1 + p2) / 2
            arr = []
            
            if dash: arr.append(DashedLine([p1[0], p1[1], 0], [p2[0], p2[1], 0], 
                            color = col_s, stroke_opacity = op_s, stroke_width = lw, cap_style = cap_map[cap], dash_length = 0.17, dashed_ratio = dash).set_z_index(zz))
            else:
                arr.append(Arrow([p1[0], p1[1], 0], [p2[0], p2[1], 0], buff = 0, tip_shape = CustomArrowTip, tip_style = {'width': style.arrow_width, 'height': style.arrow_height, 'fill': col_s},
                            color = col_s, stroke_opacity = op_s, stroke_width = lw, cap_style = cap_map[cap]).set_z_index(zz))

            if 'lines' in elem.style:
                num = elem.style['lines']
                dn = elem.data.n * style.strich_len / 2
                v = (p2 - p1) / np.linalg.norm(p2 - p1)
                line = Line([m[0] + dn[0], m[1] + dn[1], 0], [m[0] - dn[0], m[1] - dn[1], 0],
                            color = col_s, stroke_width = style.strich_width, stroke_opacity = op_s).set_z_index(zz)

                for i in range(num):
                    d = style.strich_rshift * ((1 - num) * 0.5 + i)
                    arr.append(line.copy().shift([v[0] * d, v[1] * d, 0]))       

            if hasParam(elem.style, 'show_label'):
                label = elem.style['label'] if hasParam(elem.style, 'label') else '$' + elem.name + '$'
                tex = Tex(correctedLabel(label), color = col_label).set_z_index(zz_label).set(font_size = font_size)
                tex.move_to([m[0], m[1], 0])
                arr.append(tex)
                if hasParam(elem.style, 'offset'):
                    tex.shift([elem.style['offset'][0], elem.style['offset'][1], 0])
            
            return VGroup(*arr, name = elem.name)

        if type(elem.data) == geo.Circle: 
            circ_fill = Circle(name = elem.name, arc_center = [elem.data.c[0], elem.data.c[1], 0], radius = elem.data.r, 
                        fill_color = col_f, fill_opacity = op_f, stroke_opacity = 0, stroke_width = 0).set_z_index(zz_fill)
            circ_stroke = Circle(name = elem.name, arc_center = [elem.data.c[0], elem.data.c[1], 0], radius = elem.data.r, 
                        color = col_s, fill_opacity = 0, stroke_opacity = op_s, stroke_width = lw).set_z_index(zz)
            
            if dash:
                circ_stroke = DashedVMobject(
                    circ_stroke, num_dashes=int(2 * np.pi * elem.data.r / 0.17), dashed_ratio=dash
                )
            
            return VGroup(circ_fill, circ_stroke, name = elem.name)

        if type(elem.data) == geo.Arc:  
            c = [elem.data.c[0], elem.data.c[1], 0]
            a1, a2 = elem.data.angles 
            arr = [
                Arc(arc_center = c, radius = elem.data.r, start_angle = a1, angle = (a2 - a1) % (2*np.pi),
                        fill_color = col_f, fill_opacity = op_f, stroke_width = 0).set_z_index(zz_fill),
                Arc(arc_center = c, radius = elem.data.r, start_angle = a1, angle = (a2 - a1) % (2*np.pi),
                        color = col_s, fill_opacity = 0, stroke_opacity = op_s, stroke_width = lw, cap_style = cap_map[cap]).set_z_index(zz)
            ]
            if hasParam(elem.style, 'show_label'):
                label = elem.style['label'] if hasParam(elem.style, 'label') else '$' + elem.name + '$'
                tex = Tex(correctedLabel(label), color = col_label).set_z_index(zz_label).set(font_size = font_size)
                tex.move_to(Arc(arc_center = c, radius = elem.data.r + 0.7, start_angle = a1, angle = a2 - a1).point_from_proportion(0.5))
                arr.append(tex)
                if hasParam(elem.style, 'offset'):
                    tex.shift([elem.style['offset'][0], elem.style['offset'][1], 0])

            return VGroup(*arr, name = elem.name)
        
        if type(elem.data) == geo.CircleSector:  
            c = [elem.data.c[0], elem.data.c[1], 0]
            a1, a2 = elem.data.angles 
            angle_diff = a2 - a1

            sector_fill = Sector(arc_center=c, radius=elem.data.r, start_angle=a1, angle=angle_diff,
                fill_color=col_f, fill_opacity=op_f, stroke_width=0).set_z_index(zz_fill)

            sector_stroke = Arc(arc_center=c, radius=elem.data.r, start_angle=a1, angle=angle_diff,
                color=col_s, fill_opacity=0, stroke_opacity=op_s, stroke_width=lw, cap_style=cap_map[cap]).set_z_index(zz)
            
            arr = [sector_fill, sector_stroke]

            if hasParam(elem.style, 'show_label'):
                label = elem.style['label'] if hasParam(elem.style, 'label') else '$' + elem.name + '$'
                tex = Tex(correctedLabel(label), color=col_label).set_z_index(zz_label).set(font_size=font_size)
                # Размещаем метку в средней точке дуги
                mid_angle = a1 + angle_diff / 2
                label_pos = c + elem.data.r * 0.7 * np.array([np.cos(mid_angle), np.sin(mid_angle), 0])
                tex.move_to(label_pos)
                arr.append(tex)
                if hasParam(elem.style, 'offset'):
                    tex.shift([elem.style['offset'][0], elem.style['offset'][1], 0])

            return VGroup(*arr, name = elem.name)

        if type(elem.data) == geo.Point:
            radius = elem.style['size'] / 2 if hasParam(elem.style, 'size') else style.dot_size / 2
            arr = [Dot([elem.data.a[0], elem.data.a[1], 0], radius = radius,
                    color = col_f, fill_opacity = op_f).set_z_index(zz)]
            if getParamFromDict(style.technic, 'points_display', None) == 'only_labels':
                arr[0].set_fill(opacity = 0)
                arr[0].set_phantom(True)
                
            if hasParam(elem.style, 'show_label'):
                label = elem.style['label'] if hasParam(elem.style, 'label') else '$' + elem.name + '$'
                tex = Tex(correctedLabel(label), color = col_label).set_z_index(zz_label).move_to(arr[0]).set(font_size = font_size)
                arr.append(tex)
                if hasParam(elem.style, 'offset'):
                    tex.shift([elem.style['offset'][0], elem.style['offset'][1], 0])
                if getParamFromDict(style.technic, 'points_display', None) == 'only_points':
                    arr[1].set_fill(opacity = 0)
                    arr[1].set_phantom(True)

            return VGroup(*arr, name = elem.name)
        
    except Exception as e:
        print(f'MObject for element "{elem.name}" is NONE')
        print(f'EXCEPTION: {e}')
        return None
    
    return None

