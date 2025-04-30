from mupyjs.AST import pp
from mupyjs.parser import parse

if __name__ == "__main__":
    src = open("./src/mupyjs/example.py", "r").read()
    print(pp(parse(src)))
