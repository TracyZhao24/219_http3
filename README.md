1. Start docker container
```
docker pull klee/klee:3.0
docker run -v $(pwd)/test_cases:/home/klee/test_cases --rm -ti --ulimit='stack=-1:-1' klee/klee:3.0
```
3. Compile: ```clang -I ../../include -emit-llvm -c -g -O0 -Xclang -disable-O0-optnone <path_to_c_file>```

4. Run ```--output-dir=/home/klee/test_cases/test1 --libc=uclibc <path_to_bc_file>```. 
The output directory needs to be a directory that Klee creates, it cannot already exist. The `libc` option lets Klee recognize C library calls.

5. To see the outputs, run ```ktest-tool [output-directory]/test######.ktest```


