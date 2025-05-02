import * as runtime from '@/mupyjs/runtime.js';
Object.assign(self, runtime);
import * as re from '@/re';
function legal_method_name(name) {
  return (
    isinstance(name, str) &&
    re.match('"^[a-zA-Z_][a-zA-Z0-9_]*$', name) !== undefined
  );
}
