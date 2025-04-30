from mupyjs.AST import AST
import libcst as cst

def classname(obj):
    return obj.__class__.__name__

class Parser:
    def parse_Assign(self, node):
        assert(len(node.targets) == 1)
        if isinstance(node.targets[0], cst.AssignTarget):
            assert(isinstance(node.targets[0].target, cst.Attribute))
            assert(isinstance(node.targets[0].target.attr, cst.Name))
            return AST(".__setattr__", self(node.targets[0].target.value), node.targets[0].target.attr.value, self(node.value))
        else:
            return AST("set", self(node.targets[0]), self(node.value))
    def parse_BooleanOperation(self, node):
        if isinstance(node.operator, cst.And):
            return AST("and", self(node.left), self(node.right))
        elif isinstance(node.operator, cst.Or):
            return AST("or", self(node.left), self(node.right))
        else:
            raise Exception("Unknown boolean operator", node)
    def parse_Call(self, node):
        args = []
        kwargs = []
        for arg in node.args:
            if arg.keyword:
                raise Exception("Keyword arguments not supported yet", arg)
                args.append(self(arg.keyword))
                args.append(self(arg.value))
            elif arg.star == "*":
                args.append(AST("splat", self(arg.value)))
            elif arg.star == "**":
                kwargs.append(AST("splat", self(arg.value)))
            else:
                args.append(self(arg.value))
        if len(kwargs) > 0:
            args.append(AST("dict", "_kwargs", AST("name", "True"), *kwargs))
        return AST("call", self(node.func), *args)
    def parse_ClassDef(self, node):
        assert(isinstance(node.body, cst.IndentedBlock))
        return AST("class", self(node.name), *map(self, node.body.body))
    def parse_Dict(self, node):
        assert(len(node.elements) == 0)
        return AST("dict")
    def parse_FunctionDef(self, node):
        assert(isinstance(node.params, cst.Parameters))
        assert(isinstance(node.body, cst.IndentedBlock))

        params = [AST("arg", self(param.name), self(param.default)) for param in (node.params.params or ()) + (node.params.posonly_params or ())]
        if node.params.star_arg:
            params.append(AST("arg", AST("splat", self(node.params.star_arg.name))))
        if node.params.kwonly_params or node.params.star_kwarg:
            kwparams = []
            for param in node.params.kwonly_params or ():
                kwparams.append(self(param.name.value))
                kwparams.append(self(param.default))
            if node.params.star_kwarg:
                kwparams.append(AST("splat", self(node.params.star_kwarg.name)))
            params.append(AST("arg", AST("dict", *kwparams)))
        return AST("function", self(node.name), *params, *map(self, node.body.body))

    def parse_If(self, node):
        args = ["if", self(node.test), self(node.body)]
        if classname(node.orelse) == "Else":
            args.append(self(node.orelse.body))
        else:
            print(node.orelse)
            print(classname(node.orelse))
            raise Exception("Error unhandled else")
        return AST(*args)
    def parse_IndentedBlock(self, node):
        return AST("do", *map(self, node.body))
    def parse_Index(self, node):
        return self(node.value)
    def parse_Integer(self, node):
        return AST("num", node.value)
    def parse_Module(self, node):
        return AST("module", *map(self, node.body))
    def parse_Name(self, node):
        return AST("name", node.value)
    def parse_NoneType(self, node):
        return AST("name", "None")
    def parse_SimpleStatementLine(self, node):
        assert(len(node.body) == 1)
        return self(node.body[0])
    def parse_Slice(self, node):
        return AST("call", AST("name", "slice"), self(node.lower), self(node.upper), self(node.step))
    def parse_Subscript(self, node):
        assert(len(node.slice) == 1)
        assert(isinstance(node.slice[0], cst.SubscriptElement))
        return AST(".__getitem__", self(node.value), self(node.slice[0].slice))
    def __call__(self, node):
        node_type = node.__class__.__name__
        handler = getattr(self, "parse_" + node_type, None)
        if handler:
            return handler(node)
        else:
            print(node);
            error = f"No handler for {node_type}"
            print(error)
            return AST("parse_error", error)

def parse(src):
    return Parser()(cst.parse_module(src))