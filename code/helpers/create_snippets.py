import random


def extract_structural_snippets(
    lines: list,
    num_snippets: int = 20,
    max_prev_lines: int = None,
):
    """Extract code snippets from Python code."""
    snippets = []
    for i, line in enumerate(lines):
        stripped = line.strip()
        if stripped and not (
            stripped.startswith("#")
            or stripped.startswith('"""')
            or stripped.startswith("import")
        ):
            if i > 0:
                start = max(0, i - max_prev_lines) if max_prev_lines is not None else 0
                prefix = "".join(lines[start:i])
                target = line.rstrip()
                snippets.append((prefix, target))
    return random.sample(snippets, min(num_snippets, len(snippets))) if snippets else []


def extract_assignment_snippets(
    lines: list,
    num_snippets: int = 30,
    max_prev_lines: int = None,
):
    """
    Extract assignment snippets (=) from Python code.
    Inputs (x) are the code before and LHS of the assignment.
    Targets (y) are the RHS of the assignment.
    """
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


def extract_function_snippets_ts(lines: list, file_base: str):

    snippets = []
    imports = [line for line in lines if line.strip().startswith("import")]
    in_function = False
    function_start = 0
    brace_count = 0
    function_lines = []

    for i, line in enumerate(lines):
        stripped = line.strip()
        if (
            stripped.startswith("export async function")
            or stripped.startswith("export function")
            or stripped.startswith("async function")
            or stripped.startswith("function")
        ) and not in_function:
            in_function = True
            function_start = i
            brace_count = 0
            function_lines = []

        if in_function:
            function_lines.append(line)
            brace_count += stripped.count("{") - stripped.count("}")
            if brace_count == 0 and i > function_start:
                # filter and pick random targets
                body_lines = [
                    line for line in function_lines[1:-1] if len(line.strip()) > 1
                ]
                num_targets = max(1, len(body_lines) // 3)
                if body_lines:
                    target_lines = random.sample(
                        body_lines, min(num_targets, len(body_lines))
                    )
                    for target in target_lines:
                        target_idx = function_lines.index(target)
                        prefix = "".join(imports) + "".join(function_lines[:target_idx])
                        snippets.append((file_base, prefix, target))
                in_function = False

    return snippets


def extract_function_snippets_ts_full_each_line(lines: list, file_base: str):
    """
    Extract function snippets from TypeScript code.
    For each line inside function a snippet is created including the imports and the previous lines of the function as input and the line as target.

    (used for creating evaluation set)
    """
    snippets = []
    imports = [line for line in lines if line.strip().startswith("import")]
    in_function = False
    function_start = 0
    brace_count = 0
    function_lines = []

    for i, line in enumerate(lines):
        stripped = line.strip()
        if (
            stripped.startswith("export async function")
            or stripped.startswith("export function")
            or stripped.startswith("async function")
            or stripped.startswith("function")
        ):
            in_function = True
            function_start = i
            brace_count = 0
            function_lines = []
        if in_function:
            function_lines.append(line)
            brace_count += stripped.count("{") - stripped.count("}")
            if brace_count > 0 and i > function_start + 1:  # After signature
                prefix = "".join(imports) + "".join(
                    function_lines[:-1]
                )  # Imports + function up to last line
                target = function_lines[-1]  # Last line as target
                if len(target.strip()) > 1:
                    snippets.append((file_base, prefix, target))
            if brace_count == 0 and i > function_start:
                in_function = False

    return snippets
