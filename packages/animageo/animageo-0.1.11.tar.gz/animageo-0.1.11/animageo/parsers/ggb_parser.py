import os
import shutil
import re
import ast
from zipfile import ZipFile
from xml.etree import ElementTree
from xml.etree.ElementTree import Element as XElement

from ..geo.construction import Construction
from ..geo.lib_commands import Command
from ..geo.lib_vars import *
from ..geo.lib_elements import *
from .short_parser import putCode  # Импорт функции для выполнения кода

temp_path = os.path.join(os.getcwd(), "temp")

#--------------------------------------------------------------------------

from lark import Lark, Transformer, v_args
import xml.etree.ElementTree as ET

# Включаем преобразование аргументов в узлы дерева
@v_args(inline=True)
class GeoGebraTransformer(Transformer):
    def __init__(self):
        super().__init__()
    
    def number(self, token):
        return float(token)
    
    def variable(self, token):
        return str(token)
    
    def coordinates(self, x, y):
        return ("coordinates", x, y)
    
    def function_call(self, name, *args):
        # Фильтруем запятые и None
        args = [arg for arg in args if arg not in (',', None)]
        return ("function_call", str(name), args)
    
    def add(self, left, right):
        return ("bin_op", "+", left, right)
    
    def sub(self, left, right):
        return ("bin_op", "-", left, right)
    
    def mul(self, left, right):
        return ("bin_op", "*", left, right)
    
    def div(self, left, right):
        return ("bin_op", "/", left, right)
    
    def pow(self, left, right):
        return ("bin_op", "^", left, right)
    
    def neg(self, expr):
        return ("unary_op", "-", expr)
    
    def expression(self, expr):
        return expr
    
    def start(self, expr):
        return expr

# Грамматика с правильным приоритетом операций
grammar = """
    start: expression

    expression: sum

    sum: product
        | sum "+" product -> add
        | sum "-" product -> sub

    product: power
           | product "*" power -> mul
           | product "/" power -> div

    power: atom
         | power "^" atom -> pow

    atom: number
        | variable
        | coordinates
        | function_call
        | "-" atom -> neg
        | "(" expression ")"

    number: SIGNED_NUMBER
    variable: CNAME

    coordinates: "(" expression "," expression ")"

    function_call: CNAME "[" [args] "]"  -> function_call
                 | CNAME "(" [args] ")"  -> function_call

    args: expression ("," expression)*

    %import common.CNAME
    %import common.SIGNED_NUMBER
    %import common.WS
    %ignore WS
"""

# Создаем парсер
lark_parser = Lark(grammar, start="start", parser="lalr", transformer=GeoGebraTransformer())

# Функция для обработки специальных символов (например, градусов)
def preprocess_expression(expr):
    # Заменяем специальные символы
    expr = expr.replace("°", "")  # Удаляем символ градуса
    # Можно добавить другие замены по необходимости
    return expr

# Функция для парсинга XML GeoGebra
def parse_geogebra_xml(xml_content):
    root = ET.fromstring(xml_content)
    results = []
    
    # Парсим выражения из команд
    for cmd in root.findall(".//command"):
        for inp in cmd.findall("input"):
            for attr_name, expr in inp.items():
                if attr_name.startswith('a'):
                    try:
                        processed_expr = preprocess_expression(expr)
                        parsed = lark_parser.parse(processed_expr)
                        results.append(("command_input", cmd.get("name"), attr_name, expr, parsed))
                    except Exception as e:
                        results.append(("error", f"Ошибка разбора {expr}: {e}"))
    
    # Парсим выражения из элементов expression
    for expr_elem in root.findall(".//expression"):
        expr = expr_elem.get("exp")
        if expr:
            try:
                processed_expr = preprocess_expression(expr)
                parsed = lark_parser.parse(processed_expr)
                results.append(("expression", expr_elem.get("label"), expr, parsed))
            except Exception as e:
                results.append(("error", f"Ошибка разбора {expr}: {e}"))
    
    return results

