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
