class AST {
  constructor(type, ...children) {
    const self = this;
    self.__setattr__('type', type);
    if (children && isinstance(children.__getitem__(0), dict)) {
      self.__setattr__(
        'children',
        children.__getitem__(slice(1, undefined, undefined))
      );
    } else {
      self.__setattr__('children', children);
    }
  }
}
