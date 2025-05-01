from mupyjs.AST import pp, parse_pp
from mupyjs.parser import parse, ParseError
from mupyjs.compiler import Compiler, CompileError
import sys
import re
import requests
import subprocess
import time

def format_with_prettier(code):
    response = requests.post('http://localhost:9696/format', data=code)
    return response.text

def extract_tests_from_readme(readme_path="README.md"):
    with open(readme_path, "r") as f:
        doc = f.read()
    
    doc_sections = doc.split('```')
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
    
    return tests

def run_test(test, test_number):
    try:
        ast = parse(test[1])
        py_ppast = pp(ast)
        ast_ppast = pp(parse_pp(test[2]))
        compiled_js = Compiler()(ast)
        
        expected_js_formatted = format_with_prettier(test[3])
        compiled_js_formatted = format_with_prettier(compiled_js)
        
        if py_ppast != ast_ppast:
            return False, f"TEST {test_number} AST fail:\n{test[1]}\nEXPECTED:\n{ast_ppast}\nGOT:\n{py_ppast}"
            
        if expected_js_formatted != compiled_js_formatted:
            return False, f"TEST {test_number} Compile fail:\n{test[1]}\nAST:\n{py_ppast}\n\nEXPECTED:\n{expected_js_formatted}\nGOT:\n{compiled_js_formatted}"
            
        return True, f"=>\n\n{compiled_js_formatted}\nTEST {test_number} Passed\n--------------------------------"
        
    except ParseError as e:
        return False, f"ParseError: {e}"
    except CompileError as e:
        return False, f"CompileError: {e}"

def main():
    prettier_server = subprocess.Popen(['node', 'src/mupyjs/prettier_server.js'])
    time.sleep(0.1)
    
    try:
        tests = extract_tests_from_readme()
        if len(sys.argv) > 1:
            tests = [test for test in tests if sys.argv[1] in test[0]]
        
        print(f"Running {len(tests)} tests from README.md\n--------------------------------")
        
        correct = 0
        for i, test in enumerate(tests, 1):
            print(f"TEST {i} running\n{test[1]}")
            success, result = run_test(test, i)
            if not success:
                print(result)
                break
            print(result)
            correct += 1
        
        print(f"TESTS PASSED: {correct}/{len(tests)}")
    finally:
        prettier_server.terminate()
        prettier_server.wait()

if __name__ == "__main__":
    main()