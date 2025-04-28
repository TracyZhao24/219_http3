# Direct Extremal Test Generation with LLMs

## Generate Test Cases

1. Modify the prompt and output file in `extremal_query.py`. 
2. Call the LLM with your prompt to get code for test case generation: `python3 extremal_query.py`
2. Execute the returned code to get concrete test cases: `python3 <output_file>.py`

## Differential Testing
Run the `extremal_diff_test_script.py` script with a list of files containing your test cases and the name of the subdirectory you would like your log files to be written to.
```
python3 extremal_diff_test_script.py --test_files llm_tests_4.json --log_dir extremal_tests_1
```

## Comparing the Outputs
Run the `response_comparison.py` script with the name of the subdirectory you wrote your log files to during the testing and an output file to write the results of the comparison to.
```
python3 ./diff_testing/response_comparison.py --results_dir extremal_tests_1 --output_file ./diff_testing/diff_results_extremal_tests_1.json
```