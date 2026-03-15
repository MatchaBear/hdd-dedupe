#!/usr/bin/env python3
"""
hdd-dedupe: Find duplicate files and move them to a review folder.
Duplicates are renamed to show where the kept original lives.

Usage:
    python3 dedupe.py <drive_path> [--dry-run]

Example:
    python3 dedupe.py "/media/hadescloak/SanDisk SSD/"
    python3 dedupe.py "/media/hadescloak/SanDisk SSD/" --dry-run
"""

import subprocess
import os
import shutil
import sys


def make_prefix_from_path(drive_root, filepath):
    """
    Turn the folder path of a file into a prefix string.
    e.g. /media/SanDisk SSD/Japan 2017/Part 4/photo.jpg
         -> Japan_2017__Part_4__
    """
    rel = os.path.relpath(os.path.dirname(filepath), drive_root)
    if rel == ".":
        return "ROOT__"
    # Replace spaces and slashes with underscores, collapse multiples
    prefix = rel.replace("/", "__").replace(" ", "_")
    return prefix + "__"


def build_dest_path(review_folder, kept_file, dupe_file, drive_root):
    """
    Build the destination path for a duplicate file.
    Filename becomes: <folder_of_kept_original>__<original_dupe_filename>
    """
    prefix = make_prefix_from_path(drive_root, kept_file)
    original_name = os.path.basename(dupe_file)
    new_name = prefix + original_name

    dest = os.path.join(review_folder, new_name)

    # Handle filename collisions in review folder
    if os.path.exists(dest):
        base, ext = os.path.splitext(new_name)
        counter = 1
        while os.path.exists(dest):
            dest = os.path.join(review_folder, f"{base}__{counter}{ext}")
            counter += 1

    return dest


def parse_jdupes_output(output, review_folder):
    """
    Parse jdupes output into sets, excluding any files already in review folder.
    Returns list of lists, each list is a duplicate set.
    """
    sets = []
    current_set = []

    for line in output.splitlines():
        line = line.strip()
        if line == "":
            if len(current_set) > 1:
                sets.append(current_set)
            current_set = []
        elif line.startswith("/") or line.startswith("."):
            # Skip files already in review folder
            if review_folder not in line:
                current_set.append(line)

    # Catch last set if file doesn't end with blank line
    if len(current_set) > 1:
        sets.append(current_set)

    return sets


def run(drive_root, dry_run=False):
    drive_root = os.path.realpath(drive_root)
    review_folder = os.path.join(drive_root, "DUPLICATES_FOR_REVIEW")

    print("=" * 60)
    print("  HDD DEDUPE")
    print("=" * 60)
    print(f"  Drive    : {drive_root}")
    print(f"  Review   : {review_folder}")
    print(f"  Dry run  : {'YES — no files will be moved' if dry_run else 'NO — files will be moved'}")
    print("=" * 60)
    print()

    if not dry_run:
        os.makedirs(review_folder, exist_ok=True)

    print("Scanning for duplicates (this may take a while)...")
    result = subprocess.run(
        ["jdupes", "-r", drive_root],
        capture_output=True,
        text=True
    )

    if result.returncode not in (0, 1):
        print(f"jdupes error:\n{result.stderr}")
        sys.exit(1)

    dup_sets = parse_jdupes_output(result.stdout, review_folder)

    if not dup_sets:
        print("No duplicates found!")
        return

    print(f"Found {len(dup_sets)} duplicate set(s).\n")

    total_moved = 0
    total_sets = 0

    for i, dup_set in enumerate(dup_sets, 1):
        kept = dup_set[0]
        dupes = dup_set[1:]

        print(f"[Set {i}]")
        print(f"  KEEP : {kept}")

        for dupe in dupes:
            dest = build_dest_path(review_folder, kept, dupe, drive_root)
            new_name = os.path.basename(dest)

            print(f"  DUPE : {dupe}")
            print(f"    --> REVIEW/{new_name}")

            if not dry_run:
                shutil.move(dupe, dest)
            total_moved += 1

        print()
        total_sets += 1

    print("=" * 60)
    if dry_run:
        print(f"  DRY RUN: {total_moved} files would be moved across {total_sets} sets.")
    else:
        print(f"  DONE: {total_moved} files moved to DUPLICATES_FOR_REVIEW.")
        print(f"  Review the folder, then delete what you don't need.")
    print("=" * 60)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)

    drive_path = sys.argv[1]
    dry_run = "--dry-run" in sys.argv

    if not os.path.isdir(drive_path):
        print(f"Error: '{drive_path}' is not a valid directory.")
        sys.exit(1)

    run(drive_path, dry_run=dry_run)
