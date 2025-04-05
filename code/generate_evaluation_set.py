import os
import random
from tqdm import tqdm
from helpers.create_snippets import (
    extract_structural_snippets,
    extract_assignment_snippets,
    extract_function_snippets_ts_full_each_line,
)
from helpers.convert_data import convert_dataset_to_jsonl


def generate_evaluation_set(
    source_dirs: list[str],
    output_dir: str,
    file_types: list[str],
    filters_out: list[str] = None,
    filters_in: list[str] = None,
):
    """
    Generate evaluation snippets by extracting snippets from source code files

    Args:
        source_dirs (list[str]): List of source directories containing source code files
        output_dir (str): Output directory to save evaluation snippets
        file_types (list[str]): List of file extensions to process
        filter (str, optional): Filter to include files containing this string. Defaults to None.
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
                    all_snippets.extend(
                        (file_base, prefix, target) for _, prefix, target in snippets
                    )
                    count_files += 1

    random.shuffle(all_snippets)
    count_snippets = 0
    for i, (file_base, prefix, target) in enumerate(all_snippets, 1):
        with open(f"{output_dir}/{file_base}_{i:03d}.txt", "w", encoding="utf-8") as f:
            f.write(f"__INPUT__: {prefix}\n__OUTPUT__: {target}\n")
        count_snippets += 1

    print(
        f"Generated {count_snippets} evaluation snippets from {count_files} files in {output_dir}"
    )


if __name__ == "__main__":
    current_dir = os.path.dirname(os.path.abspath(__file__))
    source_dirs = [
        os.path.join(current_dir, "..", "data", "repos", "klicker-uzh", "apps"),
        os.path.join(current_dir, "..", "data", "repos", "klicker-uzh", "packages"),
    ]
    output_dir = os.path.join(current_dir, "..", "data", "evaluation", "snippets")

    filters_in = ["practicequiz"]

    generate_evaluation_set(
        source_dirs, output_dir, file_types=["ts", "tsx"], filters_in=filters_in
    )

    input_dir = output_dir
    output_file = os.path.join(
        current_dir, "..", "data", "evaluation", "evaluation.jsonl"
    )
    convert_dataset_to_jsonl(input_dir, output_file, separator="__###__")
