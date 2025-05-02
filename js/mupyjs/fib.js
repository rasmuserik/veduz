import * as runtime from '@/mupyjs/runtime.js';
Object.assign(self, runtime);
function fib(n) {
  if (n.__le__(1)) {
    return n;
  }
  return fib(n.__sub__(1)).__add__(fib(n.__sub__(2)));
}
print(fib(32));
