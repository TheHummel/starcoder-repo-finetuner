import os
import random
from tqdm import tqdm
from helpers.create_snippets import (
    extract_structural_snippets,
    extract_assignment_snippets,
)

script_dir = os.path.dirname(os.path.abspath(__file__))
source_dir = os.path.join(script_dir, "..", "data", "evaluation", "projects")
output_dir = os.path.join(script_dir, "..", "data", "evaluation", "snippets")

if not os.path.isdir(source_dir):
    raise ValueError(f"Source directory {source_dir} not found")
os.makedirs(output_dir, exist_ok=True)

count = 0
all_snippets = []
for root, _, files in os.walk(source_dir):
    for file in tqdm(files, desc="Processing files"):
        if file.endswith(".py") or file.endswith(".py.tmpl"):
            path = os.path.join(root, file)
            file_base = os.path.splitext(file)[0]
            project = path.split("projects/")[-1].split("/")[0]
            with open(path, "r", encoding="utf-8") as f:
                lines = f.readlines()
            structural = extract_structural_snippets(lines, max_prev_lines=25)
            assignments = extract_assignment_snippets(lines, max_prev_lines=25)
            all_snippets.extend(
                (project, file_base, prefix, target)
                for prefix, target in structural + assignments
            )

random.shuffle(all_snippets)
for i, (project, file_base, prefix, target) in enumerate(all_snippets, 1):
    with open(
        f"{output_dir}/{project}_{file_base}_{i:03d}.txt", "w", encoding="utf-8"
    ) as f:
        f.write(f"Input: {prefix}\nOutput: {target}\n")
    count += 1

print(f"Generated {count} evaluation snippets in {output_dir}")
