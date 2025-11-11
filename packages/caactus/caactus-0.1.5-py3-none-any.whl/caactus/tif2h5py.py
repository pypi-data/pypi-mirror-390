#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
"""

import os
import sys
import tomli
import h5py
import tifffile
import vigra
import argparse
import imagecodecs  # Ensures image codecs are registered


def load_config(path="config.toml"):
    """Load a TOML configuration file."""
    with open(path, "rb") as f:
        return tomli.load(f)


def convert_tif_to_h5(input_dir, output_dir):
    """Convert all .tif files in input_dir to .h5 format in output_dir."""

    os.makedirs(output_dir, exist_ok=True)

    tif_files = [f for f in os.listdir(input_dir) if f.endswith('.tif')]
    if not tif_files:
        print("No .tif files found in input directory.")
        return

    for tif_file in tif_files:
        tif_path = os.path.join(input_dir, tif_file)

        with tifffile.TiffFile(tif_path) as tiff:
            image_data = tiff.asarray()
            print("Image data shape:", image_data.shape)

            if len(image_data.shape) == 3:
                image_data_5d = image_data.reshape((1, 1, *image_data.shape))
            elif len(image_data.shape) == 4:
                image_data_5d = image_data.reshape((1, *image_data.shape))
            else:
                raise ValueError(f"Unexpected image shape: {image_data.shape}")

            data_shape = image_data_5d.shape
            axistags = vigra.defaultAxistags("tzyxc")

            h5_file = os.path.splitext(tif_file)[0] + '.h5'
            h5_path = os.path.join(output_dir, h5_file)

            with h5py.File(h5_path, 'w') as h5:
                ds = h5.create_dataset(
                    name='data',
                    data=image_data_5d,
                    chunks=(1, 1, 256, 256, 1)
                )
                ds.attrs["axistags"] = axistags.toJSON()
                ds.attrs["data_shape"] = data_shape

        print(f"Converted {tif_file} to {h5_file}")


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-c", "--config",
        required=True,
        help="Path to config file"
    )
    parser.add_argument(
        "-m", "--mode",
        required=True,
        choices=["training", "batch"],
        help="Define if training or batch mode"
    )
    args = parser.parse_args()

    config = load_config(args.config)
    script_key = "tif2h5py"

    if script_key not in config or args.mode not in config[script_key]:
        print(f"Missing configuration for [{script_key}.{args.mode}]")
        sys.exit(1)

    section = config[script_key][args.mode]
    main_folder = config["main_folder"]
    input_dir = os.path.join(main_folder, section["input_path"])
    output_dir = os.path.join(main_folder, section["output_path"])

    convert_tif_to_h5(input_dir, output_dir)


if __name__ == "__main__":
    main()
