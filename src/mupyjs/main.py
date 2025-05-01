from mupyjs.pass1 import pass1
from mupyjs.AST import pp, parse_pp
from mupyjs.parser import parse, ParseError
from mupyjs.compiler import CompileError, compile
import re
import requests
import subprocess
import time
import sys

def prettier(code):
    response = requests.post('http://localhost:9696/format', data=code)
    return response.text

def run_markdown_tests(fname):
    doc_sections = open(fname, "r").read().split('```')
    tests = []
    for i in range(0, len(doc_sections) - 6):
        if (re.match(r'python *\n', doc_sections[i+1]) and 
            re.match(r'AST *\n', doc_sections[i+3]) and 
            re.match(r'js *\n', doc_sections[i+5])):
            tests.append([
                doc_sections[i],
                re.sub(r'^[^\n]*\n', '', doc_sections[i+1]),
                re.sub(r'^[^\n]*\n', '', doc_sections[i+3]),
                re.sub(r'^[^\n]*\n', '', doc_sections[i+5])
            ])
    print(f"Running {len(tests)} tests from README.md\n--------------------------------")
    correct = 0
    for i, test in enumerate(tests, 1):
        print(f"TEST {i} running")
        try:
            ast = parse(test[1])
            ast = pass1(ast)
            print(test[1],"\n--------------------------------")
            py_ppast = pp(ast)
            print(py_ppast,"\n--------------------------------")
            ast_ppast = pp(parse_pp(test[2]))
            compiled_js = compile(ast)
            expected_js_formatted = prettier(test[3])
            print(ast_ppast,"\n--------------------------------")
            compiled_js_formatted = prettier(compiled_js)
            if py_ppast != ast_ppast:
                return print(f"TEST {i} AST fail:\n{test[1]}\nEXPECTED:\n{ast_ppast}\nGOT:\n{py_ppast}")
            if expected_js_formatted != compiled_js_formatted:
                return print(f"TEST {i} Compile fail:\n{test[1]}\nAST:\n{py_ppast}\n\nEXPECTED:\n{expected_js_formatted}\nGOT:\n{compiled_js_formatted}")
            print(f"=>\n\n{compiled_js_formatted}\nTEST {i} Passed\n--------------------------------")
            correct += 1
        except ParseError as e:
            return print(f"ParseError: {e}")
        except CompileError as e:
            return print(f"CompileError: {e}")
    print(f"TESTS PASSED: {correct}/{len(tests)}")

def main():
    prettier_server = subprocess.Popen(['node', 'src/mupyjs/prettier_server.js'])
    time.sleep(0.1)
    filename = sys.argv[1] if len(sys.argv) > 1 else "README.md"

    try:
        if filename.endswith('.md'):
            run_markdown_tests(filename)
        if filename.endswith('.py'):
            src = open(filename, 'r').read()
            ast = parse(src)
            ast = pass1(ast)
            print(src,"\n--------------------------------")
            print(pp(ast),"\n--------------------------------")
            print(prettier(compile(ast)))
    except (ParseError, CompileError) as e:
        sys.exit(f"{type(e).__name__}: {e}")
    finally:
        prettier_server.terminate()

if __name__ == "__main__":
    main()