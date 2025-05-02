import { print } from './runtime.js';
class AST {
  constructor(type, ...children) {
    const self = this;
    self['type'] = type;
    if (children && isinstance(children.__getitem__(0), dict)) {
      self['annotations'] = children.__getitem__(0);
      self['children'] = children.__getitem__(slice(1, undefined, undefined));
    } else {
      self['annotations'] = __dict();
      self['children'] = children;
    }
  }
}
function fib(n) {
  if (n.__le__(1)) {
    return n;
  }
  return fib(n.__sub__(1)).__add__(fib(n.__sub__(2)));
}
print(fib(32));