#--------------------------------------------------------------------------

def rgb_to_hex(r, g, b):
    return '#{:02x}{:02x}{:02x}'.format(r, g, b)

def get_xelems(ggb_path: str):
    try:    
        os.mkdir(temp_path)
    except FileExistsError:
        pass
    shutil.copyfile(ggb_path, os.path.join(temp_path, "temp.ggb"))
    
    ggb = ZipFile(os.path.join(temp_path, "temp.ggb"))
    ggb.extractall(temp_path)
    ggb.close()
    os.remove(os.path.join(temp_path, "temp.ggb"))
    
    tree = ElementTree.parse(os.path.join(temp_path, "geogebra.xml"))
    root = tree.getroot()
    
    shutil.rmtree(temp_path)
    
    return root.find("construction"), root.find("euclidianView")

def replace_with_point(expr_str):
    # Регулярное выражение для поиска нужных скобок
    pattern = r'''
        (?<!\w)           # Отрицательный просмотр назад: перед скобкой не должно быть символа слова
        \(                # Открывающая круглая скобка
        \s*               # Возможные пробелы после открывающей скобки
        [^(),]+           # Первый элемент (не содержит скобок или запятых)
        \s*               # Возможные пробелы
        ,                 # Запятая, разделяющая элементы
        \s*               # Возможные пробелы
        [^(),]+           # Второй элемент (не содержит скобок или запятых)
        \s*               # Возможные пробелы перед закрывающей скобкой
        \)                # Закрывающая круглая скобка
    '''
    
    # Замена: вставляем 'Point' перед найденными скобками
    return re.sub(pattern, r'Point\g<0>', expr_str, flags=re.VERBOSE)

 # Функция для извлечения идентификаторов из выражения
def extract_identifiers(expression):
    # Ищем идентификаторы, которые могут содержать фигурные скобки как часть имени
    # Это включает имена типа "M_{1}", "u_{1}" и т.д.
    identifier_pattern = r'[a-zA-Z_][a-zA-Z0-9_]*\{[^}]*\}|[a-zA-Z_][a-zA-Z0-9_]*'
    
    # Находим все совпадения
    identifiers = set()
    for match in re.finditer(identifier_pattern, expression):
        ident = match.group(0)
        # Проверяем, что это не часть числа и не оператор
        if not re.match(r'^\d', ident) and ident not in ['and', 'or', 'not']:
            identifiers.add(ident)
    
    # Также ищем идентификаторы с специальными символами, которые могут быть пропущены
    special_pattern = r'[a-zA-Z_][a-zA-Z0-9_{}\'&°]*'
    for match in re.finditer(special_pattern, expression):
        ident = match.group(0)
        # Исключаем чисто числовые значения и операторы
        if not re.match(r'^\d', ident) and ident not in ['and', 'or', 'not']:
            identifiers.add(ident)
    
    # Исключаем ключевые слова Python и стандартные функции
    python_keywords = {'and', 'as', 'assert', 'break', 'class', 'continue', 
                      'def', 'del', 'elif', 'else', 'except', 'False', 'finally', 
                      'for', 'from', 'global', 'if', 'import', 'in', 'is', 
                      'lambda', 'None', 'nonlocal', 'not', 'or', 'pass', 'raise', 
                      'return', 'True', 'try', 'while', 'with', 'yield'}
    
    math_functions = {'sin', 'cos', 'tan', 'sqrt', 'log', 'ln', 'exp', 'abs', 
                     'round', 'floor', 'ceil', 'min', 'max', 'sum'}
    
    excluded = python_keywords.union(math_functions)
    return identifiers - excluded

