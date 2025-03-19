# Generate Test Cases

1. Start Klee docker container
```
docker pull klee/klee:3.0
docker run -v $(pwd)/test_cases:/home/klee/test_cases --rm -ti --ulimit='stack=-1:-1' klee/klee:3.0
```
3. Compile: ```clang -I ../../include -emit-llvm -c -g -O0 -Xclang -disable-O0-optnone <path_to_c_file>```

4. Run ```--output-dir=/home/klee/test_cases/test1 --libc=uclibc <path_to_bc_file>```. 
The output directory needs to be a directory that Klee creates, it cannot already exist. The `libc` option lets Klee recognize C library calls.

5. To see the outputs, run ```ktest-tool [output-directory]/test######.ktest```

# Formatting the Test Cases
We wrote a python script to scrape the `ktest-tool` outputs into a json file. To run it, you have to be in the klee container. 

# Differential Testing

## Running the Script


## Making a Dockerfile for one HTTP Implementation: [nginx](https://hub.docker.com/_/nginx) Docker image

1. Create a Dockerfile in the directory of your local testing filesystem. If you can an official image maintained on Docker Hub, you can get by with this: 
```
FROM {official package}
COPY model_fs {package-specific-location for serving static files}
```
For NGINX this is `/usr/share/nginx/html`.

2. In the directory diff_testing, run these commands to build, start your container, and expose the external port.
```
docker build -t {tag} -f {image.dockerfile} .
docker run --name {container-name} -d -p 8080:80 {tag}
```

3. Then you can hit http://localhost:8080 or http://host-ip:8080 in your browser.


