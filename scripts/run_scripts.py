import sys
import subprocess
import csv
import re
import json
import os
import argparse


def run_script_with_args(script_path, args, env=None):
    """
    Run a Python script with specified arguments and environment variables.

    Args:
        script_path (str): path to the Python script.
        args (list): List of arguments to pass to the script.
        env (dict): Dictionary of environment variables to set.

    Returns:
        tuple: A tuple containing the script's output and any error messages, or (None, None) if no error occurs.
    """
    try:
        # setup environment variabe before run the script if provides.
        if env:
            for key, value in env.items():
                os.environ[key] = value
        # Start running script in sub-process
        result = subprocess.run(["python", script_path] + args, capture_output=True, text=True, check=True)
        return result.stdout, result.stderr
    except subprocess.CalledProcessError as e:
        print("Error: ", e)
        return None, e.stderr


def parse_output(output, patterns):
    """
    parse the output of a script using specified patterns.

    Args:
        output (str): The output of the script.
        patterns (dict): Dictionary of patterns to search for in the output.

    Returns:
        dict: A dictionary containing the matched patterns and their corresponding values.
    """
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
    """
    Main function to run scripts with various arguments and process console output, then store results in CSV.

    Args:
        args (argparse.Namespace): Command-line arguments.

    Returns:
        None
    """
    scripts_file = args.scripts_file
    patterns_file = args.patterns_file
    output_file = args.output_file or "results.csv"

    # Load script and pattern configurations from JSON files
    with open(scripts_file, "r") as file:
        scripts_data = json.load(file)

    with open(patterns_file, "r") as file:
        patterns_data = json.load(file)

    scripts = scripts_data.get("scripts", [])
    result_patterns = patterns_data.get("result_patterns", {})
    error_patterns = patterns_data.get("error_patterns", {})

    print(f"Running {len(scripts)} scripts:")

    # Open CSV file for writing results
    with open(output_file, "w", newline="") as csvfile:
        extra_arguments_keys = set()
        for script in scripts:
            extra_arguments_list = script.get("extra_arguments", [])
            for extra_arguments in extra_arguments_list:
                extra_arguments_keys.update(extra_arguments.keys())

        header = ["Model"] + sorted(extra_arguments_keys) + list(result_patterns.keys()) + ["Error"]

        csv_writer = csv.writer(csvfile)
        csv_writer.writerow(header)

        for script in scripts:
            script_name = script.get("name", "")
            script_path = script.get("path", "")
            default_arguments = script.get("default_arguments", [])
            extra_arguments_list = script.get("extra_arguments", [])
            env = script.get("env", {})

            print(f"---> {script_name} with {len(extra_arguments_list)} set(s) of extra arguments ...")
            print(f"      Default Argument:")
            print(f"            {default_arguments}")

            # Check if all default arguments are provided
            # if not all(arg in default_arguments for arg in default_arguments):
            #     print(f"Error: Missing default arguments for script '{script_name}'")
            #     continue
            # Check if default_arguments list is not empty
            if not default_arguments:
                print(f"Warning: No default arguments provided for script '{script_name}'")
                continue

            # Combine default and extra arguments, if provided
            if extra_arguments_list:
                for extra_arguments in extra_arguments_list:
                    #arguments = default_arguments + ["--{} {}".format(key, value) for key, value in extra_arguments.items()]
                    arguments = default_arguments.copy() # make a copy of default_arguments
                    for key, value in extra_arguments.items():
                        arguments.append("--{}".format(key))
                        if value and value != "":
                            arguments.append(value)

                    # Fill extra arguments columns with values or empty strings if not provided
                    extra_arguments_row = [extra_arguments.get(key, "") for key in sorted(extra_arguments_keys)]
                    
                    print(f"    ... Running with: {extra_arguments}")
                    # Run the script with arguments and process the output
                    output, error = run_script_with_args(script_path, arguments, env=env)
                    result_row = [script_name] + extra_arguments_row

                    if output:
                        result_dict = parse_output(output, result_patterns)
                        for pattern_name in result_patterns.keys():
                            result_row.append(result_dict.get(pattern_name, ""))
                    else:
                        result_row.extend([""] * len(result_patterns))

                    # Process error message
                    if error:
                        error_messages = parse_output(error, error_patterns)
                        error_str = "; ".join([f"{name}: {message}" for name, message in error_messages.items()])
                        result_row.append(error_str)
                    else:
                        result_row.extend("")

                    # Write the result row to the CSV file
                    csv_writer.writerow(result_row)
            else:
                # Run with only default arguments
                arguments = default_arguments

                # Run the script with arguments and process the output
                output, error = run_script_with_args(script_path, arguments, env=env)
                result_row = [script_name] + [""] * len(extra_arguments_keys)

                if output:
                    result_dict = parse_output(output, result_patterns)
                    for pattern_name in result_patterns.keys():
                        result_row.append(result_dict.get(pattern_name, ""))
                else:
                    result_row.extend([""] * len(result_patterns))

                # Process error message
                if error:
                    error_messages = parse_output(error, error_patterns)
                    error_str = "; ".join([f"{name}: {message}" for name, message in error_messages.items()])
                    result_row.append(error_str)
                else:
                    result_row.extend("")

                # Write the result row to the CSV file
                csv_writer.writerow(result_row)


if __name__ == "__main__":
    # Create an ArgumentParser object
    parser = argparse.ArgumentParser(description="Run scripts with various arguments and process console output, then store results in CSV.")

    # Add arguments with detailed descriptions
    parser.add_argument("--scripts_file", required=True, help="JSON file containing script configuration")
    parser.add_argument("--patterns_file", required=True, help="JSON file containing result and error patterns")
    parser.add_argument("-o", "--output_file", default="results.csv", help="Output CSV file path (default: results.csv)")

    # Parse the command-line arguments
    args = parser.parse_args()
    # Call main function
    main(args)
