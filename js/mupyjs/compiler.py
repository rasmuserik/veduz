import json
from mupyjs.AST import AST, pp
from mupyjs.utils import legal_method_name

class CompileError(Exception):
    def __init__(self, message):
        self.message = message

name_map = {
    "True": "true",
    "False": "false",
    "None": "undefined",
    "pass": "",
}

class Compiler:
    def __init__(self):
        self.compiling_class = False
    def compile_arg(self, ast):
        return self(ast.children[0])
    def compile_and(self, ast):
        return "(" + self(ast.children[0]) + ")&&(" + self(ast.children[1]) + ")"
    def compile_class(self, ast):
        compiling_class = self.compiling_class
        self.compiling_class = True
        result = "class " + self(ast.children[0]) + "{"
        for child in ast.children[1:]:
            if(child.type == "fn" and child.children[0].children[0] == "__init__"):
                child = AST("fn", AST("name", "constructor"), *child.children[1:])
            result += self(child)
        self.compiling_class = compiling_class
        return result + "}"
    def compile_do(self, ast):
        return ";\n".join(map(self, ast.children))
    def compile_fn(self, ast):
        compiling_class = self.compiling_class
        self.compiling_class = False
        result = "" if compiling_class else "function "
        i = 1
        args = []
        set_self = ""
        while(i < len(ast.children) and ast.children[i].type == "arg"):
            if ast.children[i].children[0].children[0] == "self":
                set_self = "const self = this;\n"
            else:
                args.append(self(ast.children[i]))
            i += 1
        kwargs = ""
        while(i < len(ast.children) and ast.children[i].type == "kwarg"):
            kwarg = ast.children[i].children[0]
            if(kwarg.type == "splat"):
                kwargs += "..." + self(kwarg.children[0]) + ","
            else:
                kwargs += kwarg.children[0] + ','
            i += 1
        if(kwargs):
            args.append("{" + kwargs + "}")
        result += self(ast.children[0]) + "(" + ",".join(args) + "){" + set_self
        while(i < len(ast.children)):
            result += self(ast.children[i]) + ";\n"
            i += 1
        result += "}"
        self.compiling_class = compiling_class
        return result;
    def compile_for(self, ast):
        iter = ast.children[0]
        vartype = ""
        if "vartype" in iter.meta:
            vartype = iter.meta["vartype"] + " "
        return "for(" + vartype + " " + self(iter.children[0])+ " of " + self(iter.children[1]) + "){" + self(ast.children[1]) + "}"
    def compile_generator(self, ast):
        result = "(function*(){\n"
        for child in ast.children[1:]:
            if child.type == "iter":
                result += "for(const " + self(child.children[0]) + " of " + self(child.children[1]) + ")\n"
            else:
                result += "if(" + self(child) + ")\n"
        result += "yield " + self(ast.children[0]) + ";\n"
        result += "})()"
        return result
    def compile_global(self, ast):
        return ""
    def compile_if(self, ast):
        result = "if(" + self(ast.children[0]) + "){" + self(ast.children[1]) + "}"
        i = 2
        while(i < len(ast.children) - 1):
            result += "else if(" + self(ast.children[i]) + "){" + self(ast.children[i + 1]) + "}"
            i += 2
        if(i < len(ast.children)):
            result += "else{" + self(ast.children[i]) + "}"
        return result
    def compile_ifelse(self, ast):
        return "(" + self(ast.children[0]) + ")?(" + self(ast.children[1]) + "):(" + self(ast.children[2]) + ")"
    def compile_import_as(self, ast):
        return "import * as " + self(ast.children[1]) + ' from "@/' + ast.children[0] + '"'
    def compile_import_from(self, ast):
        return "import {" + ", ".join(self(child) for child in ast.children[1:]) + '} from "@/' + ast.children[0] + '"'
    def compile_kwargs(self, ast):
        children = []
        i = 0
        while(i < len(ast.children)):
            if(isinstance(ast.children[i], str)):
                children.append(self(ast.children[i]) + ":" + self(ast.children[i + 1]))
                i += 2
            else:
                print(pp(ast), i)
                assert(ast.children[i].type == "splat")
                children.append(self(ast.children[i]))
                i += 1
        return "{_kwargs:true," + ", ".join(children) + "}"
    def compile_method_call(self, ast):
        method = ast.type[1:]
        return "(" + self(ast.children[0]) + ")." + method + "(" + ", ".join(self(child) for child in ast.children[1:]) + ")"
    def compile_name(self, ast):
        assert(len(ast.children) == 1)
        if ast.children[0] in name_map:
            return name_map[ast.children[0]]
        return ast.children[0]
    def compile_nonlocal(self, ast):
        return ""
    def compile_num(self, ast):
        assert(len(ast.children) == 1)
        return str(ast.children[0])
    def compile_or(self, ast):
        return "(" + self(ast.children[0]) + ")||(" + self(ast.children[1]) + ")"
    def compile_return(self, ast):
        return "return (" + self(ast.children[0]) + ")"
    def compile_set(self, ast):
        vartype = ""
        if "vartype" in ast.meta:
            vartype = ast.meta["vartype"] + " "
        return vartype + self(ast.children[0]) + " = " + self(ast.children[1])
    def compile_splat(self, ast):
        assert(len(ast.children) == 1)
        return "..." + self(ast.children[0])
    def compile_try(self, ast):
        body = []
        excepts = []
        finallyBody = []
        for child in ast.children:
            if child.type == "except":
                excepts.append(child)
            elif child.type == "finally":
                finallyBody = child
            else:
                body.append(child)
        result = "try{" + ";\n".join(map(self, body)) + "}"
        if len(excepts) > 0:
            name = self(excepts[0].children[1])
            result += "catch(" + name + "){"
            for e in excepts:
                result += "if(" + name + " instanceof " + self(e.children[0]) + "){"
                result += ";\n".join(map(self, e.children[2:]))
                result += "} else "
            result = result[:-6] + "}"
        if finallyBody:
            result += "finally{" + ";\n".join(map(self, finallyBody.children)) + "}"
        return result
    def compile_while(self, ast):
        return "while(" + self(ast.children[0]) + "){" + ";\n".join(map(self, ast.children[1:])) + "}"
    def method___call__(self, ast):
        prefix = "("
        if(ast.children[0].type == "name" and ast.children[0].children[0][0].isupper()):
            prefix = "new ("
        return prefix + self(ast.children[0]) + ")(" + ", ".join(self(child) for child in ast.children[1:]) + ")"
    def method___dict(self, ast):
        return "__dict(" + ", ".join([self(child) for child in ast.children]) + ")"
    def method___eq__(self, ast):
        return "(" + self(ast.children[0]) + "??Nil).__eq__(" + self(ast.children[1]) + ")"
    def method___fstr(self, ast):
        return "+".join([self(child) for child in ast.children])
    def method___is(self, ast):
        return "(" + self(ast.children[0]) + ") === (" + self(ast.children[1]) + ")"
    def method___isnot(self, ast):
        return "(" + self(ast.children[0]) + ") !== (" + self(ast.children[1]) + ")"
    def method___getattr__(self, ast):
        if legal_method_name(ast.children[1]):
            return "(" + self(ast.children[0]) + ")." + ast.children[1]
        else:
            return self.compile_method_call(ast)
    def method___list(self, ast):
        return "[" + ", ".join([self(child) for child in ast.children]) + "]"
    def method___ne__(self, ast):
        return "(" + self(ast.children[0]) + "??Nil).__ne__(" + self(ast.children[1]) + ")"
    def method___setattr__(self, ast):
        return "(" + self(ast.children[0]) + ")[" + self(ast.children[1]) + "] = " + self(ast.children[2])
    def method___tuple(self, ast):
        return "[" + ", ".join([self(child) for child in ast.children]) + "]"
    def __call__(self, ast):
        if(isinstance(ast, str)):
            return json.dumps(ast)
        type = ast.type
        if(type[0] == "."):
            handler = getattr(self, "method_" + type[1:], None)
            if not handler:
                handler = getattr(self, "compile_method_call", None)
        else:
            handler = getattr(self, "compile_" + type, None)
        if handler:
            return handler(ast)
        else:
            print(pp(ast));
            error = f"No compile-handler for {type}"
            raise CompileError(error)

def compile(ast):
    return Compiler()(ast)

def compile_module(ast):
    return "import * as runtime from '@/mupyjs/runtime.js';Object.assign(self, runtime);\n" + compile(ast)
