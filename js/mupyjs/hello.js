import * as runtime from '@/mupyjs/runtime.js';
Object.assign(self, runtime);
print('Hello, world!');
document.body['innerHTML'] = list(
  (function* () {
    for (const i of range(10)) yield 'hello '.__add__(i);
  })()
);
