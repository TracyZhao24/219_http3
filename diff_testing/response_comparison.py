import re
import glob
import os
import urllib.parse
import json
import argparse

def parse_log_file(log_path):
    """
    Parses a log file (e.g., 'nginx/run_1/0.json') and extracts:
      - test_case index
      - status_code (None if an error/exception occurred)
      - resolved_uri (only if status_code is successful instead of 404, 500, etc.)
    Returns a dict with those fields.
    """
    data = {
        'test_case': None,
        'status_code': None,
        'resolved_uri': None
    }

    with open(log_path, 'r', encoding='utf-8') as f:
        for line in f:
            # Get test case
            match_test_case = re.match(r'^Test case\s+(\d+):', line.strip())
            if match_test_case:
                data['test_case'] = int(match_test_case.group(1))
                continue

            # Match success
            match_success = re.match(r'^Request to .* status code:\s+(\d+)', line.strip())
            if match_success:
                data['status_code'] = int(match_success.group(1))
                continue

            # Match error
            match_error = re.match(r'^Request to .* returned error:\s+(\d+)', line.strip())
            if match_error:
                # If there's an error status code, store it, but no resolved_uri
                data['status_code'] = int(match_error.group(1))
                continue

            # Resolved URI, e.g. http://localhost:8080/abc.txt, host number is different for each implementation
            match_resolved = re.match(r'^Resolved URI:\s+(.*)$', line.strip())
            if match_resolved:
                # Only store resolved path if status_code < 400
                if data['status_code'] and data['status_code'] < 400:
                    full_uri = match_resolved.group(1)
                    parsed = urllib.parse.urlparse(full_uri)
                    # Combine path + query
                    combined = parsed.path
                    if parsed.query:
                        combined += "?" + parsed.query
                    data['resolved_path'] = combined
                else:
                    pass

    return data


def compare_logs_in_subfolders(output_file, subfolder):
    """
    1. We look for JSON files named '0.json', '1.json', etc.
       in the subfolders for each server.
    2. We parse each file (using parse_log_file).
    3. We compare the status_code and resolved_uri across servers
       for each test index.
    """

    # Map server names to the folder where their logs live
    server_dirs = {
        "nginx": f"./nginx/{subfolder}",
        "apache": f"./apache/{subfolder}",
        "caddy": f"./caddy/{subfolder}",
        "lighttpd": f"./lighttpd/{subfolder}",
        "h2o": f"./h2o/{subfolder}",
    }

    # Store the parsed results in a dict-of-dicts:
    # all_results[server][test_index] = parsed_data
    all_results = {server: {} for server in server_dirs}

    # 1) Gather all test indices
    test_indices = set()

    for server, folder in server_dirs.items():
        pattern = os.path.join(folder, '*.json') 
        for path in glob.glob(pattern): # e.g. glob("./nginx/run_1/*.json") -> ["./nginx/run_1/0.json", "./nginx/run_1/1.json", ...]
            filename = os.path.basename(path)  # e.g. "0.json"
            # parse out the test # from "0.json" => 0
            match = re.match(r'^(\d+)\.json$', filename)
            if match:
                test_idx = int(match.group(1))
                test_indices.add(test_idx)
                # Parse it
                parsed_data = parse_log_file(path)
                # Save it in all_results
                all_results[server][test_idx] = parsed_data
    
    differences = []

    # 2) Compare across servers for each test case
    for idx in sorted(test_indices):
        results_for_idx = {}
        for server in server_dirs:
            if idx in all_results[server]:
                results_for_idx[server] = all_results[server][idx]
            else:
                print(f"{server} has no test #{idx} log file")
                results_for_idx[server] = None
        
        

        # Compare each server pair
        server_names = list(server_dirs.keys())
        for i in range(len(server_names)):
            for j in range(i + 1, len(server_names)):
                base = server_names[i]
                other = server_names[j]
                base_data = results_for_idx[base]
                other_data = results_for_idx[other]

                if not base_data or not other_data:
                    continue

            # Compare status codes
            if base_data['status_code'] != other_data['status_code']:
                differences.append({
                    "test_case": idx,
                    "comparison": f"{base} vs {other}",
                    "difference": "status_code",
                    "base_status_code": base_data['status_code'],
                    "other_status_code": other_data['status_code']
                })
                # print(f"[DIFF] Test#{idx} {base} vs {other}: "
                #       f"status {base_data['status_code']} != {other_data['status_code']}")

            # If both are success codes, compare resolved_uri
            if (base_data['status_code'] and base_data['status_code'] < 400 and
                other_data['status_code'] and other_data['status_code'] < 400):
                if base_data['resolved_uri'] != other_data['resolved_uri']:
                    differences.append({
                        "test_case": idx,
                        "comparison": f"{base} vs {other}",
                        "difference": "resolved_uri",
                        "base_resolved_uri": base_data['resolved_uri'],
                        "other_resolved_uri": other_data['resolved_uri']
                    })
                    # print(f"[DIFF] Test#{idx} {base} vs {other}: "
                    #       f"resolved_uri mismatch\n"
                    #       f"  {base}: {base_data['resolved_uri']}\n"
                    #       f"  {other}: {other_data['resolved_uri']}")
    
    with open(output_file, 'w', encoding="utf-8") as output:
        json.dump(differences, output, indent=4)


def main():
    parser = argparse.ArgumentParser(description="Compare responses of different HTTP servers.")
    parser.add_argument(
        '--results_dir',
        required=True,
        help="Subdirectory to read log files from (e.g., run_2, varied_fs_bases)"
    )
    parser.add_argument(
        '--output_file',
        required=True,
        help="File to write results to."
    )
    args = parser.parse_args()

    compare_logs_in_subfolders(args.output_file, args.results_dir)

if __name__ == "__main__":
    main()
