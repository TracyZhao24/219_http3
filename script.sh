#!/bin/bash
set -e

usage()
{
    echo "Usage: $0 <test_files> <log_dir> <output_file>"
    echo "  test_files: Name of the test file"
    echo "  log_dir: Directory to save the logs."
    echo "  output_file: File to save the comparison results."
}

if [ "$#" -ne 3 ]; then
    usage
    exit 1
fi

cd direct_llm
python3 extremal_diff_test_script.py --test_files "$1" --log_dir "$2"
cd ../diff_testing
python3 response_comparison.py --results_dir "$2" --output_file "$3"
