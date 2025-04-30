class AST:
    def __init__(self, type, *children):
        self.type = type
        if children and isinstance(children[0], dict):
            self.annotations = children[0]
            self.children = children[1:]
        else:
            self.annotations = {}
            self.children = children
