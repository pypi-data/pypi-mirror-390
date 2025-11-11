#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""

"""

import os  # For interacting with the file system
import pandas as pd  # For handling CSV data
import shutil  # For copying and renaming files
import re  # For natural sorting using regex
import tomli  # For loading the configuration file
import argparse  # For command-line parsing
import sys  # For error handling and exit


def load_config(path="config.toml"):
    with open(path, "rb") as f:
        return tomli.load(f)


def natural_sort_key(s):
    """
    Key function for natural sorting of file names.
    Splits strings into parts of digits and non-digits for natural ordering.
    """
    return [int(text) if text.isdigit() else text.lower()
            for text in re.split(r'(\d+)', s)]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-c", "--config",
        required=True,
        default="config.toml",
        help="Path to config file"
    )
    args = parser.parse_args()

    config = load_config(args.config)
    script_key = "renaming"

    if script_key not in config:
        print(f"Missing configuration section: [{script_key}]")
        sys.exit(1)

    section = config[script_key]
    main_folder = config["main_folder"]
    input_path = section["input_path"]
    output_path = section["output_path"]
    csv_rename = section["csv_rename"]

    input_dir = os.path.join(main_folder, input_path)
    output_dir = os.path.join(main_folder, output_path)
    csv_file = os.path.join(main_folder, csv_rename)

    # Load new names from the CSV file
    try:
        df = pd.read_csv(csv_file)
    except FileNotFoundError:
        print(f"The file {csv_file} was not found.")
        sys.exit(1)

    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)

    # List and sort files naturally
    files = [f for f in os.listdir(input_dir)
             if os.path.isfile(os.path.join(input_dir, f))
             and not f.startswith('.')]
    files.sort(key=natural_sort_key)

    if len(df) != len(files):
        print("The number of new names does not match the number of files.")
        print(f"Number of files: {len(files)}")
        print(f"Number of new names: {len(df)}")
    else:
        for idx, row in df.iterrows():
            new_file_name = "_".join(
                [f"{col}-{row[col]}" for col in df.columns]) + ".tif"
            current_file_name = files[idx]
            current_file_path = os.path.join(input_dir, current_file_name)
            new_file_path = os.path.join(output_dir, new_file_name)

            shutil.copy(current_file_path, new_file_path)
            print(f"Renamed '{current_file_name}' to '{new_file_name}'")

        print("Batch renaming completed.")


if __name__ == "__main__":
    main()

