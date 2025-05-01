from mupyjs.AST import pp, parse_pp
from mupyjs.parser import parse, ParseError
from mupyjs.compiler import Compiler, CompileError
import re
import requests
import subprocess
import time

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
        print(f"TEST {i} running\n{test[1]}")
        try:
            ast = parse(test[1])
            py_ppast = pp(ast)
            ast_ppast = pp(parse_pp(test[2]))
            compiled_js = Compiler()(ast)
            expected_js_formatted = prettier(test[3])
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
    
    try:
        run_markdown_tests("README.md")
    finally:
        prettier_server.terminate()
        prettier_server.wait()

if __name__ == "__main__":
    main()