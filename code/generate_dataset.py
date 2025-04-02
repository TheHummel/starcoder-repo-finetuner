import os
import random
import json
from tqdm import tqdm
from helpers.create_snippets import (
    extract_structural_snippets,
    extract_assignment_snippets,
)
from helpers.convert_data import convert_dataset_to_jsonl


def generate_dataset(
    source_dir: str, output_dir: str, file_types: list[str], filter: str = None
):
    """
    Generate training dataset by extracting snippets from source code files

    Args:
        source_dir (str): Source directory containing source code files
        output_dir (str): Output directory to save training snippets
        file_types (list[str]): List of file extensions to process
        filter (str, optional): Filter to exclude files containing this string. Defaults to None.
    """

    if not os.path.isdir(source_dir):
        raise ValueError(f"Source directory {source_dir} not found")
    os.makedirs(output_dir, exist_ok=True)

    count_snippets = 0
    count_files = 0
    all_snippets = []
    for root, _, files in os.walk(source_dir):
        for file in tqdm(files, desc="Processing files"):
            if file.split(".")[-1] in file_types and (
                filter is None or filter not in file.lower()
            ):
                path = os.path.join(root, file)
                file_base = os.path.splitext(file)[0]
                with open(path, "r", encoding="utf-8") as f:
                    lines = f.readlines()
                structural = extract_structural_snippets(
                    lines, num_snippets=50, max_prev_lines=10
                )
                # assignments = extract_assignment_snippets(
                #     lines, num_snippets=50, max_prev_lines=10
                # )
                all_snippets.extend(
                    (file_base, prefix, target)
                    for prefix, target in structural  # + assignments
                )
                count_files += 1

    random.shuffle(all_snippets)
    for i, (file_base, prefix, target) in enumerate(all_snippets, 1):
        with open(f"{output_dir}/{file_base}_{i:03d}.txt", "w", encoding="utf-8") as f:
            f.write(f"Input: {prefix}\nOutput: {target}\n")
        count_snippets += 1

    print(
        f"Generated {count_snippets} training snippets from {count_files} files in {output_dir}"
    )


if __name__ == "__main__":
    script_dir = os.path.dirname(os.path.abspath(__file__))
    source_dir = os.path.join(script_dir, "..", "data", "repos", "klicker-uzh", "apps")
    output_dir = os.path.join(script_dir, "..", "data", "training", "completion")

    generate_dataset(
        source_dir, output_dir, file_types=["ts", "tsx"], filter="practicequiz"
    )

    input_dir = output_dir
    output_file = os.path.join(script_dir, "..", "data", "training", "train.jsonl")
    convert_dataset_to_jsonl(input_dir, output_file)
