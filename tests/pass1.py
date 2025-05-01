from mupyjs.AST import AST, pp
import json

class Pass1Error(Exception):
    def __init__(self, message):
        self.message = message


class Pass_1:
    def __init__(self):
        pass
    def handle_fn(self, ast):
        children = [child for child in ast.children if not (child.type == "name" and child.children[0] == "pass")]
        return AST("fn", *map(self, children))
    def __call__(self, ast):
        if(isinstance(ast, str)): return ast
        type = ast.type
        handler = getattr(self, "handle_" + type, None)
        if handler:
            return handler(ast)
        else:
            return AST(type, *map(self, ast.children))

def pass1(ast):
    return Pass_1()(ast)
