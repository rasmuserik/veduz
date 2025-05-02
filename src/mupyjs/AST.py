import json
import re

class AST:
    def __init__(self, type, *children):
        self.type = type
        if(len(children) > 0 and isinstance(children[0], dict)):    
            self.meta = children[0]
            self.children = children[1:]
        else:
            self.meta = {}
            self.children = children

def ast_to_pplist(ast):
    if isinstance(ast, str):
        return json.dumps(ast)
    if ast.type == "name":
        return ast.children[0]
    if ast.type == "num":
        return ast.children[0]
    return ["(", ast.type, *map(ast_to_pplist, ast.children), ")"]

def ppline(pplist, maxlen):
    if isinstance(pplist, str): return pplist
    result = pplist[0]
    for child in pplist[1:-1]:
        result = result + ppline(child, maxlen - len(result)) + " "
    result = result[0:-1] + pplist[-1]
    if len(result) > maxlen:
        raise Exception("Line too long")
    return result

maxlen = 80
def pp_pplist(pplist, indent = "  "):
    try:
        return ppline(pplist, maxlen - len(indent))
    except Exception as e:
        result = pplist[0] + pplist[1] + "\n" + indent
        for child in pplist[2:-2]:
            result = result + pp_pplist(child, indent + "  ") + "\n" + indent
        result = result + pp_pplist(pplist[-2], indent + "  ") + pplist[-1]
        return result
def pp(ast):
    return pp_pplist(ast_to_pplist(ast))

def _parse_pp(str):
    str = str.strip()
    if str[0] == '"':
        i = 1
        while True:
            if str[i] == '"':
                return [str[1:i], str[i+1:]]
            if str[i] == '\\': i = i + 1
            i = i + 1
    elif str[0] == '(':
        str = str[1:].strip();
        result = []
        while str and str[0] != ')':
            [first, rest] = _parse_pp(str)
            result.append(first)
            str = rest
        return [AST(result[0].children[0], *result[1:]), str[1:]]
    else:
        result = ""
        while str and not str[0].isspace() and str[0] != '(' and str[0] != ')':
            result = result + str[0]
            str = str[1:]
        if re.match(r"^\d+[.]?\d*$", result):
            return [AST("num", result), str]
        else:
            return [AST("name", result), str]


def parse_pp(str):
    result = []
    while str.strip():
        [first, rest] = _parse_pp(str)
        result.append(first)
        str = rest
    return AST("do", *result)