import ast
from ..geo.construction import *

#--------------------------------------------------------------------------

def selectPut(astElem):
    if type(astElem) == ast.Name:
        return astElem.id
    elif type(astElem) == ast.Constant:
        return astElem.value
    else:
        return astElem

def getNewName(constr):
    num = 1
    while ('_' + str(num)) in constr.phantoms: num += 1
    return '_' + str(num)

def reset_fixed_and_alpha(constr, outputs):
    for name in outputs:
        elem = constr.element(name)
        if elem is not None:
            elem.fixed = False
            elem.alpha = None

def addToConstr(constr, what, outputs = [], debug = False, update = False):
    inputs = []
    command = ''
    
    if type(what) == ast.Call:
        command = what.func.id
        for elem in what.args:
            inputs.append(selectPut(elem))
    elif type(what) == ast.BinOp:
        command = ast.dump(what.op)[:-2]
        inputs.append(selectPut(what.left))
        inputs.append(selectPut(what.right)) 
    elif type(what) == ast.UnaryOp:
        command = ast.dump(what.op)[:-2]
        inputs.append(selectPut(what.operand))
    elif (type(what) == ast.Name) | (type(what) == ast.Constant):
        command = 'Assign'
        inputs.append(selectPut(what))

    else: assert('inputs of ' + str(ast.dump(what)) + ': не поддерживается')

    if debug: print(str(outputs) + ' = ' + command + str(inputs))

    if command == 'Assign':
        constr.update(outputs[0], inputs[0])
        reset_fixed_and_alpha(constr, outputs)
    else:
        for i in range(len(inputs)):
            if (type(inputs[i]) != str) & (type(inputs[i]) != int) & (type(inputs[i]) != float):
                key = getNewName(constr)
                constr.phantoms[key] = None
                inputs[i] = addToConstr(constr, inputs[i], [key], debug, update)[0]
        if update:
            constr.updateCommand(command, inputs, outputs)
        else:
            constr.add(Command(command, inputs, outputs))
        reset_fixed_and_alpha(constr, outputs)

    if debug: print(str(outputs) + ' = ' + command + str(inputs))

    return outputs

def assign(constr, action, debug = False, update = False):
    outputs = []

    for elem in action.targets:
        if type(elem) == ast.Name: outputs.append(elem.id)
        elif type(elem) == ast.Tuple:
            for el in elem.elts:
                if type(el) == ast.Name: outputs.append(el.id)
                else: assert("Среди элементов на выходе должны быть только переменные")
        else: assert("Среди элементов на выходе должны быть только переменные")
    
    outputs = addToConstr(constr, action.value, outputs, debug, update)

def putCode(constr, strCode, debug = False, update = False):
    tree = ast.parse(strCode)

    for action in tree.body:
        if type(action) == ast.Assign:
            assign(constr, action, debug, update)
            
    constr.sortCommands()
    constr.rebuild(full = True)

#--------------------------------------------------------------------------

def loadCode(constr, file_py, debug = False, update = False):
    putCode(constr, open(file_py).read(), debug, update)

def load(file_py, build = False, debug = False, update = False):
    tree = ast.parse(open(file_py).read())
    constr = Construction()

    for action in tree.body:
        if type(action) == ast.Assign:
            assign(constr, action, debug, update)

    if build: constr.rebuild(debug = debug)

    return constr
