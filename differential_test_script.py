import httpx

# Function to send HTTP/2 GET request for each URI
def send_http2_get_requests(baseURL, file_path, log_file):
    with open(file_path, 'r') as file:
        uris = file.readlines()
    
    # Trim any extra whitespace 
    uris = [uri.strip() for uri in uris]
    
    # Create an HTTP/2 client session
    with httpx.Client(base_url=baseURL, http1=True) as client:
        for i, uri in enumerate(uris):
            with open(log_file, 'a') as log:
                log.write(f"Test case {i}: {uri}\n")

            try:
                # Send the GET request
                response = client.get(uri)
                resolved_uri = response.url

                # Raises HTTPStatusError for 4xx/5xx responses
                response.raise_for_status() 

                # Log the successful response content
                # TODO handle if response is a directory instead of a file
                with open(log_file, 'a') as log:
                    log.write(f"Request to {uri} completed with status code: {response.status_code}\n")
                    log.write(f"Resolved URI: {resolved_uri}\n")
                    # Limit dump to first 200 chars
                    log.write(f"Response content from {uri}: {response.text[:200]}\n\n")  

            except httpx.RequestError as e:
                # General request error (e.g., connection issues)
                with open(log_file, 'a') as log:
                    log.write(f"Request to {uri} failed: {str(e)}\n\n")

            except httpx.TimeoutException as e:
                # Timeout error (e.g., server took too long to respond)
                with open(log_file, 'a') as log:
                    log.write(f"Request to {uri} timed out: {str(e)}\n\n")

            except httpx.HTTPStatusError as e:
                # HTTP error (e.g., 404, 500, etc.)
                resolved_url = e.response.url
                with open(log_file, 'a') as log:
                    log.write(f"Request to {uri} returned error: {e.response.status_code}\n")
                    log.write(f"Resolved URL: {resolved_url}\n\n")

            except httpx.TooManyRedirects as e:
                # Too many redirects error
                with open(log_file, 'a') as log:
                    log.write(f"Request to {uri} failed due to too many redirects: {str(e)}\n\n")

            except Exception as e:
                # Catch any other unexpected errors
                with open(log_file, 'a') as log:
                    log.write(f"An unexpected error occurred with {uri}: {str(e)}\n\n")


test_file = 'first.txt'

# name log file <http_impl_name>_log.txt
log_file = 'nginx_log.txt'  

baseURL = "http://localhost:8080"

# Call the function to send the requests
send_http2_get_requests(baseURL, test_file, log_file)
