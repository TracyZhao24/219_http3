1. Start docker container
```
docker pull klee/klee:3.0
<!-- docker run -v $(pwd)/test_cases:/home/klee --rm -ti --ulimit='stack=-1:-1' klee/klee:3.0 -->
docker run --rm -ti --ulimit='stack=-1:-1' klee/klee:3.0
```

2. Transfer files from local file system to to the container (in separate terminal)
```docker cp <LOCAL_PATH of the C file> <CONTAINER_NAME>:/home/klee/```

3. Compile: ```clang -I ../../include -emit-llvm -c -g -O0 -Xclang -disable-O0-optnone <path_to_c_file>```

4. Run ```klee --libc=uclibc <path_to_bc_file>```. 
The option is needed to make Klee recognize calls to the C library.

5. To see the outputs, run ```ktest-tool klee-last/test######.ktest```


