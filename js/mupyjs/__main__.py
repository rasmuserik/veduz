import glob
import shutil
import os
from watchfiles import watch
from mupyjs.prettier import prettier
from mupyjs.compiler import compile_module
from mupyjs.parser import parse
from mupyjs.AST import pp
from mupyjs.pass1 import pass1

def jsfile(fname):
    if fname.endswith(".py"):
        fname = fname[:-3] + ".js"
    fname = fname.replace("src/", "js/")
    os.makedirs(os.path.dirname(fname), exist_ok=True)
    return fname

def compile_py_to_js(pyfile):
    with open(pyfile, "r") as f:
        code = f.read()
    dest = jsfile(pyfile)
    shutil.copyfile(pyfile, dest[:-3] + ".py")
    try:
        ast = (parse(code))
        with open(dest[:-3] + ".ast0", "w") as f:
            f.write(pp(ast))
        ast = pass1(ast)
        with open(dest[:-3] + ".ast1", "w") as f:
            f.write(pp(ast))
        jscode = compile_module(ast)
        with open(dest[:-3] + ".unformatted.js", "w") as f:
            f.write(jscode)
        formatted = prettier(jscode)
        with open(dest, "w") as f:
            f.write(formatted)
    except Exception as e:
        print(f"error compiling {pyfile}: {e}")
        return 


def syncfile(fname):
    print(f"syncing {fname}")
    target_fname = jsfile(fname)
    if fname.endswith(".py"):
        compile_py_to_js(fname)
    else:
        shutil.copyfile(fname, target_fname)

jsfiles = glob.glob("src/**/*.js")
pyfiles = {f[:-3] for f in glob.glob("src/**/*.py")} 
pyfiles -= {f[:-3] for f in jsfiles}
pyfiles = [f + ".py" for f in pyfiles]
files = pyfiles + jsfiles + glob.glob("src/*.html")
files = [os.path.abspath(f) for f in files]


for f in files:
    syncfile(f)

for changes in watch("src", recursive=True):
    for change_type, path in changes:
        print(f"change: {change_type} {path}")
        if str(path) in files:
            syncfile(path)