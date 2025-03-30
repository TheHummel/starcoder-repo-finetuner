import random


def extract_structural_snippets(lines, num_snippets=20, max_prev_lines=None):
    snippets = []
    for i, line in enumerate(lines):
        stripped = line.strip()
        if stripped and not (stripped.startswith("#") or stripped.startswith('"""')):
            if i > 0:
                start = max(0, i - max_prev_lines) if max_prev_lines is not None else 0
                prefix = "".join(lines[start:i])
                target = line.rstrip()
                snippets.append((prefix, target))
    return random.sample(snippets, min(num_snippets, len(snippets))) if snippets else []


def extract_assignment_snippets(lines, num_snippets=30, max_prev_lines=None):
    snippets = []
    in_def = False
    for i, line in enumerate(lines):
        stripped = line.strip()
        if stripped.startswith("def "):
            in_def = True
        elif in_def and stripped and "=" in stripped and not stripped.startswith("#"):
            if "=" in stripped.split(":")[-1]:
                lhs, rhs = stripped.split("=", 1)
                lhs, rhs = lhs.strip(), rhs.strip()
                if rhs and not rhs.startswith("#"):
                    start = (
                        max(0, i - max_prev_lines) if max_prev_lines is not None else 0
                    )
                    prefix = "".join(lines[start:i]) + f"{lhs} =\n"
                    snippets.append((prefix, rhs))
        elif in_def and not stripped.startswith(" "):
            in_def = False
    return random.sample(snippets, min(num_snippets, len(snippets))) if snippets else []
