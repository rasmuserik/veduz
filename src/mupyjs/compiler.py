from mupyjs.AST import AST, pp
import json
def classname(obj):
    return obj.__class__.__name__

class CompileError(Exception):
    def __init__(self, message):
        self.message = message

name_map = {
    "True": "true",
    "False": "false",
    "None": "undefined",
}

class Compiler:
    def __init__(self):
        self.compiling_class = False
    def compile_arg(self, ast):
        return self(ast.children[0])
    def compile_and(self, ast):
        return "(" + self(ast.children[0]) + "&&" + self(ast.children[1]) + ")"
    def compile_call(self, ast):
        return self(ast.children[0]) + "(" + ", ".join(self(child) for child in ast.children[1:]) + ")"
    def compile_class(self, ast):
        self.compiling_class = True
        result = "class " + self(ast.children[0]) + "{"
        for child in ast.children[1:]:
            if(child.type == "fn" and child.children[0].children[0] == "__init__"):
                child = AST("fn", AST("name", "constructor"), *child.children[1:])
            result += self(child)
        return result + "}"
    def compile_dict(self, ast):
        children = [];
        i = 0;
        while(i < len(ast.children)):
            if(isinstance(ast.children[i], str)):
                children.append(self(ast.children[i]) + ":" + self(ast.children[i + 1]))
                i += 2;
            else:
                assert(ast.children[i].type == "splat")
                children.append(self(ast.children[i]))
                i += 1;
        return "{" + ", ".join(children) + "}"
    def compile_do(self, ast):
        return ";".join(map(self, ast.children[1:]))
    def compile_fn(self, ast):
        compiling_class = self.compiling_class
        self.compiling_class = False
        result = "" if compiling_class else "function "
        i = 1
        args = []
        set_self = "";
        while(i < len(ast.children) and ast.children[i].type == "arg"):
            if ast.children[i].children[0].children[0] == "self":
                set_self = "const self = this;"
            else:
                args.append(self(ast.children[i]))
            i += 1
        result += self(ast.children[0]) + "(" + ",".join(args) + "){" + set_self
        while(i < len(ast.children)):
            result += self(ast.children[i]) + ";"
            i += 1
        result += "}"
        self.compiling_class = compiling_class
        return result;
    def compile_if(self, ast):
        return "if(" + self(ast.children[0]) + "){" + self(ast.children[1]) + "}"
        i = 2
        while(i < len(ast.children) - 1):
            result += "else if(" + self(ast.children[i]) + "){" + self(ast.children[i + 1]) + "}"
            i += 2
        if(i < len(ast.children)):
            result += "else{" + self(ast.children[i]) + "}"
        return result
    def compile_method_call(self, ast):
        method = ast.type[1:]
        return self(ast.children[0]) + "." + method + "(" + ", ".join(self(child) for child in ast.children[1:]) + ")"
    def compile_module(self, ast):
        return "\n".join(self(child) for child in ast.children)
    def compile_name(self, ast):
        assert(len(ast.children) == 1)
        if(name_map.get(ast.children[0])):
            return name_map[ast.children[0]]
        return ast.children[0]
    def compile_num(self, ast):
        assert(len(ast.children) == 1)
        return str(ast.children[0])
    def compile_splat(self, ast):
        assert(len(ast.children) == 1)
        return "..." + self(ast.children[0])
    def __call__(self, ast):
        if(isinstance(ast, str)):
            return json.dumps(ast)
        type = ast.type
        if(type[0] == "."):
            type = "method_call"
        handler = getattr(self, "compile_" + type, None)
        if handler:
            return handler(ast)
        else:
            print(pp(ast));
            error = f"No compile-handler for {type}"
            raise CompileError(error)

def parse(src):
    return Parser()(cst.parse_module(src))