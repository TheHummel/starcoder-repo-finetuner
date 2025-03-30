import os
import random
from tqdm import tqdm
from helpers.create_snippets import (
    extract_structural_snippets,
    extract_assignment_snippets,
)

script_dir = os.path.dirname(os.path.abspath(__file__))
source_dir = os.path.join(script_dir, "..", "data", "repos", "scrapy", "scrapy")
output_dir = os.path.join(script_dir, "..", "data", "training", "completion")

if not os.path.isdir(source_dir):
    raise ValueError(f"Source directory {source_dir} not found")
os.makedirs(output_dir, exist_ok=True)

count = 0
all_snippets = []
for root, _, files in os.walk(source_dir):
    for file in tqdm(files, desc="Processing files"):
        if file.endswith(".py"):
            path = os.path.join(root, file)
            file_base = os.path.splitext(file)[0]
            with open(path, "r", encoding="utf-8") as f:
                lines = f.readlines()
            structural = extract_structural_snippets(
                lines, num_snippets=50, max_prev_lines=10
            )
            assignments = extract_assignment_snippets(
                lines, num_snippets=50, max_prev_lines=10
            )
            all_snippets.extend(
                (file_base, prefix, target)
                for prefix, target in structural + assignments
            )

random.shuffle(all_snippets)
for i, (file_base, prefix, target) in enumerate(all_snippets, 1):
    with open(f"{output_dir}/{file_base}_{i:03d}.txt", "w", encoding="utf-8") as f:
        f.write(f"Input: {prefix}\nOutput: {target}\n")
    count += 1

print(f"Generated {count} training snippets in {output_dir}")
