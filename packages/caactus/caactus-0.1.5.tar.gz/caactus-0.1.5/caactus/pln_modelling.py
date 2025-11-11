#!/usr/bin/env python3

# -*- coding: utf-8 -*-

"""

import os
import sys
import tomli
import argparse
import pandas as pd
import matplotlib.pyplot as plt
from pyPLNmodels import ZIPln  # For statistical modeling


def load_config(path="config.toml"):
    """Load the TOML config file."""
    with open(path, "rb") as f:
        return tomli.load(f)


def modelling(input_dir, output_dir, variable_names, dynamic_columns):
    """Run ZIPln modelling on input data with dynamic design."""

    # Load counts data
    counts = pd.read_csv(
        os.path.join(input_dir, 'counts_df.csv'),
        index_col=0
    )
    counts = counts[counts["Predicted Class"].notna()]
    # Pivot data: shape is [filename + grouping vars] x [Predicted Classes]
    pivot_df = counts.reset_index().pivot_table(
        index=["filename"] + variable_names,
        columns="Predicted Class",
        values="count",
        fill_value=0
    ).reset_index()

    print(pivot_df)

    # Remove unwanted class if present
    if 'not usuable' in pivot_df.columns:
        pivot_df = pivot_df.drop(columns=["not usuable"])

    # Combine category levels into a single factor
    pivot_df['combined_category'] = (
        pivot_df[variable_names[0]].astype(str) +
        ' & ' +
        pivot_df[variable_names[1]].astype(str)
    )

    # Extract data for model
    combined_dict = {
        variable_names[0]: pivot_df[variable_names[0]].to_numpy(),
        variable_names[1]: pivot_df[variable_names[1]].to_numpy(),
        "combined_category": pivot_df["combined_category"].to_numpy(),
        "counts": pivot_df[dynamic_columns].to_numpy()
    }

    print("Counts dataframe for dictionary:")
    print(combined_dict["counts"])

    # Fit ZIPln model
    formula = f"counts ~ {variable_names[0]} * {variable_names[1]}"
    zipln = ZIPln.from_formula(formula, data=combined_dict)
    zipln.fit()

    print(zipln)

    # PCA visualization with proper legend labels
    fig, ax = plt.subplots(figsize=(10, 6))
    
    # Plot each combined category separately with its label
    for cat in sorted(set(combined_dict["combined_category"])):
        mask = combined_dict["combined_category"] == cat
        ax.scatter(
            zipln.latent_variables[mask, 0],
            zipln.latent_variables[mask, 1],
            label=cat
        )
    
    ax.set_xlabel("Latent Dimension 1")
    ax.set_ylabel("Latent Dimension 2")
    ax.set_title("ZIPln PCA Projection")
    
    # Adjust layout and add legend
    box = ax.get_position()
    ax.set_position([box.x0, box.y0, box.width * 0.75, box.height])
    ax.legend(
        loc='center left',
        bbox_to_anchor=(1, 0.5),
        title='Combined Category'
    )
    
    # Save PCA plot
    plt.savefig(
        os.path.join(output_dir, 'pca_plot.png'),
        bbox_inches='tight'
    )
    plt.show()


    # Plot correlation circle (direct rendering)
    zipln.plot_correlation_circle(
        column_names=[variable_names[0], variable_names[1]],
        column_index=[0, 2]
    )


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
    script_key = "pln_modelling"

    if script_key not in config:
        print(f"Missing configuration section: [{script_key}]")
        sys.exit(1)

    section = config[script_key]
    main_folder = config["main_folder"]
    input_dir = os.path.join(main_folder, section["input_path"])
    output_dir = os.path.join(main_folder, section["output_path"])
    variable_names = section["variable_names"]
    dynamic_columns = section["dynamic_columns"]

    modelling(input_dir, output_dir, variable_names, dynamic_columns)


if __name__ == "__main__":
    main()
