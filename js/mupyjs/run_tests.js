import * as runtime from '@/mupyjs/runtime.js';
Object.assign(self, runtime);
import * as glob from '@/glob';
import * as sys from '@/sys';
import { prettier } from '@/mupyjs/main';
import { pass1 } from '@/mupyjs/pass1';
import { parse } from '@/mupyjs/parser';
import { compile_import, compile } from '@/mupyjs/compiler';
import { pp } from '@/mupyjs/AST';
import { run_markdown_tests } from '@/mupyjs/main';
function write_file(name, src) {
  var file = open(name, 'w');
  file.write(src);
  file.close();
}
function run_test(test_file) {
  var file = open(test_file, 'r');
  var src = file.read();
  file.close();
  var prefix = test_file.__getitem__(
    slice(undefined, (3).__neg__(), undefined)
  );
  var ast = parse(src);
  write_file(prefix.__add__('.ast0'), pp(ast));
  ast = pass1(ast);
  write_file(prefix.__add__('.ast1'), pp(ast));
  var js = compile_import(ast);
  write_file(prefix.__add__('.unformatted.js'), js);
  write_file(prefix.__add__('.js'), prettier(js));
}
if ((__name__ ?? Nil).__eq__('__main__')) {
  run_markdown_tests('README.md');
  var test_files = glob.glob('./tests/**/*.py', {
    _kwargs: true,
    recursive: true,
  });
  print(test_files);
  for (var test_file of test_files) {
    try {
      run_test(test_file);
    } catch (e) {
      if (e instanceof Exception) {
        print(e);
        print('Error running test ' + test_file + ': ' + e);
      }
    }
  }
}
