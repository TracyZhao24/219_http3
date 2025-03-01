import httpx
import json
from concurrent.futures import ThreadPoolExecutor
import docker
import os

# Build docker image from dockerfile 
def build_image(dockerfile_path, tag):
    client = docker.from_env()
    print(f"Building image {tag} from {dockerfile_path}")
    image, logs = client.images.build(path=dockerfile_path, tag=tag)
    for log in logs:
        print(log.get('stream', '').strip())
    return image


# Start each docker container
def start_container(name, image, port, client):
    container = client.containers.run(
        image.id,
        name=name,
        ports={f"{port}/tcp": port},
        detach=True
    )
    print(f"Started container {name} on port {port}")
    return container


# Start all docker containers
def start_all_containers():
    client = docker.from_env()
    # Define  server configurations
    servers = [
        {"name": "nginx", "dockerfile": "./diff_testing/nginx.dockerfile", "port": 8080},
        {"name": "h2o", "dockerfile": "./diff_testing/h2o.dockerfile", "port": 8081},
        {"name": "apache", "dockerfile": "./diff_testing/apache.dockerfile", "port": 8082}
    ]

    containers = []
    for server in servers:
        # Build the image from the Dockerfile
        image = build_image(server["dockerfile"], server["name"])
        container = start_container(server["name"], image, server["port"], client)
        containers.append(container)

    return containers


# Send HTTP/1 GET request for each URI
def send_http2_get_requests(baseURL, file_path, log_file):
    with open(file_path, 'r', encoding="utf-8") as file:
        uris = json.load(file)
    
    # Create a HTTP client session
    with httpx.Client(base_url=baseURL, http1=True) as client, open(log_file, 'a', encoding="utf-8") as log:
        for i, obj in enumerate(uris):
            uri = obj["relative_uri"].strip()
            # print(uri)

            log.write(f"Test case {i}: {uri}\n")

            try:
                # Send the GET request
                response = client.get(uri)
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
                resolved_uri = e.response.url
                log.write(f"Request to {uri} failed: {str(e)}\n\n")
                log.write(f"Resolved URL: {resolved_uri}\n\n")

            except httpx.TimeoutException as e:
                # Timeout error (e.g., server took too long to respond)
                resolved_uri = e.response.url
                log.write(f"Request to {uri} timed out: {str(e)}\n\n")
                log.write(f"Resolved URL: {resolved_uri}\n\n")

            except httpx.HTTPStatusError as e:
                # HTTP error (e.g., 404, 500, etc.)
                resolved_uri = e.response.url
                log.write(f"Request to {uri} returned error: {e.response.status_code}\n")
                log.write(f"Resolved URL: {resolved_uri}\n\n")

            except httpx.TooManyRedirects as e:
                # Too many redirects error
                resolved_uri = e.response.url
                log.write(f"Request to {uri} failed due to too many redirects: {str(e)}\n\n")
                log.write(f"Resolved URL: {resolved_uri}\n\n")

            except Exception as e:
                # Catch any other unexpected errors
                log.write(f"An unexpected error occurred with {uri}: {str(e)}\n\n")


def test_server(baseURL, file_path, log_file):
    send_http2_get_requests(baseURL, file_path, log_file)


def __main__():
    print('Starting containers')

    start_all_containers()
    
    test_file = 'unpack_test.json'

    # Define the different server implementations and their log files
    servers = [
        {"baseURL": "http://localhost:8080", "log_file": "nginx_log.txt"},
        {"baseURL": "http://localhost:8081", "log_file": "h2o_log.txt"},
        {"baseURL": "http://localhost:8082", "log_file": "apache_log.txt"}
    ]

    # Use ThreadPoolExecutor to run tests
    with ThreadPoolExecutor() as executor:
        futures = [executor.submit(test_server, server["baseURL"], test_file, server["log_file"]) for server in servers]

        # Wait for all futures to complete
        for future in futures:
            future.result()

    print("Tests completed")
