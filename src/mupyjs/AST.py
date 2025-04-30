
class AST:
    def __init__(self, type, *children):
        self.type = type
        if children and isinstance(children[0], dict):
            self.annotations = children[0]
            self.children = children[1:]
        else:
            self.annotations = {}
            self.children = children
    def to_list(self):
        def ast_to_list(obj):
            return obj if isinstance(obj, str) else obj.to_list()
        result = [self.type]
        for name, value in self.annotations.items():
            result.append([name, *map(ast_to_list, value if isinstance(value, list) else [value])])
        for child in self.children:
            result.append(ast_to_list(child))
        return result


def ast_to_pplist(ast):
    if isinstance(ast, str):
        return '"' + ast + '"'
    if ast.type == "name":
        return ast.children[0]
    if ast.type == "num":
        return ast.children[0]
    return ["(", ast.type, *map(ast_to_pplist, ast.children), ")"]

def ppline(pplist, maxlen):
    if isinstance(pplist, str): return pplist
    result = pplist[0]
    for child in pplist[1:-1]:
        result += ppline(child, maxlen - len(result)) + " ";
    result += pplist[-1]
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
            result += pp_pplist(child, indent + "  ") + "\n" + indent
        result += pp_pplist(pplist[-2], indent + "  ") + pplist[-1]
        return result
def pp(ast):
    return pp_pplist(ast_to_pplist(ast))
