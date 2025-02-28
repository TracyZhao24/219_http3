1. Start docker container
```
docker pull klee/klee:3.0
docker run -v $(pwd)/test_cases:/home/klee --rm -ti --ulimit='stack=-1:-1' klee/klee:3.0
```

2. Compile: ```clang -I ../../include -emit-llvm -c -g -O0 -Xclang -disable-O0-optnone --path_to_c_file```

3. Run ```klee --libc=uclibc --path_to_bc_file```. 
The option is needed to make Klee recognize calls to the C library.

4. To see the outputs, run ```ktest-tool klee-last/test######.ktest```


