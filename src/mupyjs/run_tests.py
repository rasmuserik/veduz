import glob
import sys
from mupyjs.main import prettier
from mupyjs.pass1 import pass1
from mupyjs.parser import parse
from mupyjs.compiler import compile
from mupyjs.AST import pp
from mupyjs.main import run_markdown_tests

def write_file(name, src):
    file = open(name, 'w')
    file.write(src)
    file.close()

def run_test(test_file):
    file = open(test_file, 'r')
    src = file.read()
    file.close()

    prefix = test_file[:-3]
    ast = parse(src)
    write_file(prefix + '.ast0', pp(ast))
    ast = pass1(ast)
    write_file(prefix + '.ast1', pp(ast))
    js = compile(ast)
    write_file(prefix + '.unformatted.js', js)
    write_file(prefix + '.js', prettier(js))

if __name__ == "__main__":
    run_markdown_tests("README.md")
    test_files = glob.glob('./tests/**/*.py', recursive=True)
    #test_files = reversed(test_files)
    print(test_files)
    for test_file in test_files:
        try:
            run_test(test_file)
        except Exception as e:
            print(e);
            print(f"Error running test {test_file}: {e}")