def convert_ggb_expr_to_python(constr, expr_str, expr_type=None):    
    # Извлекаем все идентификаторы из выражения
    identifiers = extract_identifiers(expr_str)
    # print("identifiers:", identifiers)
    
    # Добавляем новые идентификаторы в name_mapping, если они еще не там
    for identifier in identifiers:
        if identifier not in constr.name_mapping:
            constr.get_normalized_name(identifier)
    
    # Заменяем все имена согласно name_mapping
    for original, normalized in constr.name_mapping.items():
        expr_str = re.sub(r'\b' + re.escape(original), normalized, expr_str)
        
    # Проверяем, является ли выражение простым вектором в формате (x, y)
    vector_match = re.match(r'^\s*\(\s*([-\d.]+)\s*,\s*([-\d.]+)\s*\)\s*$', expr_str)
    if vector_match and expr_type == "vector":
        x, y = vector_match.groups()
        return f"Vector(Point({x}, {y}))"
    
    expr_str = replace_with_point(expr_str)
    
    # Заменяем квадратные скобки на круглые
    expr_str = expr_str.replace('[', '(').replace(']', ')')
    
    # Заменяем функции CamelCase на snake_case
    pattern = r'\b([A-Za-z_][A-Za-z0-9_]*)\('
    def camel_to_snake(match):
        name = match.group(1)
        s = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', name)
        return s + '('
    
    expr_str = re.sub(pattern, camel_to_snake, expr_str)
    
    # Заменяем градусы
    pattern_deg = r'(\d+)°'
    expr_str = re.sub(pattern_deg, r'AngleSize("\1°")', expr_str)
    
    return expr_str

def is_number(s):
    try:
        float(s)
        return True
    except ValueError:
        return False

def is_angle_degrees(s):
    try:
        assert(s[-1] == '°')
        float(s[:-1])
        return True
    except:
        return False

def is_simple_value(s):
    if s is None:
        return True
    if is_number(s):
        return True
    if is_angle_degrees(s):
        return True
    if re.match(r'^[a-zA-Z_][a-zA-Z0-9_]*$', s):
        return True
    return False

def get_alpha_from_point_and_circle(point, circle):
    """Вычисляет alpha для точки на окружности"""
    vector = point.a - circle.c
    theta = np.arctan2(vector[1], vector[0])
    return theta % (2*np.pi)

def get_alpha_from_point_and_line(point, line):
    """Вычисляет alpha для точки на прямой"""
    base_point = line.c * line.n
    t = np.dot(point.a - base_point, line.v)
    return t

def get_alpha_from_point_and_segment(point, segment):
    """Вычисляет alpha для точки на отрезке"""
    A = segment.end_points[0]
    B = segment.end_points[1]
    AB = B - A
    AP = point.a - A
    alpha = np.dot(AP, AB) / np.dot(AB, AB)
    return alpha

