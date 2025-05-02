import * as sys from '@/sys';
import * as requests from '@/requests';
import * as subprocess from '@/subprocess';
import * as atexit from '@/atexit';
function prettier(code) {
  var response = requests.post('http://localhost:9696/format', {
    _kwargs: true,
    data: code,
  });
  return response.text;
}
var popen = subprocess.Popen;
var prettier_process = popen(['node', 'src/mupyjs/prettier_server.js']);
function cleanup_prettier_process() {
  if (prettier_process) {
    prettier_process.terminate();
    prettier_process = undefined;
  }
}
atexit.register(cleanup_prettier_process);
var original_excepthook = sys.excepthook;
function exception_handler(exctype, value, traceback) {
  cleanup_prettier_process();
  original_excepthook(exctype, value, traceback);
}
sys['excepthook'] = exception_handler;
