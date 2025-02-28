1. Start docker container
```
docker pull klee/klee:3.0
docker run --rm -ti --ulimit='stack=-1:-1' klee/klee:3.0
```

2. Copy c file into container

3. Compile: ```clang -I ../../include -emit-llvm -c -g -O0 -Xclang -disable-O0-optnone```

4. run ```klee --libc=uclibc --path_to_bc_file```
the option is needed to make Klee recognize calls to the C library.

5. To see the outputs, run ```ktest-tool klee-last/test######.ktest```
