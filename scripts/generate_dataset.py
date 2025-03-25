import os
import random
from tqdm import tqdm

script_dir = os.path.dirname(os.path.abspath(__file__))
source_dir = os.path.join(script_dir, "..", "data", "repos", "scrapy", "scrapy")
output_dir = os.path.join(script_dir, "..", "data", "completion")


if not os.path.isdir(source_dir):
    raise ValueError(f"Source directory {source_dir} does not exist!")


def extract_snippets(file_path, num_snippets=5):
    with open(file_path, "r", encoding="utf-8") as f:
        lines = f.readlines()
    snippets = []
    current_snippet = []
    for i, line in enumerate(lines):
        if (
            line.strip().startswith(("def ", "class ", "if ", "for "))
            and current_snippet
        ):
            if i + 1 < len(lines):
                target = lines[i].rstrip()
                if i + 2 < len(lines) and lines[i + 1].strip():
                    target += "\n" + lines[i + 1].rstrip()
                snippets.append(("".join(current_snippet), target))
            current_snippet = [line]
        else:
            current_snippet.append(line)
    return random.sample(snippets, min(num_snippets, len(snippets))) if snippets else []


count = 0
for root, _, files in os.walk(source_dir):
    for file in tqdm(files, total=min(150, len(files)), desc="Processing files"):
        if file.endswith(".py"):
            path = os.path.join(root, file)
            snippets = extract_snippets(path)
            for prefix, target in snippets:
                count += 1
                with open(f"{output_dir}/{count:03d}.txt", "w", encoding="utf-8") as f:
                    f.write(f"Input: {prefix}\nOutput: {target}\n")
                if count >= 150:
                    break
    if count >= 150:
        break

print(f"Generated {count} completion snippets in {output_dir}")
