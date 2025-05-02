import * as runtime from '@/mupyjs/runtime.js';
Object.assign(self, runtime);
import * as json from '@/json';
import * as re from '@/re';
class AST {
  constructor(type, ...children) {
    const self = this;
    self['type'] = type;
    if (len(children).__gt__(0) && isinstance(children.__getitem__(0), dict)) {
      self['meta'] = children.__getitem__(0);
      self['children'] = children.__getitem__(slice(1, undefined, undefined));
    } else {
      self['meta'] = __dict();
      self['children'] = children;
    }
  }
}
function ast_to_pplist(ast) {
  if (isinstance(ast, str)) {
    return json.dumps(ast);
  }
  if ((ast.type ?? Nil).__eq__('name')) {
    return ast.children.__getitem__(0);
  }
  if ((ast.type ?? Nil).__eq__('num')) {
    return ast.children.__getitem__(0);
  }
  return ['(', ast.type, ...map(ast_to_pplist, ast.children), ')'];
}
function ppline(pplist, maxlen) {
  if (isinstance(pplist, str)) {
    return pplist;
  }
  var result = pplist.__getitem__(0);
  for (var child of pplist.__getitem__(slice(1, (1).__neg__(), undefined))) {
    result = result
      .__add__(ppline(child, maxlen.__sub__(len(result))))
      .__add__(' ');
  }
  result = result
    .__getitem__(slice(0, (1).__neg__(), undefined))
    .__add__(pplist.__getitem__((1).__neg__()));
  if (len(result).__gt__(maxlen)) {
    raise(new Exception('Line too long'));
  }
  return result;
}
var maxlen = 80;
function pp_pplist(pplist, indent) {
  try {
    return ppline(pplist, maxlen.__sub__(len(indent)));
  } catch (e) {
    if (e instanceof Exception) {
      var result = pplist
        .__getitem__(0)
        .__add__(pplist.__getitem__(1))
        .__add__('\\n')
        .__add__(indent);
      for (var child of pplist.__getitem__(
        slice(2, (2).__neg__(), undefined)
      )) {
        result = result
          .__add__(pp_pplist(child, indent.__add__('  ')))
          .__add__('\\n')
          .__add__(indent);
      }
      result = result
        .__add__(
          pp_pplist(pplist.__getitem__((2).__neg__()), indent.__add__('  '))
        )
        .__add__(pplist.__getitem__((1).__neg__()));
      return result;
    }
  }
}
function pp(ast) {
  return pp_pplist(ast_to_pplist(ast));
}
function _parse_pp(str) {
  var str = str.strip();
  if ((str.__getitem__(0) ?? Nil).__eq__('"')) {
    var i = 1;
    while (true) {
      if ((str.__getitem__(i) ?? Nil).__eq__('"')) {
        return [
          str.__getitem__(slice(1, i, undefined)),
          str.__getitem__(slice(i.__add__(1), undefined, undefined)),
        ];
      }
      if ((str.__getitem__(i) ?? Nil).__eq__('\\\\')) {
        i = i.__add__(1);
      }
      i = i.__add__(1);
    }
  } else if ((str.__getitem__(0) ?? Nil).__eq__('(')) {
    str = str.__getitem__(slice(1, undefined, undefined)).strip();
    var result = [];
    while (str && (str.__getitem__(0) ?? Nil).__ne__(')')) {
      [first, rest] = _parse_pp(str);
      result.append(first);
      str = rest;
    }
    return [
      new AST(
        result.__getitem__(0).children.__getitem__(0),
        ...result.__getitem__(slice(1, undefined, undefined))
      ),
      str.__getitem__(slice(1, undefined, undefined)),
    ];
  } else {
    result = '';
    while (
      str &&
      str.__getitem__(0).isspace().__not__() &&
      (str.__getitem__(0) ?? Nil).__ne__('(') &&
      (str.__getitem__(0) ?? Nil).__ne__(')')
    ) {
      result = result.__add__(str.__getitem__(0));
      str = str.__getitem__(slice(1, undefined, undefined));
    }
    if (re.match('"^\\d+[.]?\\d*$', result)) {
      return [new AST('num', result), str];
    } else {
      return [new AST('name', result), str];
    }
  }
}
function parse_pp(str) {
  var result = [];
  while (str.strip()) {
    [first, rest] = _parse_pp(str);
    result.append(first);
    var str = rest;
  }
  return new AST('do', ...result);
}
