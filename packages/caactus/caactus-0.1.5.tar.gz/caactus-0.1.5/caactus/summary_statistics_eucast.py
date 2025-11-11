#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
"""

import os
import sys
import argparse
import tomli
import pandas as pd
import seaborn.objects as so  # For plotting


def load_config(path="config.toml"):
    """Load the TOML config file."""
    with open(path, "rb") as f:
        return tomli.load(f)


def process_eucast_data(
    input_dir, output_dir, variable_names,
    class_order, color_mapping,
    conc_order, timepoint_order
):
    """Process EUCAST data and generate a stacked bar plot."""

    df_clean = pd.read_csv(
        os.path.join(input_dir, 'df_clean.csv'), index_col=0
    )

    counts = (
        df_clean.groupby(['filename', 'Predicted Class'])
        .size()
        .reset_index(name='count')
    )

    split_cols = counts['filename'].str.split('_', expand=True)
    counts['conc'] = split_cols[1].str.replace("conc-", "")
    counts['timepoint'] = split_cols[2].str.replace("timepoint-", "")

    # Flag all entries from files that contain any mycelium as mycelium
    filenames_with_mycelium = counts.loc[
        counts['Predicted Class'] == 'mycelium', 'filename'
    ].unique()

    counts.loc[
        counts['filename'].isin(filenames_with_mycelium),
        'Predicted Class'
    ] = 'mycelium'

    counts["Predicted Class"] = pd.Categorical(
        counts["Predicted Class"],
        categories=["not usuable"] + class_order,
        ordered=True
    )

    counts = counts[[
        "filename", "conc", "timepoint",
        "Predicted Class", "count"
    ]]
    counts["conc"] = counts["conc"].astype(float)
    counts.to_csv(os.path.join(output_dir, 'counts_df.csv'))

    # Group by replicates
    unique_experiments = (
        df_clean.groupby(["conc", "timepoint"])["biorep"]
        .nunique()
        .reset_index(name="biorep")
    )
    unique_parallels = (
        df_clean.groupby(["conc", "timepoint"])["techrep"]
        .nunique()
        .reset_index(name="techrep")
    )

    # Aggregate and compute % per category
    merged_df = (
        counts.groupby(["conc", "timepoint", "Predicted Class"])["count"]
        .sum()
        .reset_index(name="count")
    )
    merged_df = merged_df.merge(
        unique_experiments, on=["conc", "timepoint"], how="left"
    )
    merged_df = merged_df.merge(
        unique_parallels, on=["conc", "timepoint"], how="left"
    )

    merged_df["average_count"] = round(
        merged_df["count"] /
        (merged_df["techrep"] * merged_df["biorep"]), 2
    )
    merged_df['%'] = round(
        100 * merged_df["average_count"] /
        merged_df.groupby(["conc", "timepoint"])["average_count"]
        .transform('sum'), 2
    )

    avg_size = (
        df_clean.groupby(["conc", "timepoint", "Predicted Class"])["size_microm"]
        .mean()
        .round(2)
    )
    merged_complete_df = merged_df.merge(
        avg_size, on=["conc", "timepoint", "Predicted Class"], how="left"
    )
    merged_complete_df.to_csv(
        os.path.join(output_dir, 'df_summary_complete.csv')
    )

    # Refined counts without 'not usable'
    counts_df2 = counts[counts["Predicted Class"] != "not usuable"]
    counts_df2 = (
        counts_df2.groupby(["conc", "timepoint", "Predicted Class"])["count"]
        .sum()
        .reset_index(name="count")
    )
    counts_df2 = counts_df2.merge(
        unique_experiments, on=["conc", "timepoint"], how="left"
    )
    counts_df2 = counts_df2.merge(
        unique_parallels, on=["conc", "timepoint"], how="left"
    )
    counts_df2["average_count"] = round(
        counts_df2["count"] /
        (counts_df2["techrep"] * counts_df2["biorep"]), 2
    )
    counts_df2["%"] = round(
        100 * counts_df2["count"] /
        counts_df2.groupby(["conc", "timepoint"])["count"]
        .transform('sum'), 2
    )

    counts_df2_complete_df = counts_df2.merge(
        avg_size, on=["conc", "timepoint", "Predicted Class"], how="left"
    )
    counts_df2_complete_df.to_csv(
        os.path.join(output_dir, 'df_refined_complete.csv')
    )

    # Prepare for plotting
    counts2_reduced_df = counts_df2.drop(
        ["count", "techrep", "biorep"], axis=1
    )
    counts2_reduced_df["Predicted Class"] = pd.Categorical(
        counts2_reduced_df["Predicted Class"],
        categories=class_order,
        ordered=True
    )

    counts2_pivot_df = counts2_reduced_df.pivot_table(
        index=["conc", "timepoint"],
        columns="Predicted Class",
        values="%",
        aggfunc="sum"
    ).replace(0, float("nan")).dropna(how="all").dropna(axis=1, how="all")

    counts2_pivot_df = counts2_pivot_df.reset_index()

    # Melt pivot table
    existing_classes = [
        cls for cls in class_order if cls in counts2_pivot_df.columns
    ]
    counts2_melted_df = counts2_pivot_df.melt(
        id_vars=["conc", "timepoint"],
        value_vars=existing_classes,
        var_name="Predicted Class",
        value_name="%"
    ).dropna()

    # Recast columns
    counts2_melted_df["Predicted Class"] = pd.Categorical(
        counts2_melted_df["Predicted Class"],
        categories=class_order,
        ordered=True
    )
    counts2_melted_df["conc"] = pd.Categorical(
        counts2_melted_df["conc"].astype(float).map(lambda x: f"{x:g}"),
        categories=conc_order,
        ordered=True
    )
    counts2_melted_df["timepoint"] = pd.Categorical(
        counts2_melted_df["timepoint"],
        categories=timepoint_order,
        ordered=True
    )

    # Plot using seaborn.objects
    plot = (
        so.Plot(
            counts2_melted_df,
            x="conc", y="%", color="Predicted Class", text="%"
        )
        .facet(row="timepoint")
        .layout(size=(15, 4))
        .add(so.Bar(), so.Stack())
        .scale(color=color_mapping)
        .label(x="drug concentration (µg/mL)")
    )

    g = plot.plot()
    g.save(os.path.join(output_dir, 'barchart.png'), bbox_inches="tight")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-c", "--config",
        required=True,
        help="Path to config file"
    )
    args = parser.parse_args()

    config = load_config(args.config)
    script_key = "summary_statistics_eucast"

    if script_key not in config:
        print(f"Missing configuration section: [{script_key}]")
        sys.exit(1)

    section = config[script_key]
    section["main_folder"] = config.get("main_folder", ".")

    input_dir = os.path.join(
        section["main_folder"], section["input_path"]
    )
    output_dir = os.path.join(
        section["main_folder"], section["output_path"]
    )
    variable_names = section["variable_names"]
    class_order = section["class_order"]
    color_mapping = section["color_mapping"]
    conc_order = section["conc_order"]
    timepoint_order = section["timepoint_order"]

    process_eucast_data(
        input_dir, output_dir,
        variable_names, class_order,
        color_mapping, conc_order,
        timepoint_order
    )


if __name__ == "__main__":
    main()
