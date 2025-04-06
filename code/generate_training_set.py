import os
import random
import json
from tqdm import tqdm
from helpers.create_snippets import (
    extract_structural_snippets,
    extract_assignment_snippets,
    extract_function_snippets_ts_full_each_line,
    extract_function_snippets_ts,
)
from helpers.convert_data import convert_dataset_to_jsonl


def generate_dataset(
    source_dirs: list[str],
    output_dir: str,
    file_types: list[str],
    filters_out: list[str] = None,
    filters_in: list[str] = None,
):
    """
    Generate snippets from source code files and save them to the output directory.
    Args:
        source_dirs (list[str]): List of source directories containing source code files
        output_dir (str): Output directory to save snippets
        file_types (list[str]): List of file extensions to process
        filters_out (list[str], optional): List of strings to filter out files containing these strings.
        filters_in (list[str], optional): List of strings to include files containing these strings.
    """

    os.makedirs(output_dir, exist_ok=True)
    all_snippets = []

    count_files = 0
    for source_dir in source_dirs:
        if not os.path.isdir(source_dir):
            print(f"Warning: {source_dir} not found. Skipping.")
            continue
        for root, _, files in os.walk(source_dir):
            for file in tqdm(files, desc=f"Processing files in {source_dir}"):
                if (
                    file.split(".")[-1] in file_types
                    and (
                        filters_out is None
                        or all(f.lower() not in file.lower() for f in filters_out)
                    )
                    and (
                        filters_in is None
                        or any(f.lower() in file.lower() for f in filters_in)
                    )
                ):
                    path = os.path.join(root, file)
                    file_base = os.path.splitext(file)[0]
                    with open(path, "r", encoding="utf-8") as f:
                        lines = f.readlines()
                    snippets = extract_function_snippets_ts_full_each_line(
                        lines, file_base
                    )
                    all_snippets.extend(snippets)
                    count_files += 1

    random.shuffle(all_snippets)
    for i, (file_base, prefix, target) in enumerate(all_snippets, 1):
        with open(f"{output_dir}/{file_base}_{i:03d}.txt", "w", encoding="utf-8") as f:
            f.write(f"__INPUT__: {prefix}\n__OUTPUT__: {target}\n")
    print(
        f"Generated {len(all_snippets)} snippets in {count_files} files in {output_dir}"
    )


if __name__ == "__main__":
    script_dir = os.path.dirname(os.path.abspath(__file__))
    source_dirs = [
        os.path.join(
            script_dir,
            "..",
            "data",
            "repos",
            "klicker-uzh",
            "apps",
            "frontend-manage",
            "src",
        ),
        os.path.join(
            script_dir,
            "..",
            "data",
            "repos",
            "klicker-uzh",
            "apps",
            "frontend-pwa",
            "src",
        ),
    ]
    filters_out = [
        "practicequiz",
        "node_modules",
        "dist",
        "cache",
        "test",
        "lib",
        "prisma",
        "_app",
        "2024",
        "2025",
        "seed",
    ]
    # filters_in = [
    #     "microlearning",
    # ]

    output_dir = os.path.join(script_dir, "..", "data", "training", "completion")

    generate_dataset(
        source_dirs, output_dir, file_types=["ts", "tsx"], filters_in=filters_out
    )

    input_dir = output_dir
    output_file = os.path.join(script_dir, "..", "data", "training", "train.jsonl")
    convert_dataset_to_jsonl(input_dir, output_file)
