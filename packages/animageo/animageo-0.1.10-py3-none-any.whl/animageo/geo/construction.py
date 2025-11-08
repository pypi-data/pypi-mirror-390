from .lib_vars import *
from .lib_elements import *
from .lib_commands import *
import itertools
from collections import deque

#--------------------------------------------------------------------------

def appendIfNew(elem, elemArray):
    for el in elemArray:
        if elem == el: return
    
    elemArray.append(elem)
    
def normalize_name(name):
    # Заменяем HTML-сущности
    name = name.replace("&apos;", "_prime")
    # Заменяем нижние индексы в фигурных скобках
    name = re.sub(r'{(\w+)}', r'\1', name)
    # Заменяем любые другие недопустимые символы на подчеркивание
    name = re.sub(r'[\']', "_Prime", name)
    # Убедимся, что имя не начинается с цифры
    if name[0].isdigit():
        name = 'var_' + name
    return name

class Construction:
    def __init__(self):
        self.phantoms = {}   #example: {'_1': Var, '_2': Point, '_3': [Point, float, '_2']}
        self.vars = []
        self.elements = [
            Element("xAxis", Line((0, 1), 0), visible=False),
            Element("yAxis", Line((1, 0), 0), visible=False)
        ]
        self.commands = []
        self.state = {} #статус элементов и связи (state[elem_name] = {level, inputs, outputs, input_commands, built})
        self.name_mapping = {} #перевод сложных имен в нормализованные: t_{1} -> t_1
        
        self.style = {}

    def __repr__(self):
        str_out = "-------------------\n[[construction]]:\n"

        str_out += "\n[{} phantoms]:".format(len(self.phantoms)) + '\n'
        for key in self.phantoms: str_out += str(key) + ': ' + str(self.phantoms[key]) + '\n'

        str_out += "\n[{} vars]:".format(len(self.vars)) + '\n'
        for var in self.vars: str_out += str(var) + '\n'
       
        str_out += "\n[{} elements]:".format(len(self.elements)) + '\n'
        for element in self.elements: str_out += str(element) + '\n'
        
        str_out += "\n[{} commands]:".format(len(self.commands)) + '\n'
        for command in self.commands: str_out += str(command) + '\n'

        str_out += "\n.....................\n"
        str_out += "[[state]]:\n"

        state = []
        for name in self.state:
            level = self.state[name]['level']
            while level >= len(state): state.append([])
            state[level].append(name)

        for level in range(len(state)):
            str_out += f"\n[level {level}]:\n"
            for name in state[level]:
                str_out += name + ('' if self.state[name]['built'] else '*') + "\t"

        str_out += "\n-------------------\n"
        return str_out

    def new_repr(self):
        return "-------------------\n[[construction]]:\n" + \
            f"\n[{len(self.vars)} vars]:\n" + '\n'.join(map(str, self.vars)) + "\n" + \
                f"\n[{len(self.elements)} elements]:\n" + '\n'.join(map(str, self.elements)) + "\n" + \
                    f"\n[{len(self.commands)} commands]:\n" + '\n'.join(map(str, self.commands)) + "\n" + \
                        "-------------------\n"

    def add_new_phantom(self):
        num = 1
        while ('_' + str(num)) in self.phantoms: num += 1
        key = '_' + str(num)
        self.phantoms[key] = None
        return key
    
    def get_normalized_name(self, name):
        normalized_name = normalize_name(name)
        self.name_mapping[name] = normalized_name
        return normalized_name

    def add(self, obj):
        if isinstance(obj, Var): 
            self.vars.append(obj)
            if obj.name not in self.state:
                self.state[obj.name] = { 'level': 0, 'inputs': [], 'outputs': [], 'input_commands': [], 'built': True }
        elif isinstance(obj, Element): 
            self.elements.append(obj)
            if obj.name not in self.state:
                self.state[obj.name] = { 'level': 0, 'inputs': [], 'outputs': [], 'input_commands': [], 'built': True }
        elif isinstance(obj, Command): 
            self.commands.append(obj)                    
            self.updateStateLevels(obj)

    def update(self, name, data, log = None):
        if isinstance(data, str):
            data_prepared = self.dataByStr(data)
            if data_prepared: data = data_prepared
        
        obj = self.objectByName(name)
        if obj is None:
            if name not in self.state:
                self.state[name] = { 'level': 0, 'inputs': [], 'outputs': [], 'input_commands': [], 'built': False }
            if isinstance(data, (Point, Line, Angle, Polygon, Circle, Vector)):
                self.add(Element(name, data, visible = (name[0] != '_')))
                self.state[name]['built'] = True
                if log is not None: log[name] = True
            elif isinstance(data, (int, float, bool, Measure, AngleSize)):
                self.add(Var(name, data))
                self.state[name]['built'] = True
                if log is not None: log[name] = True
            else:
                print(f"Construction.update({name}) ERROR: element data type {type(data)} update has no realization")
        else:
            if isinstance(obj, Var) or isinstance(obj, Element):
                for output in self.state[name]['outputs']:
                    self.state[output]['built'] = False
                # ?здесь нужно ли проверить, что объект не имеет предшедствующих зависимостей
                if not isinstance(obj.data, type(data)):
                    if isinstance(obj, Var):
                        if isinstance(obj.data, AngleSize) and isinstance(data, (int, float)):
                            data = AngleSize(data)
                        elif isinstance(obj.data, (int, float)) and isinstance(data, AngleSize):
                            data = data.value
                    else:
                        print(f"Construction.update({name}) ERROR: update data type is uncompatible: {obj.data} != {data}")
                obj.data = data
                self.state[name]['built'] = True
                if log is not None: log[name] = True
            elif isinstance(obj, Command):
                print(f"Construction.update({name}) ERROR: command update has no realization")

    # def _updateStateLevel(self, name, level):
    #     if self.state[name]['level'] < level:
    #         self.state[name]['level'] = level
    #         for output in self.state[name]['outputs']:
    #             self._updateStateLevel(output, max(self.state[output]['level'], level + 1))

    def _updateStateLevel(self, name, level):
        queue = deque()
        queue.append((name, level))
        
        while queue:
            current_name, current_level = queue.popleft()
            
            if self.state[current_name]['level'] < current_level:
                self.state[current_name]['level'] = current_level
                
                for output in self.state[current_name]['outputs']:
                    next_level = current_level + 1
                    if next_level > self.state[output]['level']:
                        queue.append((output, next_level))

    def sortCommands(self):
        #! todo поправить state (расположение элементов по уровням!) после сортировки
        
        i_first = -1
        i_last = len(self.commands) - 1
        for _ in range(len(self.commands)):
            cmd_last = self.commands[i_last]
            i = 0
            while (i < i_last) and (i_first < 0):
                cmd_first = self.commands[i]
                for input, output in itertools.product(cmd_first.inputs, cmd_last.outputs):
                    if input == output:
                        i_first = i
                        break
                i += 1
                    
            if i_first >= 0:
                self.commands.pop(i_last)
                self.commands.insert(i_first, cmd_last)
            else:
                i_last -= 1
            i_first = -1
        
        #! todo нужно в конце еще один раз проверить, если снова есть нарушенный порядок, значит, это неизбежно и есть циклы зависимостей между командами

    def updateStateLevels(self, command):
        for output in command.outputs:
            if is_number(output): raise Exception(f'output could not be a number: {output}')
            if is_angle_degrees(output): raise Exception(f'output could not be an angle_size: {output}')    
            if output not in self.state:
                self.state[output] = { 'level': 0, 'inputs': [], 'outputs': [], 'input_commands': [], 'built': False }
            
            self.state[output]['built'] = False
            appendIfNew(command, self.state[output]['input_commands'])
            
            for input in command.inputs:
                if is_number(input): continue
                if is_angle_degrees(input): continue
                if input not in self.state:
                    self.state[input] = { 'level': 0, 'inputs': [], 'outputs': [], 'input_commands': [], 'built': False }

                appendIfNew(output, self.state[input]['outputs'])
                appendIfNew(input, self.state[output]['inputs'])
                
                self._updateStateLevel(output, max(self.state[output]['level'], self.state[input]['level'] + 1))


    def updateCommand(self, nameCommand, inputs, outputs = None):
        command = None if outputs is None else self.commandByElementName(outputs[0])
        if command is not None:
            command.name = nameCommand
            command.inputs = inputs
            command.outputs = outputs
            self.updateStateLevels(command)
        else:
            self.add(Command(nameCommand, inputs, outputs))

    def element(self, name: str): #) -> Element | None:
        result = list(filter(lambda elem: elem.name == name, self.elements))
        return result[0] if result else None

    def var(self, name: str): #) -> Var | None:
        result = list(filter(lambda var: var.name == name, self.vars))
        return result[0] if result else None

    def objectByName(self, name: str): #) -> Element | Var | None:
        for elem in self.elements:
            if elem.name == name: return elem
        for var in self.vars:
            if var.name == name: return var
        for key in self.phantoms:
            if key == name: return self.phantoms[key]   
        return None

    def commandByElementName(self, name: str): #) -> Command | None:
        result = list(filter(lambda comm: name in comm.outputs, self.commands))
        return result[0] if result else None

    def dataByStr(self, text):
        obj = self.objectByName(text)
        if obj is not None: return obj.data

        if is_number(text): return float(text)
        if is_angle_degrees(text): return AngleSizeFromStr(text)
        if is_boolean(text): return boolean(text)

        #raise Exception("Not found object(s) '{}' or not processing".format(text))
        return None

    def prepareInputs(self, command):
        for i in range(len(command.inputs)):
            if isinstance(command.inputs[i], str):
                command.inputs[i] = self.dataByStr(command.inputs[i])

    def rebuild(self, debug = False, full = False):
        log = {}
        if full:
            for command in self.commands: self.apply(command, debug, log = log)
        else:
            state = []
            for name in self.state:
                level = self.state[name]['level']
                while level >= len(state): state.append([])
                state[level].append(name)

            for level in range(len(state)):
                for name in state[level]:
                    if not self.state[name]['built']:
                        for command in self.state[name]['input_commands']:
                            self.apply(command, debug = debug, log = log)
        
        return log

    def copy(self, command):
        assert(isinstance(command, Command))
        command_copy = Command(command.name, list(command.inputs).copy(), list(command.outputs).copy())
        return command_copy

    def apply(self, command_original, debug = False, log = None):
        command = self.copy(command_original)            
        self.prepareInputs(command)
        input_data = [obj.data if hasattr(obj,"data") else obj for obj in command.inputs]
        
        # специальный случай для Point: если у Point определено положение с помощью коэфф alpha, то он передается в команду как дополнительный параметр
        if len(command.outputs) == 1 and self.element(command.outputs[0]):
            if isinstance(self.element(command.outputs[0]).data, Point):
                if self.element(command.outputs[0]).alpha is not None:
                    input_data.append(self.element(command.outputs[0]).alpha)
        
        # специальный случай для Intersect(Circle, ...): если уже были точки до этого, то используется порядок точек
        points_order = None
        if command.name == 'Intersect':
            circ, circ_name = None, None
            for i, inp in enumerate(command_original.inputs):
                if isinstance(input_data[i], Circle):
                    circ, circ_name = input_data[i], inp.name if hasattr(inp,"name") else inp
                    break
            
            if circ:
                points_order = []
                for circ_input in self.state[circ_name]['inputs']:
                    elem = self.element(circ_input)
                    if elem is not None:
                        if isinstance(elem.data, Point): points_order.append(elem.data)
                # for circ_output in self.state[circ_name]['outputs']:
                #     if self.element(circ_output):
                #         p = self.element(circ_output).data
                #         if isinstance(p, Point): points_order.append(p)

                if (len(points_order) > 0) and is_number(input_data[-1]):
                    input_data.append(points_order)
                    # print(f"INTERSECT input_data: {input_data}")
                    
                # print(f"circ {circ_name}: {circ}, points_order: {points_order}")
        
        f = command.func()

        if f is not None:
            # основной вызов расчетной команды
            output_data = f(*input_data)
            if not isinstance(output_data, list): output_data = [output_data]
            if debug:
                str_inputs = [obj.name if hasattr(obj,"name") else obj for obj in command_original.inputs]
                print(f"{f.__name__}: {str_inputs} >> {command_original.outputs}")
                print(f"    {input_data}")
                print(f"    {output_data}")

            # здесь идет проверка выходных данных output_data и запись соответствующих данных в command.outputs
            for i in range(len(output_data)):
                if (i < len(command.outputs)) and (output_data[i] is not None):
                    if self.element(command.outputs[i]) is not None:
                        if not self.element(command.outputs[i]).fixed:
                            self.update(command.outputs[i], output_data[i], log = log)
                    else:
                        self.update(command.outputs[i], output_data[i], log = log)
        else:
            str_inputs = [obj.name if hasattr(obj,"name") else obj for obj in command_original.inputs]
                    
            has_none_attr = False
            for inp in input_data: 
                if inp is None: 
                    has_none_attr = True
                    break
            
            if has_none_attr:
                if debug:
                    print(f"{strFullCommand(command.name, command.inputs)}: {str_inputs} >> {command_original.outputs}")
                    print(f"    {input_data}")
                    print(f"WARNING: undefined arguments in '{command.name}'\n")
            else:
                str_types = [type(x).__name__ for x in input_data]
                print(f"{strFullCommand(command.name, command.inputs)}: {str_inputs} >> {command_original.outputs}")
                print(f"    {input_data}")
                print(f"WARNING: no implementation for '{command.name}' and arguments {str_types}\n")
            

def is_number(s):
    try:
        float(s)
        return True
    except:
        return False
    
def is_boolean(s):
    try:
        assert(str(s).lower() in ['true', 'false'])
        return True
    except:
        return False
    
def boolean(s):
    return (str(s).lower() == 'true')

def is_angle_degrees(s):
    try:
        assert(s[-1] == '°')
        float(s[:-1])
        return True
    except:
        return False