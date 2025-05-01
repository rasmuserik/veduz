from mupyjs.AST import AST
import libcst as cst

def classname(obj):
    return obj.__class__.__name__

class ParseError(Exception):
    def __init__(self, message):
        self.message = message

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
                assert(isinstance(arg.keyword, cst.Name))
                kwargs.append(arg.keyword.value)
                kwargs.append(self(arg.value))
            elif arg.star == "*":
                args.append(AST("splat", self(arg.value)))
            elif arg.star == "**":
                kwargs.append(AST("splat", self(arg.value)))
            else:
                args.append(self(arg.value))
        if len(kwargs) > 0:
            args.append(AST("dict", "_kwargs", AST("name", "True"), *kwargs))
        return AST(".__call__", self(node.func), *args)
    def parse_ClassDef(self, node):
        assert(isinstance(node.body, cst.IndentedBlock))
        return AST("class", self(node.name), *map(self, node.body.body))
    def parse_Dict(self, node):
        assert(len(node.elements) == 0)
        return AST("dict")
    def parse_Expr(self, node):
        return self(node.value)
    def parse_FunctionDef(self, node):
        assert(isinstance(node.params, cst.Parameters))
        assert(isinstance(node.body, cst.IndentedBlock))

        params = []
        for param in (node.params.params or ()) + (node.params.posonly_params or ()):
            params.append(AST(*["arg", self(param.name)] + ([self(param.default)] if param.default else [])))
        if node.params.star_arg and isinstance(node.params.star_arg, cst.Param):
            params.append(AST("arg", AST("splat", self(node.params.star_arg.name))))
        if node.params.kwonly_params:
            for param in node.params.kwonly_params or ():
                params.append(AST(*["kwarg", self(param.name)] + ([self(param.default)] if param.default else [])))
        if node.params.star_kwarg:
            params.append(AST("kwarg", AST("splat", self(node.params.star_kwarg.name))))
        return AST("fn", self(node.name), *params, *map(self, node.body.body))
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
    def parse_Pass(self, node):
        return AST("name", "pass")
    def parse_SimpleStatementLine(self, node):
        assert(len(node.body) == 1)
        return self(node.body[0])
    def parse_SimpleString(self, node):
        return node.value[1:-1]
    def parse_Slice(self, node):
        return AST(".__call__", AST("name", "slice"), self(node.lower), self(node.upper), self(node.step))
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
            raise ParseError(error)

def parse(src):
    return Parser()(cst.parse_module(src))