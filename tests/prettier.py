import sys
import requests
import subprocess
import atexit

def prettier(code):
    response = requests.post('http://localhost:9696/format', data=code)
    return response.text

prettier_process = subprocess.Popen(['node', 'src/mupyjs/prettier_server.js'])

def cleanup_prettier_process():
    global prettier_process
    if prettier_process:
        prettier_process.terminate()
        prettier_process = None

atexit.register(cleanup_prettier_process)
original_excepthook = sys.excepthook
def exception_handler(exctype, value, traceback):
    cleanup_prettier_process()
    original_excepthook(exctype, value, traceback)
sys.excepthook = exception_handler
