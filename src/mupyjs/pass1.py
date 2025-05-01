from mupyjs.AST import AST, pp

class Pass1Error(Exception):
    def __init__(self, message):
        self.message = message

class Pass_1:
    def __init__(self):
        self.scope = {}
        pass
    def handle_fn(self, ast):
        prev_scope = self.scope
        self.scope = {}
        children = [child for child in ast.children if not (child.type == "name" and child.children[0] == "pass")]
        result = AST("fn", ast.meta, *map(self, children))
        self.scope = prev_scope
        return result
    def handle_iter(self, ast):
        if ast.children[0].type == "name":
            name = ast.children[0].children[0]
            if not name in self.scope:
                ast.meta["vartype"] = "var"
                self.scope[name] = {}
        return AST(ast.type, ast.meta, *map(self, ast.children))
    def handle_set(self, ast):
        if ast.children[0].type == "name":
            name = ast.children[0].children[0]
            if not name in self.scope:
                ast.meta["vartype"] = "var"
                self.scope[name] = {}
        return AST(ast.type, ast.meta, *map(self, ast.children))
    def postprocess(self, ast):
        return ast
    def __call__(self, ast):
        if(isinstance(ast, str)): return ast
        type = ast.type
        handler = getattr(self, "handle_" + type, None)
        if handler:
            return self.postprocess(handler(ast))
        else:
            return self.postprocess(AST(type, *map(self, ast.children)))

def pass1(ast):
    return Pass_1()(ast)