def parse_constr(constr: Construction, constr_xelem: XElement, debug = False):
    xelems_left_to_pass = 0
    fixed_element = False
    alpha_input = None
    name_mapping = {}
    style = {}

    for xelem in constr_xelem:                    
        if xelem.tag == "element":                    
            name = xelem.attrib['label']
            type = xelem.attrib['type']

            name_mapping[name] = constr.get_normalized_name(name)
            name = name_mapping[name]
            
            style[name] = {}

            elem = xelem.find("decoration")
            if elem is not None: 
                style[name]['lines'] = int(elem.attrib['type'])
                if type == 'angle':
                    style[name]['lines'] += 1
                
            elem = xelem.find("show")
            if elem is not None: 
                style[name]['show_element'] = (elem.attrib['object'] == 'true')
                style[name]['show_label'] = (elem.attrib['label'] == 'true')
            
            elem = xelem.find("labelMode")
            if elem is not None:
                caption = xelem.find("caption")
                if (elem.attrib['val'] == '3') & (caption is not None):
                    style[name]['label'] = '$' + caption.attrib['val'] + '$'
            
            elem = xelem.find("angleStyle")
            if elem is not None:
                if type == 'angle':
                    style[name]['range_type'] = int(elem.attrib['val'])
                    
            elem = xelem.find("pointStyle")
            if elem is not None:
                if type == 'point':
                    style[name]['point_type'] = int(elem.attrib['val'])
                    
            # elem = xelem.find("pointSize")
            # if elem is not None:
            #     if type == 'point':
            #         style[name]['size'] = float(elem.attrib['val']) * 0.01 * 2.8346456692916

            elem = xelem.find("labelOffset")
            if elem is not None: 
                x, y = float(elem.attrib['x']), float(elem.attrib['y'])
                if type == "angle":
                    style[name]['offset'] = [x/100, -y/100]
                else:
                    style[name]['offset'] = [0.1 + x/100, 0.11 - y/100]
            else:
                if type == "angle":
                    style[name]['offset'] = [0, 0]
                else:
                    style[name]['offset'] = [0.1, 0.11]

            elem = xelem.find("arcSize")
            if elem is not None: 
                if xelem.attrib['type'] == 'angle':
                    style[name]['r_offset'] = (float(elem.attrib['val']) - 30) / 150
                
            elem = xelem.find("objColor")
            if elem is not None:
                r, g, b, a = int(elem.attrib['r']), int(elem.attrib['g']), int(elem.attrib['b']), float(elem.attrib['alpha'])
                if xelem.attrib['type'] in ['angle', 'polygon', 'arc', 'conic']: #, 'point']:
                    style[name]['fill'] = rgb_to_hex(r, g, b)
                    style[name]['fill_opacity'] = a
                lineStyle = xelem.find("lineStyle")
                if lineStyle is not None:
                    thick, tt = lineStyle.attrib['thickness'], lineStyle.attrib['type']
                    op = float(lineStyle.attrib['opacity']) if 'opacity' in lineStyle.attrib else 255
                    if xelem.attrib['type'] in ['angle', 'segment', 'arc', 'conic', 'vector']:
                        style[name]['stroke'] = rgb_to_hex(r, g, b)
                        #style[name]['stroke_opacity'] = op / 255
                        style[name]['stroke_width'] = thick
                        if int(tt) > 0: style[name]['stroke_dash'] = 0.65
                        
        if xelems_left_to_pass:
            xelems_left_to_pass -= 1
            continue

        if xelem.tag == "expression":
            name = xelem.attrib['label']
            expr = xelem.attrib['exp']
            expr_type = xelem.attrib.get('type', None)
            name_mapping[name] = constr.get_normalized_name(name)
            converted_expr = convert_ggb_expr_to_python(constr, expr, expr_type)

            if debug:
                print(f"Expression found: {name} = {converted_expr}")
                
            if expr.find('=') < 0:
                putCode(constr, f"{name_mapping[name]} = {converted_expr}", debug=debug)
            else:
                print(f"{expr_type}: {expr} >> {name}")
                print(f"WARNING: parser has no implementation for expression '{expr}'\n")
            
            xelems_left_to_pass = 1
            continue
        
        if xelem.tag == "command":            
            comm_name = xelem.attrib["name"]                        
            input_xelem, output_xelem = xelem.find("input"), xelem.find("output")
            inputs, outputs = list(input_xelem.attrib.values()), list(output_xelem.attrib.values())
            outputs = [constr.get_normalized_name(output) for output in outputs]
            for i, inp in enumerate(inputs):
                if is_number(inp) or is_angle_degrees(inp):
                    inputs[i] = inp 
                else:
                    inputs[i] = constr.get_normalized_name(inp)
            
            # Обработка выражений во входных параметрах
            new_inputs = []
            for inp in inputs:
                if is_simple_value(inp):
                    new_inputs.append(inp)
                else:
                    # Создаем временную переменную для выражения
                    temp_name = constr.add_new_phantom()
                    converted_expr = convert_ggb_expr_to_python(constr, inp)
                    putCode(constr, f"{temp_name} = {converted_expr}", debug=debug)
                    new_inputs.append(temp_name)
            
            command = Command(comm_name, new_inputs, outputs)
            constr.add(command)
            constr.apply(command, debug = debug)
            
            if comm_name == "Point":
                if len(inputs) == 1:
                    if debug: print(f'Point FIXED by {inputs[0]}')
                    fixed_element = True
            
                    input0 = constr.element(inputs[0]).data if constr.element(inputs[0]) else None
                    if isinstance(input0, (Circle, Line, Segment)):
                        alpha_input = input0
            
            xelems_left_to_pass = len(output_xelem.attrib) if not alpha_input else 0
                        
            continue
        
        # Here xelem has to be a commandless point or numeric (Var)
        
        if xelem.tag == "element":
            name = name_mapping[xelem.attrib["label"]]
            if xelem.attrib["type"] == "point":
                coords = list(xelem.find("coords").attrib.values())
                coords.pop(-1) #  removing z coordinate
                alpha = None
                if alpha_input:
                    if isinstance(alpha_input, Circle):
                        alpha = get_alpha_from_point_and_circle(Point(coords), alpha_input)
                    elif isinstance(alpha_input, Segment):
                        alpha = get_alpha_from_point_and_segment(Point(coords), alpha_input)
                    elif isinstance(alpha_input, Line):
                        alpha = get_alpha_from_point_and_line(Point(coords), alpha_input)
                
                if alpha is not None: 
                    fixed_element = False
                    constr.element(name).data = Point([float(x) for x in coords])
                    constr.element(name).alpha = alpha
                else:
                    constr.add(Element(name, Point([float(x) for x in coords]), fixed = fixed_element))
                    
                fixed_element = False
                alpha_input = None
                continue
            if xelem.attrib["type"] == "numeric":
                value_xelem = xelem.find("value")
                constr.add(Var(name, float(value_xelem.attrib["val"])))
                continue
            if xelem.attrib["type"] == "angle":
                value_xelem = xelem.find("value")
                constr.add(Var(name, AngleSize(float(value_xelem.attrib["val"]))))
                continue
        
        #raise ElementTree.ParseError(f"Unexpected XElement met:\n\t<{xelem.tag}>, {xelem.attrib}")
        print(f"Unexpected XElement met:\n\t<{xelem.tag}>, {xelem.attrib}")

    constr.rebuild(debug = debug)

    #styling elements
    for name in style:
        if constr.element(name) is None: continue 
        if isinstance(constr.element(name), Var): continue 
        for key in style[name]:
            if debug: print(f'STYLE >> {name} >> {key} = {style[name][key]}')
            if key == 'show_element':
                if not constr.element(name):
                    print(f"element {name} is None")
                constr.element(name).visible = style[name][key]
                continue
            constr.element(name).style[key] = style[name][key]

def FloatOrNone(txt):
    return float(txt) if txt is not None else None

def parse_view(constr: Construction, view_xelem: XElement, debug = False):
    constr.style['view'] = {}
    
    for xelem in view_xelem:            
        if xelem.tag == "size":
            constr.style['view']['width'], constr.style['view']['height'] = FloatOrNone(xelem.attrib['width']), FloatOrNone(xelem.attrib['height'])

        if xelem.tag == "coordSystem":
            constr.style['view']['xZero'], constr.style['view']['yZero'] = FloatOrNone(xelem.attrib['xZero']), FloatOrNone(xelem.attrib['yZero'])
            constr.style['view']['scale'] = FloatOrNone(xelem.attrib['scale'])       

def load(constr: Construction, ggb_path: str, debug = False): # -> Construction:
    if debug: print("--------------------------------\n[[loading from ggb]]:\n")
    constr_xelem, view_xelem = get_xelems(ggb_path)
    # if debug: print(constr_xelem, view_xelem)
    parse_constr(constr, constr_xelem, debug = debug)
    parse_view(constr, view_xelem, debug = debug)
