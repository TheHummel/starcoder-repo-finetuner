import os
import random
from tqdm import tqdm
from helpers.create_snippets import (
    extract_structural_snippets,
    extract_assignment_snippets,
)
from helpers.convert_data import convert_dataset_to_jsonl


def generate_evaluation_set(
    source_dir: str, output_dir: str, file_types: list[str], filter: str = None
):
    """
    Generate evaluation snippets by extracting snippets from source code files

    Args:
        source_dir (str): Source directory containing source code files
        output_dir (str): Output directory to save evaluation snippets
        file_types (list[str]): List of file extensions to process
        filter (str, optional): Filter to include files containing this string. Defaults to None.
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
                filter is None or filter in file.lower()
            ):
                path = os.path.join(root, file)
                file_base = os.path.splitext(file)[0]
                project = path.split("projects/")[-1].split("/")[0]
                with open(path, "r", encoding="utf-8") as f:
                    lines = f.readlines()
                structural = extract_structural_snippets(lines, max_prev_lines=10)
                # assignments = extract_assignment_snippets(lines, max_prev_lines=10)
                all_snippets.extend(
                    (project, file_base, prefix, target)
                    for prefix, target in structural  # + assignments
                )
                count_files += 1

    random.shuffle(all_snippets)
    for i, (project, file_base, prefix, target) in enumerate(all_snippets, 1):
        with open(
            f"{output_dir}/{project}_{file_base}_{i:03d}.txt", "w", encoding="utf-8"
        ) as f:
            f.write(f"Input: {prefix}\nOutput: {target}\n")
        count_snippets += 1

    print(
        f"Generated {count_snippets} evaluation snippets from {count_files} files in {output_dir}"
    )


if __name__ == "__main__":
    current_dir = os.path.dirname(os.path.abspath(__file__))
    source_dir = os.path.join(current_dir, "..", "data", "repos", "klicker-uzh", "apps")
    output_dir = os.path.join(current_dir, "..", "data", "evaluation", "snippets")

    generate_evaluation_set(
        source_dir, output_dir, file_types=["ts", "tsx"], filter="practicequiz"
    )

    input_dir = output_dir
    output_file = os.path.join(
        current_dir, "..", "data", "evaluation", "evaluation.jsonl"
    )
    convert_dataset_to_jsonl(input_dir, output_file)
