Error formatting code: Invalid left-hand side in assignment expression. (24:51)
[0m [90m 22 |[39m }handle_iter(ast){[36mconst[39m self [33m=[39m [36mthis[39m[33m;[39m
 [90m 23 |[39m [36mif[39m(((((ast)[33m.[39mchildren)[33m.[39m__getitem__([35m0[39m))[33m.[39mtype[33m?[39m[33m?[39m[33mNil[39m)[33m.[39m__eq__([32m"name"[39m)){[36mvar[39m name [33m=[39m ((((ast)[33m.[39mchildren)[33m.[39m__getitem__([35m0[39m))[33m.[39mchildren)[33m.[39m__getitem__([35m0[39m)[33m;[39m
[31m[1m>[22m[39m[90m 24 |[39m [36mif[39m((((self)[33m.[39mscope)[33m.[39m__contains__(name))[33m.[39m__not__()){((ast)[33m.[39mmeta)[33m.[39m__getitem__([32m"vartype"[39m) [33m=[39m [32m"var"[39m[33m;[39m
 [90m    |[39m                                                   [31m[1m^[22m[39m
 [90m 25 |[39m ((self)[33m.[39mscope)[33m.[39m__getitem__(name) [33m=[39m __dict([32m"vartype"[39m[33m,[39m [32m"var"[39m)}}[33m;[39m
 [90m 26 |[39m [36mreturn[39m ([36mnew[39m ([33mAST[39m)((ast)[33m.[39mtype[33m,[39m (ast)[33m.[39mmeta[33m,[39m [33m...[39m(map)(self[33m,[39m (ast)[33m.[39mchildren)))[33m;[39m
 [90m 27 |[39m }handle_nonlocal(ast){[36mconst[39m self [33m=[39m [36mthis[39m[33m;[39m[0m