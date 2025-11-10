#!/usr/bin/env python3
"""
comment_prints.py
------------------------------------
Auto-comments unnecessary print() and print(f"...") calls across a Python project.

Key Features:
✅ Backs up each .py file once before modification into PROJECT_DIR/.print_backups/filename.py.bak.
✅ Comments only print() or print(f...) lines that are not the only print() or print(f...) statement in their block.
✅ Preserves indentation and code structure.
✅ Skips blank and commented lines.
✅ Verifies and prints results.

Core Logic:
If a print() or print(f...) is the ONLY executable line inside a block (if, else, try, etc.),
it is NOT commented — since removing it could break syntax or alter logic flow.
"""

import os
import re
import shutil
from pathlib import Path

# ---------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------
PROJECT_DIR = Path(__file__).resolve().parent.parent
BACKUP_DIR = PROJECT_DIR / ".print_backups"
BACKUP_DIR.mkdir(exist_ok=True)

# Regex patterns
PRINT_PATTERN = re.compile(r'^\s*print\s*\(.*\)\s*$')
COMMENTED_PATTERN = re.compile(r'^\s*#\s*\[auto\]\s*print\s*\(')

# Python block starters
BLOCK_STARTERS = (
    "if ", "elif ", "else:", "for ", "while ", "try:",
    "except", "finally:", "with ", "def ", "class "
)


# ---------------------------------------------------------------------
# Helper Functions
# ---------------------------------------------------------------------
def list_py_files(base_dir: Path):
    for root, _, files in os.walk(base_dir):
        for f in files:
            if f.endswith(".py") and ".print_backups" not in root:
                yield Path(root) / f


def backup_file(src: Path):
    dst = BACKUP_DIR / f"{src.name}.bak"
    if not dst.exists():
        shutil.copy2(src, dst)
        print(f"📦 Backup created: {dst.relative_to(PROJECT_DIR)}")
    else:
        print(f"⚙️ Backup already exists: {dst.relative_to(PROJECT_DIR)}")


def is_executable_line(line: str) -> bool:
    """Detect if a line is actual code (not blank/comment)."""
    stripped = line.strip()
    if not stripped or stripped.startswith("#"):
        return False
    return True


def detect_blocks(lines):
    """
    Analyze structure to identify single-line blocks.
    Returns dict: {line_index: [line_indices_in_block]}.
    """
    blocks = {}
    stack = []

    for i, line in enumerate(lines):
        indent = len(line) - len(line.lstrip())
        stripped = line.strip()

        # Close blocks if indentation decreased
        while stack and indent <= stack[-1]["indent"]:
            stack.pop()

        # Start of a new block
        if stripped.endswith(":") and any(stripped.startswith(k) for k in BLOCK_STARTERS):
            stack.append({"indent": indent, "start": i, "lines": []})
        else:
            # Add line to current block
            if stack:
                stack[-1]["lines"].append(i)

        # Record closed block if no more children
        if not stack and "current_block" in locals():
            current_block = None

        # Save blocks when indentation decreases
        if not stack or (i + 1 < len(lines) and (len(lines[i + 1]) - len(lines[i + 1].lstrip())) <= indent):
            for b in list(stack):
                blocks[b["start"]] = b["lines"]

    return blocks


# ---------------------------------------------------------------------
# Core Function
# ---------------------------------------------------------------------
def process_file(file_path: Path):
    with open(file_path, "r", encoding="utf-8") as f:
        lines = f.readlines()

    backup_file(file_path)
    new_lines = lines.copy()
    blocks = detect_blocks(lines)
    total_changes = 0

    for i, line in enumerate(lines):
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue

        if PRINT_PATTERN.match(line) and not COMMENTED_PATTERN.match(line):
            # Determine if inside a single-line block
            in_single_line_block = False
            for start, block_lines in blocks.items():
                if i in block_lines:
                    # Get executable lines inside block
                    exec_lines = [
                        idx for idx in block_lines if is_executable_line(lines[idx])
                    ]
                    if len(exec_lines) == 1:
                        in_single_line_block = True
                        break

            if in_single_line_block:
                continue  # Skip commenting

            # Comment the print
            indent = " " * (len(line) - len(line.lstrip()))
            new_lines[i] = f"{indent}# [auto] {stripped}\n"
            total_changes += 1

    if total_changes:
        with open(file_path, "w", encoding="utf-8") as f:
            f.writelines(new_lines)
        print(f"✅ Updated {file_path.relative_to(PROJECT_DIR)} ({total_changes} print(s) commented)")
    else:
        print(f"➡️ No changes: {file_path.relative_to(PROJECT_DIR)}")


# ---------------------------------------------------------------------
# Main Execution
# ---------------------------------------------------------------------
def comment_unnecessary_prints():
    print("🔍 Scanning project for Python files...")
    for py_file in list_py_files(PROJECT_DIR):
        process_file(py_file)
    print("\n🎯 Print commenting complete!")


def main():
    """CLI entry point for `comment-prints` command."""
    comment_unnecessary_prints()


if __name__ == "__main__":
    main()
