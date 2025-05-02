import { print } from './runtime.js';
import * as cst from '@/libcst';
import { AST, pp } from '@/mupyjs/AST';
import { legal_method_name } from '@/mupyjs/utils';
var cst_binops = __dict(
  'Multiply',
  '__mul__',
  'Power',
  '__pow__',
  'FloorDivide',
  '__floordiv__',
  'Divide',
  '__truediv__',
  'Modulo',
  '__mod__',
  'Add',
  '__add__',
  'Subtract',
  '__sub__',
  'LeftShift',
  '__lshift__',
  'RightShift',
  '__rshift__',
  'BitOr',
  '__or__',
  'BitXor',
  '__xor__',
  'BitAnd',
  '__and__',
  'MatrixMultiply',
  '__matmul__',
  'LessThan',
  '__lt__',
  'GreaterThan',
  '__gt__',
  'Equal',
  '__eq__',
  'LessThanOrEqual',
  '__le__',
  'GreaterThanOrEqual',
  '__ge__',
  'NotEqual',
  '__ne__'
);
function classname(obj) {
  return obj.__class__.__name__;
}
class ParseError {
  constructor(message) {
    const self = this;
    self['message'] = message;
  }
}
class Parser {
  parse_Assert(node) {
    const self = this;
    return new AST(
      '.__call__',
      new AST('name', 'assert'),
      self(node.test),
      ...(node.msg ? [self(node.msg)] : [])
    );
  }
  parse_Assign(node) {
    const self = this;
    assert((len(node.targets) ?? Nil).__eq__(1));
    if (isinstance(node.targets.__getitem__(0).target, cst.Attribute)) {
      assert(isinstance(node.targets.__getitem__(0).target, cst.Attribute));
      assert(isinstance(node.targets.__getitem__(0).target.attr, cst.Name));
      return new AST(
        '.__setattr__',
        self(node.targets.__getitem__(0).target.value),
        node.targets.__getitem__(0).target.attr.value,
        self(node.value)
      );
    } else {
      return new AST(
        'set',
        self(node.targets.__getitem__(0)),
        self(node.value)
      );
    }
  }
  parse_AssignTarget(node) {
    const self = this;
    return self(node.target);
  }
  parse_AugAssign(node) {
    const self = this;
    var type = classname(node.operator);
    var aug_ops = __dict('AddAssign', '.__add__');
    assert(aug_ops.__contains__(type));
    var val = new AST(
      aug_ops.__getitem__(type),
      self(node.target),
      self(node.value)
    );
    if (isinstance(node.target, cst.Attribute)) {
      assert(isinstance(node.target.attr, cst.Name));
      return new AST(
        '.__setattr__',
        self(node.target.value),
        node.target.attr.value,
        val
      );
    }
    if (isinstance(node.target, cst.Subscript)) {
      assert((len(node.target.slice) ?? Nil).__eq__(1));
      assert(isinstance(node.target.slice.__getitem__(0).slice, cst.Index));
      return new AST(
        '.__setitem__',
        self(node.target.value),
        self(node.target.slice.__getitem__(0).slice.value),
        val
      );
    }
    assert(isinstance(node.target, cst.Name));
    return new AST('set', self(node.target), val);
  }
  parse_Attribute(node) {
    const self = this;
    assert(isinstance(node.attr, cst.Name));
    return new AST('.__getattr__', self(node.value), node.attr.value);
  }
  parse_BinaryOperation(node) {
    const self = this;
    var cls = classname(node.operator);
    if (cst_binops.__contains__(cls)) {
      return new AST(
        '.'.__add__(cst_binops.__getitem__(cls)),
        self(node.left),
        self(node.right)
      );
    } else {
      print(node);
      raise(new Exception('Unknown binary operator', node));
    }
  }
  parse_BooleanOperation(node) {
    const self = this;
    if (isinstance(node.operator, cst.And)) {
      return new AST('and', self(node.left), self(node.right));
    } else if (isinstance(node.operator, cst.Or)) {
      return new AST('or', self(node.left), self(node.right));
    } else {
      raise(new Exception('Unknown boolean operator', node));
    }
  }
  parse_Call(node) {
    const self = this;
    var args = [];
    var kwargs = [];
    for (var arg of node.args) {
      if (arg.keyword) {
        assert(isinstance(arg.keyword, cst.Name));
        kwargs.append(arg.keyword.value);
        kwargs.append(self(arg.value));
      } else if ((arg.star ?? Nil).__eq__('*')) {
        args.append(new AST('splat', self(arg.value)));
      } else if ((arg.star ?? Nil).__eq__('**')) {
        kwargs.append(new AST('splat', self(arg.value)));
      } else {
        args.append(self(arg.value));
      }
    }
    if (len(kwargs).__gt__(0)) {
      args.append(new AST('kwargs', ...kwargs));
    }
    var obj = self(node.func);
    if (
      (obj.type ?? Nil).__eq__('.__getattr__') &&
      legal_method_name(obj.children.__getitem__(1))
    ) {
      return new AST(
        '.'.__add__(obj.children.__getitem__(1)),
        obj.children.__getitem__(0),
        ...args
      );
    }
    return new AST('.__call__', self(node.func), ...args);
  }
  parse_ClassDef(node) {
    const self = this;
    assert(isinstance(node.body, cst.IndentedBlock));
    return new AST('class', self(node.name), ...map(self, node.body.body));
  }
  parse_Comparison(node) {
    const self = this;
    var left = node.left;
    assert((len(node.comparisons) ?? Nil).__eq__(1));
    var type = classname(node.comparisons.__getitem__(0).operator);
    var right = node.comparisons.__getitem__(0).comparator;
    var comparisons = __dict(
      'LessThan',
      '__lt__',
      'LessThanEqual',
      '__le__',
      'GreaterThan',
      '__gt__',
      'GreaterThanEqual',
      '__ge__',
      'Equal',
      '__eq__',
      'NotEqual',
      '__ne__',
      'Is',
      '__is',
      'IsNot',
      '__isnot'
    );
    if (comparisons.__contains__(type)) {
      var result = new AST(
        '.'.__add__(comparisons.__getitem__(type)),
        self(left),
        self(right)
      );
      return result;
    }
    if ((type ?? Nil).__eq__('In')) {
      return new AST('.__contains__', self(right), self(left));
    }
    if ((type ?? Nil).__eq__('NotIn')) {
      return new AST(
        '.__not__',
        new AST('.__contains__', self(right), self(left))
      );
    }
    raise(new Exception('Unknown comparison operator', node));
  }
  parse_Dict(node) {
    const self = this;
    var result = ['.__dict'];
    for (var elem of node.elements) {
      if (isinstance(elem, cst.DictElement)) {
        result.append(self(elem.key));
        result.append(self(elem.value));
      } else if (isinstance(elem, cst.StarredDictElement)) {
        result.append(new AST('splat', self(elem.value)));
      }
    }
    return new AST(...result);
  }
  parse_Expr(node) {
    const self = this;
    return self(node.value);
  }
  parse_For(node) {
    const self = this;
    return new AST(
      'for',
      new AST('iter', self(node.target), self(node.iter)),
      ...map(self, node.body.body)
    );
  }
  parse_FormattedString(node) {
    const self = this;
    var result =
      len(node.parts).__gt__(0) &&
      isinstance(node.parts.__getitem__(0), cst.FormattedStringText)
        ? []
        : [''];
    for (var part of node.parts) {
      if (isinstance(part, cst.FormattedStringText)) {
        result.append(part.value);
      } else if (isinstance(part, cst.FormattedStringExpression)) {
        result.append(self(part.expression));
      }
    }
    return new AST('.__fstr', ...result);
  }
  parse_FunctionDef(node) {
    const self = this;
    assert(isinstance(node.params, cst.Parameters));
    assert(isinstance(node.body, cst.IndentedBlock));
    var params = [];
    for (var param of (node.params.params || []).__add__(
      node.params.posonly_params || []
    )) {
      params.append(
        new AST(
          ...['arg', self(param.name)].__add__(
            param.default ? [self(param.default)] : []
          )
        )
      );
    }
    if (node.params.star_arg && isinstance(node.params.star_arg, cst.Param)) {
      params.append(
        new AST('arg', new AST('splat', self(node.params.star_arg.name)))
      );
    }
    if (node.params.kwonly_params) {
      for (param of node.params.kwonly_params || []) {
        params.append(
          new AST(
            ...['kwarg', self(param.name)].__add__(
              param.default ? [self(param.default)] : []
            )
          )
        );
      }
    }
    if (node.params.star_kwarg) {
      params.append(
        new AST('kwarg', new AST('splat', self(node.params.star_kwarg.name)))
      );
    }
    return new AST(
      'fn',
      self(node.name),
      ...params,
      ...map(self, node.body.body)
    );
  }
  parse_GeneratorExp(node) {
    const self = this;
    var result = ['generator', self(node.elt)];
    var for_in = node.for_in;
    while (for_in) {
      result.append(new AST('iter', self(for_in.target), self(for_in.iter)));
      for (var if_ of for_in.ifs) {
        result.append(self(if_.test));
      }
      for_in = for_in.inner_for_in;
    }
    return new AST(...result);
  }
  parse_ListComp(node) {
    const self = this;
    return new AST(
      '.__call__',
      new AST('name', 'list'),
      self.parse_GeneratorExp(node)
    );
  }
  parse_Global(node) {
    const self = this;
    return new AST('global', ...map(self, node.names));
  }
  parse_If(node) {
    const self = this;
    var result = ['if', self(node.test), self(node.body)];
    var orelse = node.orelse;
    while (isinstance(orelse, cst.If)) {
      result.append(self(orelse.test));
      result.append(self(orelse.body));
      orelse = orelse.orelse;
    }
    if (orelse) {
      assert(isinstance(orelse, cst.Else));
      result.append(self(orelse.body));
    }
    return new AST(...result);
  }
  parse_IfExp(node) {
    const self = this;
    return new AST(
      'ifelse',
      self(node.test),
      self(node.body),
      self(node.orelse)
    );
  }
  parse_IndentedBlock(node) {
    const self = this;
    return new AST('do', ...map(self, node.body));
  }
  parse_Index(node) {
    const self = this;
    return self(node.value);
  }
  helper_Import_names(namenode) {
    const self = this;
    if (isinstance(namenode, cst.Attribute)) {
      var asname = namenode.attr;
      var name = '';
      while (isinstance(namenode, cst.Attribute)) {
        name = namenode.attr.value.__add__('/').__add__(name);
        var namenode = namenode.value;
      }
      name = namenode.value
        .__add__('/')
        .__add__(name.__getitem__(slice(undefined, (1).__neg__(), undefined)));
    } else {
      name = namenode.value;
      asname = namenode;
    }
    return [name, asname];
  }
  parse_Import(node) {
    const self = this;
    assert(isinstance(node.names.__getitem__(0), cst.ImportAlias));
    assert((len(node.names) ?? Nil).__eq__(1));
    [name, asname] = self.helper_Import_names(node.names.__getitem__(0).name);
    if (node.names.__getitem__(0).asname) {
      var asname = node.names.__getitem__(0).asname.name;
    }
    return new AST('import_as', name, self(asname));
  }
  parse_ImportFrom(node) {
    const self = this;
    [name, asname] = self.helper_Import_names(node.module);
    var module = name;
    var vars = [];
    for (var name of node.names) {
      assert(name.asname.__not__());
    }
    return new AST('import_from', module, ...vars);
  }
  parse_IndentedBlock(node) {
    const self = this;
    if ((len(node.body) ?? Nil).__eq__(1)) {
      return self(node.body.__getitem__(0));
    } else {
      return new AST('do', ...map(self, node.body));
    }
  }
  parse_Integer(node) {
    const self = this;
    return new AST('num', node.value);
  }
  parse_List(node) {
    const self = this;
    var result = ['.__list'];
    for (var elem of node.elements) {
      if (isinstance(elem, cst.Element)) {
        result.append(self(elem.value));
      } else if (isinstance(elem, cst.StarredElement)) {
        result.append(new AST('splat', self(elem.value)));
      }
    }
    return new AST(...result);
  }
  parse_Module(node) {
    const self = this;
    return new AST('do', ...map(self, node.body));
  }
  parse_Name(node) {
    const self = this;
    return new AST('name', node.value);
  }
  parse_NameItem(node) {
    const self = this;
    return self(node.name);
  }
  parse_NoneType(node) {
    const self = this;
    return new AST('name', 'None');
  }
  parse_Nonlocal(node) {
    const self = this;
    return new AST('nonlocal', ...map(self, node.names));
  }
  parse_Pass(node) {
    const self = this;
    return new AST('name', 'pass');
  }
  parse_Raise(node) {
    const self = this;
    return new AST('.__call__', new AST('name', 'raise'), self(node.exc));
  }
  parse_Return(node) {
    const self = this;
    return new AST('return', self(node.value));
  }
  parse_SimpleStatementLine(node) {
    const self = this;
    assert((len(node.body) ?? Nil).__eq__(1));
    return self(node.body.__getitem__(0));
  }
  parse_SimpleStatementSuite(node) {
    const self = this;
    assert((len(node.body) ?? Nil).__eq__(1));
    return self(node.body.__getitem__(0));
  }
  parse_SimpleString(node) {
    const self = this;
    return node.value.__getitem__(slice(1, (1).__neg__(), undefined));
  }
  parse_Slice(node) {
    const self = this;
    return new AST(
      '.__call__',
      new AST('name', 'slice'),
      self(node.lower),
      self(node.upper),
      self(node.step)
    );
  }
  parse_Subscript(node) {
    const self = this;
    assert((len(node.slice) ?? Nil).__eq__(1));
    assert(isinstance(node.slice.__getitem__(0), cst.SubscriptElement));
    return new AST(
      '.__getitem__',
      self(node.value),
      self(node.slice.__getitem__(0).slice)
    );
  }
  parse_Try(node) {
    const self = this;
    var body = self(node.body);
    var excepts = [];
    var name = undefined;
    for (var handler of node.handlers) {
      if (isinstance(handler, cst.ExceptHandler)) {
        excepts.append(handler);
        if (handler.name) {
          assert(isinstance(handler.name, cst.AsName));
          if (name) {
            assert((name ?? Nil).__eq__(handler.name.name));
          } else {
            name = handler.name.name.value;
          }
        }
      }
    }
    if (name === undefined) {
      name = '__exception';
    }
    var result = ['try', body];
    for (var e of excepts) {
      body = self(e.body);
    }
    if (node.finalbody) {
      result.append(new AST('finally', self(node.finalbody.body)));
    }
    return new AST(...result);
  }
  parse_Tuple(node) {
    const self = this;
    var result = ['.__tuple'];
    for (var elem of node.elements) {
      if (isinstance(elem, cst.Element)) {
        result.append(self(elem.value));
      } else if (isinstance(elem, cst.StarredElement)) {
        result.append(new AST('splat', self(elem.value)));
      }
    }
    return new AST(...result);
  }
  parse_UnaryOperation(node) {
    const self = this;
    if (isinstance(node.operator, cst.Minus)) {
      return new AST('.__neg__', self(node.expression));
    } else if (isinstance(node.operator, cst.Plus)) {
      return new AST('.__pos__', self(node.expression));
    } else if (isinstance(node.operator, cst.BitInvert)) {
      return new AST('.__invert__', self(node.expression));
    } else if (isinstance(node.operator, cst.Not)) {
      return new AST('.__not__', self(node.expression));
    } else {
      raise(new Exception('Unknown unary operator', node));
    }
  }
  parse_While(node) {
    const self = this;
    assert(isinstance(node.body, cst.IndentedBlock));
    return new AST('while', self(node.test), ...map(self, node.body.body));
  }
  __call__(node) {
    const self = this;
    var node_type = classname(node);
    var handler = getattr(self, 'parse_'.__add__(node_type), undefined);
    if (handler) {
      return handler(node);
    } else {
      print(node);
      var error = 'No handler for ' + node_type;
      raise(new ParseError(error));
    }
  }
}
function parse(src) {
  return new Parser()(cst.parse_module(src));
}
