from mupyjs.AST import pp, parse_pp
from mupyjs.parser import parse
import sys
import re

if __name__ == "__main__":
    
    doc = open("README.md", "r").read()
    doc = doc.split('```')
    tests = [];
    for i in range(0, len(doc) - 6):
        if (re.match(r'python *\n', doc[i+1]) and 
            re.match(r'AST *\n', doc[i+3]) and 
            re.match(r'js *\n', doc[i+5])):
            tests.append([doc[i]] + [re.sub(r'^[^\n]*\n', '', src) for src in [doc[i+1], doc[i+3], doc[i+5]]])
    if len(sys.argv) > 1:
        tests = [test for test in tests if sys.argv[1] in test[0]]


    print(f"Running {len(tests)} tests")
    correct = 0
    for i in range(0, len(tests)):
        [_, py_src, ast_src, js_src] = tests[i]
        py_ppast = pp(parse(py_src))
        ast_ppast = pp(parse_pp(ast_src))
        if py_ppast != ast_ppast:
            print(f"Test failed:")
            print(py_src)
            print(py_ppast)
            print(ast_ppast)
        else:
            correct += 1
    print(f"Passed {correct}/{len(tests)} tests")