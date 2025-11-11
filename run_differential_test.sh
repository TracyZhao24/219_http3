#!/bin/bash
set -e

usage()
{
    echo "Usage: $0 <trial_name>"
    echo "  trial_name: Name of the experiemnt. Must have a trial_name.json file in the direct_llm directory."
}

if [ "$#" -ne 1 ]; then
    usage
    exit 1
fi

TEST_FILE="$1.json"
LOG_DIR="$1"
OUTPUT_FILE="diff_results_$1.json"

cd direct_llm
if ! python3 extremal_diff_test_script.py --test_files "$TEST_FILE" --log_dir "$LOG_DIR"; then
    echo "❌ Error running extremal_diff_test_script.py"
    cd ..
    exit 1
fi

cd ../diff_testing
if ! python3 response_comparison.py --results_dir "$LOG_DIR" --output_file "$OUTPUT_FILE"; then
    echo "❌ Error running response_comparison.py"
    cd ..
    exit 1
fi
