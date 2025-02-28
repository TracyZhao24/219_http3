ls
vim trash.txt
exit
docker pull klee/klee:3.0
exit
vim trash2.txt
ls
clear
exit
ls
rm trash.txt
rm trash2.txt
clear
exit
ls
clang -I ../../include -emit-llvm -c -g -O0 -Xclang -disable-O0-optnone
clang -I ../../include -emit-llvm -c -g -O0 -Xclang -disable-O0-optnone fixed_base.c
klee --libc=uclibc fixed_base.bc
ls
which klee
ls
cd ..
ls
cd ..
ls
which klee
docker inspect <container_id> | grep Mounts -A 5
exit
