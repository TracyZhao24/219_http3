# Generate Test Cases

1. Start Klee docker container
```
docker pull klee/klee:3.0
docker run -v $(pwd)/test_cases:/home/klee/test_cases --rm -ti --ulimit='stack=-1:-1' klee/klee:3.0
```
3. Compile: ```clang -I ../../include -emit-llvm -c -g -O0 -Xclang -disable-O0-optnone <path_to_c_file>```

4. Run ```klee --output-dir=/home/klee/test_cases/test1 --libc=uclibc <path_to_bc_file>```. 
The output directory needs to be a directory that Klee creates, it cannot already exist. The `libc` option lets Klee recognize C library calls.

5. To see the outputs, run ```ktest-tool [output-directory]/test######.ktest```


# Differential Testing

## Example: [nginx](https://hub.docker.com/_/nginx) Docker image
1. Create a Dockerfile in the directory of your local testing filesystem. 
```
FROM nginx
COPY . /usr/share/nginx/html
```

2. Run these commands to build, start your container, and expose the external port.
```
docker build -t some-content-nginx .
docker run --name some-nginx -d -p 8080:80 some-content-nginx
```

3. Then you can hit http://localhost:8080 or http://host-ip:8080 in your browser.


