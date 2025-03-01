import os
import subprocess
import re
import json

# Path to the KLEE output directory
klee_output_dir = '/home/klee/klee-out-3'

# Path to the output JSON file
output_json_file = 'klee_strings.json'

# Function to convert a hex value to a character
def hex_to_char(hex_value):
    # Convert hex to integer and then to the corresponding character
    return chr(int(hex_value, 16))

# Function to extract the symbolic characters from a .ktest file
def extract_c_string_from_ktest(ktest_file):
    # Use ktest-tool to extract data from the .ktest file
    result = subprocess.run(['ktest-tool', ktest_file], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    
    if result.returncode != 0:
        print(f"Error extracting data from {ktest_file}: {result.stderr}")
        return None
    
    data = result.stdout.split('\n')

    # Regex pattern to match lines like "object n: hex : {hex code for char}"
    hex_pattern = re.compile(r'object \d+: hex')
    
    # Initialize an empty string to hold the C string
    c_string = ""
    
    # Loop through each line and check if it contains the pattern
    for line in data:
        match = hex_pattern.search(line)
        if match:
            # hex_value = match.group(1)  # Extract the hex code
            # print(line)
            hex_value = line[-5:]
            # print(hex_value)
            char = hex_to_char(hex_value)  # Convert hex to char
            # do not append null characters
            if char != '\x00':
                c_string += char  # Append the character to the string
    
    return c_string

# Function to process all .ktest files in the KLEE output directory
def process_klee_tests(klee_output_dir):
    tests = []
    
    # Iterate through the KLEE output directory to find .ktest files
    for filename in os.listdir(klee_output_dir):
        if filename.endswith('.ktest'):
            # print("found file")
            ktest_file_path = os.path.join(klee_output_dir, filename)
            # print(ktest_file_path)
            c_string = extract_c_string_from_ktest(ktest_file_path)
            if c_string:
                tests.append({
                    "base_uri": "http://a.a/a",
                    "relative_uri": c_string
                })
    
    return tests

# Main function to write the extracted C strings to a JSON file
def write_strings_to_json(klee_output_dir, output_json_file):
    tests = process_klee_tests(klee_output_dir)
    
    if tests:
        with open(output_json_file, 'w') as json_file:
            json.dump(tests, json_file, indent=4)
            print(f"C strings have been written to {output_json_file}")
    else:
        print("No test data found.")

# Run the function
# klee_output_dir: "./testX"
# output_json_file: "./all_tests/testX.json"
write_strings_to_json("./testX", "./all_tests/testX.json")
