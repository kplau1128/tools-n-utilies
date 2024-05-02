import sys
import subprocess
import csv
import re
import json
import os
import argparse


def run_script_with_args(script_path, args, env=None):
    try:
        # setup environment variabe before run the script if provides.
        if env:
            for key, value in env.items():
                os.environ[key] = value

        result = subprocess.run(["python", script_path] + args, capture_output=True, text=True, check=True)
        return result.stdout, result.stderr
    except subprocess.CalledProcessError as e:
        print("Error: ", e)
        return None, e.stderr


def parse_output(output, patterns):
    result_dict = {}
    for pattern_name, pattern in patterns.items():
        match = re.search(pattern, output)
        if match:
            value = match.group(1)
            # Round to integer if value is a long numerical decimal
            if re.match(r'^\d+\.\d+$', value):
                value = str(round(float(value), 2))
            result_dict[pattern_name] = value
    return result_dict


# main()
def main(args):
    with open(args.scripts_file, "r") as file:
        scripts_data = json.load(file)

    with open(args.patterns_file, "r") as file:
        patterns_data = json.load(file)

    scripts = scripts_data.get("scripts", [])
    result_patterns = patterns_data.get("result_patterns", {})
    error_patterns = patterns_data.get("error_patterns", {})

    output_file = args.output_file

    print(f"Running {len(scripts)} scripts:")

    with open(output_file, "w", newline="") as csvfile:
        csv_writer = csv.writer(csvfile)
        csv_writer.writerow(["Model", "Extra Arguments"] + list(result_patterns.keys()) + ["Errors"])

        for script in scripts:
            script_name = script.get("name", "")
            script_path = script.get("path", "")
            default_arguments = script.get("default_arguments", [])
            extra_arguments_list = script.get("extra_arguments", [])
            env = script.get("env", {})

            print(f"---> {script_name} with {len(extra_arguments_list)} set(s) of extra arguments ...")
            # Check if all mandatory arguments are provided
            # if not all(arg in os.environ for arg in mandatory_arguments):
            #     print(f"Error: Missing mandatory arguments for script '{script_name}'")
            #     continue

            if extra_arguments_list:
                for extra_arguments in extra_arguments_list:
                    # Combine deafult and extra arguments
                    arguments = default_arguments + extra_arguments
                    print(f"    ... Running with: {extra_arguments}")

                    output, error = run_script_with_args(script_path, arguments, env=env)
                    result_row = [script_name, ", ".join(extra_arguments)]

                    if output:
                        result_dict = parse_output(output, result_patterns)
                        for pattern_name in result_patterns.keys():
                            result_row.append(result_dict.get(pattern_name, ""))
                    else:
                        result_row.extend([""] * len(result_patterns))

                    if error:
                        error_messages = parse_output(error, error_patterns)
                        error_str = "; ".join([f"{name}: {message}" for name, message in error_messages.items()])
                        result_row.append(error_str)
                    else:
                        result_row.extend("")

                    csv_writer.writerow(result_row)
            else:
                # Run with only default arguments
                arguments = default_arguments

                output, error = run_script_with_args(script_path, arguments, env=env)
                result_row = [script_name, ""]

                if output:
                    result_dict = parse_output(output, result_patterns)
                    for pattern_name in result_patterns.keys():
                        result_row.append(result_dict.get(pattern_name, ""))
                else:
                    result_row.extend([""] * len(result_patterns))

                if error:
                    error_messages = parse_output(error, error_patterns)
                    error_str = "; ".join([f"{name}: {message}" for name, message in error_messages.items()])
                    result_row.append(error_str)
                else:
                    result_row.extend("")

                csv_writer.writerow(result_row)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run scripts with various arguments and process console output, then store results in CSV.")

    parser.add_argument("scripts_file", help="JSON file containing script configuration")
    parser.add_argument("patterns_file", help="JSON file containing result and error patterns")
    parser.add_argument("-o", "--output_file", default="results.csv", help="Output CSV file path (default: results.csv)")
    args = parser.parse_args()

    main(args)
