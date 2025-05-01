from mupyjs.AST import pp, parse_pp
from mupyjs.parser import parse, ParseError
from mupyjs.compiler import Compiler, CompileError
import sys
import re
import requests

def prettier(src):
    response = requests.post('http://localhost:9696/format', data=src)
    return response.text

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


    print(f"Running {len(tests)} tests from README.md\n--------------------------------")
    correct = 0
    for i in range(1, len(tests) + 1):
        [_, py_src, ast_src, js_src] = tests[i - 1]
        js_prettier = prettier(js_src)
        print(f"TEST {i} running\n")
        print(py_src)
        try:
            ast = parse(py_src)
            py_ppast = pp(ast)
            ast_ppast = pp(parse_pp(ast_src))
            pyjs = Compiler()(ast)
            pyjs_prettier = prettier(pyjs)
        except ParseError as e:
            print(f"ParseError: {e}")
            break
        except CompileError as e:
            print(f"CompileError: {e}")
            break

        if py_ppast != ast_ppast:
            print(f"TEST {i} AST fail:")
            print(py_src)
            print("EXPECTED:\n" + ast_ppast)
            print("GOT:\n" + py_ppast)
            break
        elif js_prettier != pyjs_prettier:
            print(f"TEST {i} Compile fail:")
            print(py_src)
            print("AST:\n" + py_ppast)
            print("\nEXPECTED:\n" + js_prettier)
            print("GOT:\n" + pyjs_prettier)
            break
        else:
            print("=>\n\n" + pyjs_prettier)
            print(f"TEST {i} Passed\n--------------------------------")
            correct += 1
    print(f"TESTS PASSED: {correct}/{len(tests)}")