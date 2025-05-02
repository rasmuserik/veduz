import libcst as cst
from mupyjs.AST import AST, pp
from mupyjs.utils import legal_method_name

cst_binops = {
    "Multiply": "__mul__",
    "Power": "__pow__",
    "FloorDivide": "__floordiv__",
    "Divide": "__truediv__",
    "Modulo": "__mod__",
    "Add": "__add__",
    "Subtract": "__sub__",
    "LeftShift": "__lshift__",
    "RightShift": "__rshift__",
    "BitOr": "__or__",
    "BitXor": "__xor__",
    "BitAnd": "__and__",
    "MatrixMultiply": "__matmul__",
    "LessThan": "__lt__",
    "GreaterThan": "__gt__",
    "Equal": "__eq__",
    "LessThanOrEqual": "__le__",
    "GreaterThanOrEqual": "__ge__",
    "NotEqual": "__ne__",
}

def classname(obj):
    return obj.__class__.__name__

class ParseError(Exception):
    def __init__(self, message):
        self.message = message

class Parser:
    def parse_Assert(self, node):
        return AST('.__call__', AST("name", "assert"), self(node.test), *([self(node.msg)] if node.msg else []))
    def parse_Assign(self, node):
        assert(len(node.targets) == 1)
        if isinstance(node.targets[0].target, cst.Attribute):
            assert(isinstance(node.targets[0].target, cst.Attribute))
            assert(isinstance(node.targets[0].target.attr, cst.Name))
            return AST(".__setattr__", self(node.targets[0].target.value), node.targets[0].target.attr.value, self(node.value))
        else:
            return AST("set", self(node.targets[0]), self(node.value))
    def parse_AssignTarget(self, node):
        return self(node.target)
    def parse_AugAssign(self, node):
        type = classname(node.operator)
        aug_ops = {
            "AddAssign": ".__add__",
        }
        assert(type in aug_ops)
        val = AST(aug_ops[type], self(node.target), self(node.value))
        if isinstance(node.target, cst.Attribute):
            assert(isinstance(node.target.attr, cst.Name))
            return AST(".__setattr__", self(node.target.value), node.target.attr.value, val)
        if isinstance(node.target, cst.Subscript):
            assert(len(node.target.slice) == 1)
            assert(isinstance(node.target.slice[0].slice, cst.Index))
            return AST(".__setitem__", self(node.target.value), self(node.target.slice[0].slice.value), val)
        assert(isinstance(node.target, cst.Name))
        return AST("set", self(node.target), val)
    def parse_Attribute(self, node):
        assert(isinstance(node.attr, cst.Name))
        return AST(".__getattr__", self(node.value), node.attr.value)
    def parse_BinaryOperation(self, node):
        cls = classname(node.operator)
        if cls in cst_binops:
            return AST("." + cst_binops[cls], self(node.left), self(node.right))
        else:
            print(node)
            raise Exception("Unknown binary operator", node)
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
        obj = self(node.func)
        if obj.type == ".__getattr__" and legal_method_name(obj.children[1]):
            return AST("." + obj.children[1], obj.children[0], *args)
        return AST(".__call__", self(node.func), *args)
    def parse_ClassDef(self, node):
        assert(isinstance(node.body, cst.IndentedBlock))
        return AST("class", self(node.name), *map(self, node.body.body))
    def parse_Comparison(self, node):
        left = node.left
        assert(len(node.comparisons) == 1)
        type = classname(node.comparisons[0].operator)
        right = node.comparisons[0].comparator
        comparisons = {
            "LessThan": "__lt__",
            "LessThanEqual": "__le__",
            "GreaterThan": "__gt__",
            "GreaterThanEqual": "__ge__",
            "Equal": "__eq__",
            "NotEqual": "__ne__",
            "Is": "__is",
            "IsNot": "__isnot",
        }
        if type in comparisons:
            result = AST("." + comparisons[type], self(left), self(right))
            return result
        if type == "In":
            return AST(".__contains__", self(right), self(left))
        if type == "NotIn":
            return AST(".__not__", AST(".__contains__", self(right), self(left)))
        raise Exception("Unknown comparison operator", node)
    def parse_Dict(self, node):
        result = [".__dict"]
        for elem in node.elements:
            if isinstance(elem, cst.DictElement):
                result.append(self(elem.key))
                result.append(self(elem.value))
            elif isinstance(elem, cst.StarredDictElement):
                result.append(AST("splat", self(elem.value)))
        return AST(*result)
    def parse_Expr(self, node):
        return self(node.value)
    def parse_For(self, node):
        return AST("for", AST("iter", self(node.target), self(node.iter)), *map(self, node.body.body))
    def parse_FormattedString(self, node):
        result = [] if len(node.parts) > 0 and isinstance(node.parts[0], cst.FormattedStringText) else [""]
        for part in node.parts:
            if isinstance(part, cst.FormattedStringText):
                result.append(part.value)
            elif isinstance(part, cst.FormattedStringExpression):
                result.append(self(part.expression))
        return AST(".__fstr", *result)
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
    def parse_GeneratorExp(self, node):
        result = ["generator", self(node.elt)];
        for_in = node.for_in
        while for_in:
            result.append(AST("iter", self(for_in.target), self(for_in.iter)))
            for if_ in for_in.ifs:
                result.append(self(if_.test))
            for_in = for_in.inner_for_in
        return AST(*result)
    def parse_ListComp(self, node):
        return AST(".__call__", AST("name", "list"), self.parse_GeneratorExp(node))
    def parse_Global(self, node):
        return AST("global", *map(self, node.names))
    def parse_If(self, node):
        result = ["if", self(node.test), self(node.body)]
        orelse = node.orelse
        while isinstance(orelse, cst.If):
            result.append(self(orelse.test))
            result.append(self(orelse.body))
            orelse = orelse.orelse
        if orelse:
            assert(isinstance(orelse, cst.Else))
            result.append(self(orelse.body))
        return AST(*result)
    def parse_IfExp(self, node):
        return AST("ifelse", self(node.test), self(node.body), self(node.orelse))
    def parse_IndentedBlock(self, node):
        return AST("do", *map(self, node.body))
    def parse_Index(self, node):
        return self(node.value)
    def helper_Import_names(self, namenode):
        if isinstance(namenode, cst.Attribute):
            asname = namenode.attr
            name = ""
            while isinstance(namenode, cst.Attribute):
                name = namenode.attr.value + "/" + name
                namenode = namenode.value
            name = namenode.value + "/" + name[:-1]
        else:
            name = namenode.value
            asname = namenode
        return [name, asname]
    def parse_Import(self, node):
        assert(isinstance(node.names[0], cst.ImportAlias))
        assert(len(node.names) == 1)
        [name, asname] = self.helper_Import_names(node.names[0].name)
        if node.names[0].asname:
            asname = node.names[0].asname.name
        return AST("import_as", name, self(asname))
    def parse_ImportFrom(self, node):
        [name, asname] = self.helper_Import_names(node.module)
        module = name
        vars = []
        for name in node.names:
            assert(not name.asname)
            vars.append(self(name.name))
        return AST("import_from", module, *vars)
    def parse_IndentedBlock(self, node):
        if len(node.body) == 1:
            return self(node.body[0])
        else:
            return AST("do", *map(self, node.body))
    def parse_Integer(self, node):
        return AST("num", node.value)
    def parse_List(self, node):
        result = [".__list"]
        for elem in node.elements:
            if isinstance(elem, cst.Element):
                result.append(self(elem.value))
            elif isinstance(elem, cst.StarredElement):
                result.append(AST("splat", self(elem.value)))
        return AST(*result)
    def parse_Module(self, node):
        return AST("module", *map(self, node.body))
    def parse_Name(self, node):
        return AST("name", node.value)
    def parse_NameItem(self, node):
        return self(node.name)
    def parse_NoneType(self, node):
        return AST("name", "None")
    def parse_Nonlocal(self, node):
        return AST("nonlocal", *map(self, node.names))
    def parse_Pass(self, node):
        return AST("name", "pass")
    def parse_Raise(self, node):
        return AST(".__call__", AST("name", "raise"), self(node.exc))
    def parse_Return(self, node):
        return AST("return", self(node.value))
    def parse_SimpleStatementLine(self, node):
        assert(len(node.body) == 1)
        return self(node.body[0])
    def parse_SimpleStatementSuite(self, node):
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
    def parse_Try(self, node):
        body = self(node.body)
        excepts = []
        name = None
        for handler in node.handlers:
            if isinstance(handler, cst.ExceptHandler):
                excepts.append(handler)
                if handler.name:
                    assert(isinstance(handler.name, cst.AsName))
                    if name:
                        assert(name == handler.name.name)
                    else:
                        name = handler.name.name.value
        if name is None:
            name = "__exception"
        result = ["try", body]
        for e in excepts:
            body = self(e.body)
            if body.type == "do":
                body = body.children
            else:
                body = [body]
            result.append(AST("except", self(e.type), AST("name", name), *body))
        if node.finalbody:
            result.append(AST("finally", self(node.finalbody.body)))
        return AST(*result)
    def parse_Tuple(self, node):
        result = [".__tuple"]
        for elem in node.elements:
            if isinstance(elem, cst.Element):
                result.append(self(elem.value))
            elif isinstance(elem, cst.StarredElement):
                result.append(AST("splat", self(elem.value)))
        return AST(*result)
    def parse_UnaryOperation(self, node):
        if isinstance(node.operator, cst.Minus):
            return AST(".__neg__", self(node.expression))
        elif isinstance(node.operator, cst.Plus):
            return AST(".__pos__", self(node.expression))
        elif isinstance(node.operator, cst.BitInvert):
            return AST(".__invert__", self(node.expression))
        elif isinstance(node.operator, cst.Not):
            return AST(".__not__", self(node.expression))
        else:
            raise Exception("Unknown unary operator", node)
    def parse_While(self, node):
        assert(isinstance(node.body, cst.IndentedBlock))
        return AST("while", self(node.test), *map(self, node.body.body))
    def __call__(self, node):
        node_type = classname(node)
        handler = getattr(self, "parse_" + node_type, None)
        if handler:
            return handler(node)
        else:
            print(node);
            error = f"No handler for {node_type}"
            raise ParseError(error)

def parse(src):
    return Parser()(cst.parse_module(src))