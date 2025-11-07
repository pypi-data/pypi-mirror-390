#!/usr/bin/env python3
import os
import json
import re
import sys

def generate_problem_json(folder_path, time_limit, memory_limit, output_json=None):
    test_cases = []
    input_files = [f for f in os.listdir(folder_path) if re.match(r"input_\d+\.txt", f)]
    input_files.sort(key=lambda x: int(re.findall(r'\d+', x)[0]))

    for input_file in input_files:
        idx = re.findall(r'\d+', input_file)[0]
        output_file = f"output_{idx}.txt"
        input_path = os.path.join(folder_path, input_file)
        output_path = os.path.join(folder_path, output_file)

        if not os.path.exists(output_path):
            print(f"Warning: {output_file} does not exist, skipping.")
            continue

        with open(input_path, 'r') as f:
            input_data = f.read()
        with open(output_path, 'r') as f:
            output_data = f.read()

        test_cases.append({
            "input": input_data,
            "output": output_data
        })

    if output_json is None:
        output_json = os.path.basename(os.path.normpath(folder_path)) + ".json"

    problem_json = {
        "time_limit": time_limit,
        "memory_limit": memory_limit,
        "test_case_count": len(test_cases),
        "test_cases": test_cases
    }

    with open(output_json, 'w') as f:
        json.dump(problem_json, f, indent=4)

    print(f"Generated JSON: {output_json}, {len(test_cases)} test cases included.")


def main():
    if len(sys.argv) < 4:
        print("Usage: makejson <folder> <time_limit> <memory_limit> [output_json]")
        sys.exit(1)

    folder = sys.argv[1]
    time_limit = int(sys.argv[2])
    memory_limit = int(sys.argv[3])
    output_json = sys.argv[4] if len(sys.argv) >= 5 else None

    generate_problem_json(folder, time_limit, memory_limit, output_json)


if __name__ == "__main__":
    main()
