import glob
from mupyjs.main import prettier
from mupyjs.pass1 import pass1
from mupyjs.parser import parse
from mupyjs.compiler import compile
from mupyjs.AST import pp

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
    js = prettier(compile(ast))
    write_file(prefix + '.js', js)

if __name__ == "__main__":
    test_files = glob.glob('./tests/**/*.py', recursive=True)
    print(test_files)
    for test_file in test_files:
        try:
            run_test(test_file)
        except Exception as e:
            print(f"Error running test {test_file}: {e}")
