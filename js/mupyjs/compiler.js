import * as runtime from '@/mupyjs/runtime.js';
Object.assign(self, runtime);
import * as json from '@/json';
import { AST, pp } from '@/mupyjs/AST';
import { legal_method_name } from '@/mupyjs/utils';
class CompileError {
  constructor(message) {
    const self = this;
    self['message'] = message;
  }
}
var name_map = __dict(
  'True',
  'true',
  'False',
  'false',
  'None',
  'undefined',
  'pass',
  ''
);
class Compiler {
  constructor() {
    const self = this;
    self['compiling_class'] = false;
  }
  compile_arg(ast) {
    const self = this;
    return self(ast.children.__getitem__(0));
  }
  compile_and(ast) {
    const self = this;
    return '('
      .__add__(self(ast.children.__getitem__(0)))
      .__add__(')&&(')
      .__add__(self(ast.children.__getitem__(1)))
      .__add__(')');
  }
  compile_class(ast) {
    const self = this;
    var compiling_class = self.compiling_class;
    self['compiling_class'] = true;
    var result = 'class '
      .__add__(self(ast.children.__getitem__(0)))
      .__add__('{');
    for (var child of ast.children.__getitem__(
      slice(1, undefined, undefined)
    )) {
      if (
        (child.type ?? Nil).__eq__('fn') &&
        (child.children.__getitem__(0).children.__getitem__(0) ?? Nil).__eq__(
          '__init__'
        )
      ) {
        child = new AST(
          'fn',
          new AST('name', 'constructor'),
          ...child.children.__getitem__(slice(1, undefined, undefined))
        );
      }
    }
    self['compiling_class'] = compiling_class;
    return result.__add__('}');
  }
  compile_do(ast) {
    const self = this;
    return ';\\n'.join(map(self, ast.children));
  }
  compile_fn(ast) {
    const self = this;
    var compiling_class = self.compiling_class;
    self['compiling_class'] = false;
    var result = compiling_class ? '' : 'function ';
    var i = 1;
    var args = [];
    var set_self = '';
    while (
      i.__lt__(len(ast.children)) &&
      (ast.children.__getitem__(i).type ?? Nil).__eq__('arg')
    ) {
      if (
        (
          ast.children
            .__getitem__(i)
            .children.__getitem__(0)
            .children.__getitem__(0) ?? Nil
        ).__eq__('self')
      ) {
        set_self = 'const self = this;\\n';
      } else {
        args.append(self(ast.children.__getitem__(i)));
      }
      i = i.__add__(1);
    }
    var kwargs = '';
    while (
      i.__lt__(len(ast.children)) &&
      (ast.children.__getitem__(i).type ?? Nil).__eq__('kwarg')
    ) {
      var kwarg = ast.children.__getitem__(i).children.__getitem__(0);
      if ((kwarg.type ?? Nil).__eq__('splat')) {
        kwargs = kwargs.__add__(
          '...'.__add__(self(kwarg.children.__getitem__(0))).__add__(',')
        );
      } else {
        kwargs = kwargs.__add__(kwarg.children.__getitem__(0).__add__(','));
      }
      i = i.__add__(1);
    }
    if (kwargs) {
      args.append('{'.__add__(kwargs).__add__('}'));
    }
    result = result.__add__(
      self(ast.children.__getitem__(0))
        .__add__('(')
        .__add__(','.join(args))
        .__add__('){')
        .__add__(set_self)
    );
    while (i.__lt__(len(ast.children))) {
      result = result.__add__(
        self(ast.children.__getitem__(i)).__add__(';\\n')
      );
      i = i.__add__(1);
    }
    result = result.__add__('}');
    self['compiling_class'] = compiling_class;
    return result;
  }
  compile_for(ast) {
    const self = this;
    var iter = ast.children.__getitem__(0);
    var vartype = '';
    if (iter.meta.__contains__('vartype')) {
      vartype = iter.meta.__getitem__('vartype').__add__(' ');
    }
    return 'for('
      .__add__(vartype)
      .__add__(' ')
      .__add__(self(iter.children.__getitem__(0)))
      .__add__(' of ')
      .__add__(self(iter.children.__getitem__(1)))
      .__add__('){')
      .__add__(self(ast.children.__getitem__(1)))
      .__add__('}');
  }
  compile_generator(ast) {
    const self = this;
    var result = '(function*(){\\n';
    for (var child of ast.children.__getitem__(
      slice(1, undefined, undefined)
    )) {
      if ((child.type ?? Nil).__eq__('iter')) {
        result = result.__add__(
          'for(const '
            .__add__(self(child.children.__getitem__(0)))
            .__add__(' of ')
            .__add__(self(child.children.__getitem__(1)))
            .__add__(')\\n')
        );
      } else {
        result = result.__add__('if('.__add__(self(child)).__add__(')\\n'));
      }
    }
    result = result.__add__(
      'yield '.__add__(self(ast.children.__getitem__(0))).__add__(';\\n')
    );
    result = result.__add__('})()');
    return result;
  }
  compile_global(ast) {
    const self = this;
    return '';
  }
  compile_if(ast) {
    const self = this;
    var result = 'if('
      .__add__(self(ast.children.__getitem__(0)))
      .__add__('){')
      .__add__(self(ast.children.__getitem__(1)))
      .__add__('}');
    var i = 2;
    while (i.__lt__(len(ast.children).__sub__(1))) {
      result = result.__add__(
        'else if('
          .__add__(self(ast.children.__getitem__(i)))
          .__add__('){')
          .__add__(self(ast.children.__getitem__(i.__add__(1))))
          .__add__('}')
      );
      i = i.__add__(2);
    }
    if (i.__lt__(len(ast.children))) {
      result = result.__add__(
        'else{'.__add__(self(ast.children.__getitem__(i))).__add__('}')
      );
    }
    return result;
  }
  compile_ifelse(ast) {
    const self = this;
    return '('
      .__add__(self(ast.children.__getitem__(0)))
      .__add__(')?(')
      .__add__(self(ast.children.__getitem__(1)))
      .__add__('):(')
      .__add__(self(ast.children.__getitem__(2)))
      .__add__(')');
  }
  compile_import_as(ast) {
    const self = this;
    return 'import * as '
      .__add__(self(ast.children.__getitem__(1)))
      .__add__(' from "@/')
      .__add__(ast.children.__getitem__(0))
      .__add__('"');
  }
  compile_import_from(ast) {
    const self = this;
    return 'import {'
      .__add__(
        ', '.join(
          (function* () {
            for (const child of ast.children.__getitem__(
              slice(1, undefined, undefined)
            ))
              yield self(child);
          })()
        )
      )
      .__add__('} from "@/')
      .__add__(ast.children.__getitem__(0))
      .__add__('"');
  }
  compile_kwargs(ast) {
    const self = this;
    var children = [];
    var i = 0;
    while (i.__lt__(len(ast.children))) {
      if (isinstance(ast.children.__getitem__(i), str)) {
        children.append(
          self(ast.children.__getitem__(i))
            .__add__(':')
            .__add__(self(ast.children.__getitem__(i.__add__(1))))
        );
        i = i.__add__(2);
      } else {
        print(pp(ast), i);
        assert((ast.children.__getitem__(i).type ?? Nil).__eq__('splat'));
        children.append(self(ast.children.__getitem__(i)));
        i = i.__add__(1);
      }
    }
    return '{_kwargs:true,'.__add__(', '.join(children)).__add__('}');
  }
  compile_method_call(ast) {
    const self = this;
    var method = ast.type.__getitem__(slice(1, undefined, undefined));
    return '('
      .__add__(self(ast.children.__getitem__(0)))
      .__add__(').')
      .__add__(method)
      .__add__('(')
      .__add__(
        ', '.join(
          (function* () {
            for (const child of ast.children.__getitem__(
              slice(1, undefined, undefined)
            ))
              yield self(child);
          })()
        )
      )
      .__add__(')');
  }
  compile_name(ast) {
    const self = this;
    assert((len(ast.children) ?? Nil).__eq__(1));
    if (name_map.__contains__(ast.children.__getitem__(0))) {
      return name_map.__getitem__(ast.children.__getitem__(0));
    }
    return ast.children.__getitem__(0);
  }
  compile_nonlocal(ast) {
    const self = this;
    return '';
  }
  compile_num(ast) {
    const self = this;
    assert((len(ast.children) ?? Nil).__eq__(1));
    return str(ast.children.__getitem__(0));
  }
  compile_or(ast) {
    const self = this;
    return '('
      .__add__(self(ast.children.__getitem__(0)))
      .__add__(')||(')
      .__add__(self(ast.children.__getitem__(1)))
      .__add__(')');
  }
  compile_return(ast) {
    const self = this;
    return 'return ('.__add__(self(ast.children.__getitem__(0))).__add__(')');
  }
  compile_set(ast) {
    const self = this;
    var vartype = '';
    if (ast.meta.__contains__('vartype')) {
      vartype = ast.meta.__getitem__('vartype').__add__(' ');
    }
    return vartype
      .__add__(self(ast.children.__getitem__(0)))
      .__add__(' = ')
      .__add__(self(ast.children.__getitem__(1)));
  }
  compile_splat(ast) {
    const self = this;
    assert((len(ast.children) ?? Nil).__eq__(1));
    return '...'.__add__(self(ast.children.__getitem__(0)));
  }
  compile_try(ast) {
    const self = this;
    var body = [];
    var excepts = [];
    var finallyBody = [];
    for (var child of ast.children) {
      if ((child.type ?? Nil).__eq__('except')) {
        excepts.append(child);
      } else if ((child.type ?? Nil).__eq__('finally')) {
        finallyBody = child;
      } else {
        body.append(child);
      }
    }
    var result = 'try{'.__add__(';\\n'.join(map(self, body))).__add__('}');
    if (len(excepts).__gt__(0)) {
      var name = self(excepts.__getitem__(0).children.__getitem__(1));
      result = result.__add__('catch('.__add__(name).__add__('){'));
      for (var e of excepts) {
        result = result.__add__(
          'if('
            .__add__(name)
            .__add__(' instanceof ')
            .__add__(self(e.children.__getitem__(0)))
            .__add__('){')
        );
      }
      result = result
        .__getitem__(slice(undefined, (6).__neg__(), undefined))
        .__add__('}');
    }
    if (finallyBody) {
      result = result.__add__(
        'finally{'
          .__add__(';\\n'.join(map(self, finallyBody.children)))
          .__add__('}')
      );
    }
    return result;
  }
  compile_while(ast) {
    const self = this;
    return 'while('
      .__add__(self(ast.children.__getitem__(0)))
      .__add__('){')
      .__add__(
        ';\\n'.join(
          map(self, ast.children.__getitem__(slice(1, undefined, undefined)))
        )
      )
      .__add__('}');
  }
  method___call__(ast) {
    const self = this;
    var prefix = '(';
    if (
      (ast.children.__getitem__(0).type ?? Nil).__eq__('name') &&
      ast.children
        .__getitem__(0)
        .children.__getitem__(0)
        .__getitem__(0)
        .isupper()
    ) {
      prefix = 'new (';
    }
    return prefix
      .__add__(self(ast.children.__getitem__(0)))
      .__add__(')(')
      .__add__(
        ', '.join(
          (function* () {
            for (const child of ast.children.__getitem__(
              slice(1, undefined, undefined)
            ))
              yield self(child);
          })()
        )
      )
      .__add__(')');
  }
  method___dict(ast) {
    const self = this;
    return '__dict('
      .__add__(
        ', '.join(
          list(
            (function* () {
              for (const child of ast.children) yield self(child);
            })()
          )
        )
      )
      .__add__(')');
  }
  method___eq__(ast) {
    const self = this;
    return '('
      .__add__(self(ast.children.__getitem__(0)))
      .__add__('??Nil).__eq__(')
      .__add__(self(ast.children.__getitem__(1)))
      .__add__(')');
  }
  method___fstr(ast) {
    const self = this;
    return '+'.join(
      list(
        (function* () {
          for (const child of ast.children) yield self(child);
        })()
      )
    );
  }
  method___is(ast) {
    const self = this;
    return '('
      .__add__(self(ast.children.__getitem__(0)))
      .__add__(') === (')
      .__add__(self(ast.children.__getitem__(1)))
      .__add__(')');
  }
  method___isnot(ast) {
    const self = this;
    return '('
      .__add__(self(ast.children.__getitem__(0)))
      .__add__(') !== (')
      .__add__(self(ast.children.__getitem__(1)))
      .__add__(')');
  }
  method___getattr__(ast) {
    const self = this;
    if (legal_method_name(ast.children.__getitem__(1))) {
      return '('
        .__add__(self(ast.children.__getitem__(0)))
        .__add__(').')
        .__add__(ast.children.__getitem__(1));
    } else {
      return self.compile_method_call(ast);
    }
  }
  method___list(ast) {
    const self = this;
    return '['
      .__add__(
        ', '.join(
          list(
            (function* () {
              for (const child of ast.children) yield self(child);
            })()
          )
        )
      )
      .__add__(']');
  }
  method___ne__(ast) {
    const self = this;
    return '('
      .__add__(self(ast.children.__getitem__(0)))
      .__add__('??Nil).__ne__(')
      .__add__(self(ast.children.__getitem__(1)))
      .__add__(')');
  }
  method___setattr__(ast) {
    const self = this;
    return '('
      .__add__(self(ast.children.__getitem__(0)))
      .__add__(')[')
      .__add__(self(ast.children.__getitem__(1)))
      .__add__('] = ')
      .__add__(self(ast.children.__getitem__(2)));
  }
  method___tuple(ast) {
    const self = this;
    return '['
      .__add__(
        ', '.join(
          list(
            (function* () {
              for (const child of ast.children) yield self(child);
            })()
          )
        )
      )
      .__add__(']');
  }
  __call__(ast) {
    const self = this;
    if (isinstance(ast, str)) {
      return json.dumps(ast);
    }
    var type = ast.type;
    if ((type.__getitem__(0) ?? Nil).__eq__('.')) {
      var handler = getattr(
        self,
        'method_'.__add__(type.__getitem__(slice(1, undefined, undefined))),
        undefined
      );
      if (handler.__not__()) {
        handler = getattr(self, 'compile_method_call', undefined);
      }
    } else {
      handler = getattr(self, 'compile_'.__add__(type), undefined);
    }
    if (handler) {
      return handler(ast);
    } else {
      print(pp(ast));
      var error = 'No compile-handler for ' + type;
      raise(new CompileError(error));
    }
  }
}
function compile(ast) {
  return new Compiler()(ast);
}
function compile_module(ast) {
  return "import * as runtime from '@/mupyjs/runtime.js';Object.assign(self, runtime);\\n".__add__(
    compile(ast)
  );
}
