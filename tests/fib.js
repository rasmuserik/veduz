import { print } from './runtime.js';
function fib1(n) {
  if (n.__le__(1)) {
    return n;
  }
  return fib1(n.__sub__(1)).__add__(fib1(n.__sub__(2)));
}

function fib2(n) {
  if(n <= 1) return n;
  return fib2(n - 1) + fib2(n - 2);
}

print(fib1(40));
