import httpx
import json
from concurrent.futures import ThreadPoolExecutor
import docker
import os
import argparse

DIFF_TESTING = "../diff_testing"
CONTAINER_PORT = 80

# Build docker image from dockerfile 
def build_image(dockerfile_path, tag):
    client = docker.from_env()
    print(f"Building image {tag} from {dockerfile_path}")
    image, logs = client.images.build(path=DIFF_TESTING, dockerfile=dockerfile_path, tag=tag)
    # for log in logs:
    #     print(log.get('stream', '').strip())
    return image


# Start each docker container
def start_container(name, image, port, client):
    container = client.containers.run(
        image.id,
        name=name,
        ports={f"{CONTAINER_PORT}/tcp": port},
        detach=True
    )
    print(f"Started container {name} on port {port}")
    return container


# Start all docker containers
def start_all_containers():
    client = docker.from_env()
    # Define  server configurations
    servers = [
        {"name": "nginx", "dockerfile": "../diff_testing/dockerfiles/nginx.dockerfile", "port": 8080},
        {"name": "apache", "dockerfile": "../diff_testing/dockerfiles/httpd.dockerfile", "port": 8081},
        {"name": "caddy", "dockerfile": "../diff_testing/dockerfiles/caddy.dockerfile", "port": 8082},
        {"name": "h2o", "dockerfile": "../diff_testing/dockerfiles/h2o.dockerfile", "port": 8083},
        {"name": "lighttpd", "dockerfile": "../diff_testing/dockerfiles/lighttpd.dockerfile", "port": 8084}
    ]

    containers = []
    for server in servers:
        # Build the image from the Dockerfile
        image = build_image(server["dockerfile"], server["name"])
        container = start_container(server["name"], image, server["port"], client)
        containers.append(container)

    return containers


# Stop and remove all docker containers
def stop_and_remove_containers(containers):
    for container in containers:
        container.stop()
        container.remove()
        print(f"Stopped and removed container {container.name}")


# Send HTTP GET request for each URI
def send_http1_get_requests(baseURL, file_paths, base_log_file):
    test_cases = []

    for file_path in file_paths:
        with open(file_path, 'r', encoding="utf-8") as file:
            test_cases.extend(json.load(file))
        
    # Create a HTTP client session
    with httpx.Client(base_url=baseURL, http1=True) as client:
        for i, obj in enumerate(test_cases):
            # Build the full path + query (ignore fragment)
            full_path = obj["path"]
            authority = obj["authority"]
            if obj["query"]:
                full_path += "?" + obj["query"]
            uri = f"{obj['scheme']}://{obj['authority']}{full_path}"

            log_file = base_log_file + f"{i}.json"
            with open(log_file, 'w', encoding="utf-8") as log:
                log.write(f"Test case {i}: {uri}\n")

                try:
                    # Send the GET request
                    response = client.get(
                        baseURL + full_path,
                        headers={"Host": authority}
                    )
                    resolved_uri = response.url

                    # Raises HTTPStatusError for 4xx/5xx responses
                    response.raise_for_status() 

                    # Log the successful response content
                    # TODO handle if response is a directory instead of a file
                    log.write(f"Request to {uri} completed with status code: {response.status_code}\n")
                    log.write(f"Resolved URI: {resolved_uri}\n")
                    # Limit dump to first 200 chars
                    log.write(f"Response content from {uri}: {response.text[:200]}\n\n")  

                except httpx.RequestError as e:
                    # General request error (e.g., connection issues)
                    # resolved_uri = e.response.url
                    log.write(f"Request to {uri} failed: {str(e)}\n\n")
                    # log.write(f"Resolved URL: {resolved_uri}\n\n")

                except httpx.TimeoutException as e:
                    # Timeout error (e.g., server took too long to respond)
                    # resolved_uri = e.response.url
                    log.write(f"Request to {uri} timed out: {str(e)}\n\n")
                    # log.write(f"Resolved URL: {resolved_uri}\n\n")

                except httpx.HTTPStatusError as e:
                    # HTTP error (e.g., 404, 500, etc.)
                    resolved_uri = e.response.url
                    log.write(f"Request to {uri} returned error: {e.response.status_code}\n")
                    log.write(f"Resolved URL: {resolved_uri}\n\n")

                except httpx.TooManyRedirects as e:
                    # Too many redirects error
                    # resolved_uri = e.response.url
                    log.write(f"Request to {uri} failed due to too many redirects: {str(e)}\n\n")
                    # log.write(f"Resolved URL: {resolved_uri}\n\n")

                except Exception as e:
                    # Catch any other unexpected errors
                    log.write(f"An unexpected error occurred with {uri}: {str(e)}\n\n")


def test_server(baseURL, file_paths, log_file):
    send_http1_get_requests(baseURL, file_paths, log_file)


def __main__():
    # Parse command-line arguments
    parser = argparse.ArgumentParser(description="Run differential testing on HTTP servers.")
    parser.add_argument(
        '--test_files',
        nargs='+',
        required=True,
        help="List of test case file paths (e.g., ./diff_testing/fs_paths.json ./test_cases/clean_tests/test2.json)"
    )
    parser.add_argument(
        '--log_dir',
        required=True,
        help="Directory to write log files to (e.g., run_2, varied_fs_bases)"
    )
    args = parser.parse_args()

    containers = []
    try:
        print('Starting containers')
        containers = start_all_containers()

        # Define the different server implementations and their log files
        servers = [
            {"baseURL": "http://localhost:8080", "log_file": f"../diff_testing/nginx/{args.log_dir}/"},
            {"baseURL": "http://localhost:8081", "log_file": f"../diff_testing/apache/{args.log_dir}/"},
            {"baseURL": "http://localhost:8082", "log_file": f"../diff_testing/caddy/{args.log_dir}/"},
        ]

        for server in servers:
            # Ensure the log directory exists
            os.makedirs(server["log_file"], exist_ok=True)

        # Use ThreadPoolExecutor to run tests
        with ThreadPoolExecutor() as executor:
            futures = [executor.submit(test_server, server["baseURL"], args.test_files, server["log_file"]) for server in servers]

            # Wait for all futures to complete
            for future in futures:
                future.result()
        
        print("Tests completed")

    except Exception as e:
        print(f"An error occurred: {str(e)}")

    finally:
        # stop and delete docker containers
        print('Stopping containers')
        stop_and_remove_containers(containers)
    

if __name__ == '__main__':
    __main__()