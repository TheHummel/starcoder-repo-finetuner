import os
import random
from tqdm import tqdm

script_dir = os.path.dirname(os.path.abspath(__file__))
source_dir = os.path.join(script_dir, "..", "data", "repos", "scrapy", "scrapy")
output_dir = os.path.join(script_dir, "..", "data", "training", "completion")
# source_dir = os.path.join(script_dir, "stock_spider", "spiders")
# output_dir = os.path.join(script_dir, "stock_spider", "data", "evaluation")

if not os.path.isdir(source_dir):
    raise ValueError(f"Source directory {source_dir} not found")
if not os.path.exists(output_dir):
    os.makedirs(output_dir)


def extract_structural_snippets(file_path, num_snippets=10):
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
                if (
                    i + 2 < len(lines)
                    and lines[i + 1].strip()
                    and not lines[i + 1].strip().startswith("#")
                    and not lines[i + 1].strip().startswith('"""')
                ):
                    target += "\n" + lines[i + 1].rstrip()
                snippets.append(("".join(current_snippet), target))
            current_snippet = [line]
        else:
            current_snippet.append(line)
    return random.sample(snippets, min(num_snippets, len(snippets))) if snippets else []


def extract_assignment_snippets(file_path, num_snippets=10):
    with open(file_path, "r", encoding="utf-8") as f:
        lines = f.readlines()
    snippets = []
    current_def = []
    in_def = False
    past_signature = False
    for i, line in enumerate(lines):
        stripped = line.strip()
        if stripped.startswith("def "):
            in_def = True
            past_signature = False
            current_def = [line]
        elif in_def and not past_signature and stripped.endswith(":"):
            current_def.append(line)
        elif in_def and stripped and not stripped.startswith("#"):
            past_signature = True
            if "=" in stripped and "=" in stripped.split(":")[-1]:
                lhs, rhs = stripped.split("=", 1)
                lhs = lhs.strip()
                rhs = rhs.strip()
                if rhs and not rhs.startswith("#"):
                    # include LHS and = in input, RHS in output
                    input_line = f"{lhs} =\n"
                    snippets.append(("".join(current_def) + input_line, rhs))
            current_def.append(line)
        elif in_def and not stripped.startswith(" "):
            in_def = False
            current_def = [line]
        else:
            current_def.append(line)
    return random.sample(snippets, min(num_snippets, len(snippets))) if snippets else []


count = 0
all_snippets = []
for root, _, files in os.walk(source_dir):
    for file in tqdm(files, desc="Processing files"):
        if file.endswith(".py"):
            path = os.path.join(root, file)
            file_base = os.path.splitext(file)[0]
            structural = extract_structural_snippets(path)
            assignments = extract_assignment_snippets(path)
            all_snippets.extend(
                (file_base, prefix, target)
                for prefix, target in structural + assignments
            )
            print(len((assignments)))
        # if len(all_snippets) >= 50:
        #     break

random.shuffle(all_snippets)
for i, (file_base, prefix, target) in enumerate(all_snippets, 1):
    with open(f"{output_dir}/{file_base}_{i:03d}.txt", "w", encoding="utf-8") as f:
        f.write(f"Input: {prefix}\nOutput: {target}\n")
    count += 1

print(f"Generated {count} completion snippets in {output_dir}")
