#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# =============================================================================
# File name: assemble.py
# Author: Cl. 10831-10836
# Date created: 2025-04-02
# Version = "1.0"
# License =  "CC0 1.0"
# Reading = "Anabasis by St.-John Perse"
# =============================================================================
""" landscape‑wide galleries from sequentially numbered image sets,
 keeping original aspect ratios and centering vertically."""
# =============================================================================

import os
import sys
from PIL import Image
import regex as re
from typing import Dict, List, Optional, Sequence, Tuple


# --------- Config ----------
INPUT_DIR: str = "input"
OUTPUT_DIR: str = "output_images"
# None => use max image height in group; or set an int (pixels)
PAGE_HEIGHT: Optional[int] = None
BACKGROUND_COLOR: Tuple[int, int, int] = (255, 255, 255)  # white
SUPPORTED_EXT: Sequence[str] = (
    ".jpg", ".jpeg", ".png", ".webp", ".bmp", ".tiff")
# ---------------------------

# Regex to split alphabetic prefix and numeric suffix.
# Will match ..letters..digits..extension. If digit suffix missing, number = 0 and groups by whole alphabetic.
# Examples matched:
#   imgA12 -> prefix='imgA', num=12
#   photo_3 -> prefix='photo_', num=3
#   sample -> prefix='sample', num=0
NAME_RE = re.compile(r"^([\p{L}\p{M}\s_\-]+?)(\d+)?$", re.UNICODE)


def natural_group_key(filename_noext: str) -> Tuple[str, int]:
    """
    Extract a grouping key from a filename without extension.

    The function uses NAME_RE (a regex compiled elsewhere) to parse the filename and
    return a tuple: (prefix, numeric_suffix). If the regex does not match, the entire
    filename is returned as the prefix and 0 as the numeric part.

    Args:
        filename_noext: Filename without extension (e.g., 'img_01').

    Returns:
        A tuple (prefix, num) where prefix is the group identifier string and num is
        the numeric suffix for sorting within the group.
    """
    m = NAME_RE.match(filename_noext)
    if not m:
        return (filename_noext, 0)
    prefix = m.group(1)
    num = int(m.group(2)) if m.group(2) else 0
    return (prefix, num)


def collect_images(input_dir: str) -> List[str]:
    """
    Collect image filenames from a directory that match supported extensions.

    Args:
        input_dir: Path to the directory to scan.

    Returns:
        A list of filenames (not full paths) in the directory that are files and
        have an extension contained in SUPPORTED_EXT (case-insensitive).
    """
    files: List[str] = []
    for entry in os.listdir(input_dir):
        low = entry.lower()
        if not any(low.endswith(ext) for ext in SUPPORTED_EXT):
            continue
        full = os.path.join(input_dir, entry)
        if os.path.isfile(full):
            files.append(entry)
    return files


def group_files(files: Sequence[str]) -> Dict[str, List[Tuple[int, str]]]:
    """
    Group filenames by their natural prefix and attach numeric sort keys.

    The filename extension is stripped before grouping. Each group maps prefix ->
    list of tuples (num, filename). Lists are sorted by numeric key then filename.

    Args:
        files: Sequence of filenames (with extensions).

    Returns:
        A dictionary mapping group prefix -> sorted list of (num, filename).
    """
    groups: Dict[str, List[Tuple[int, str]]] = {}
    for f in files:
        name, _ext = os.path.splitext(f)
        prefix, num = natural_group_key(name)
        groups.setdefault(prefix, []).append((num, f))
    # sort each group's list by numeric then filename to stabilize
    for prefix in groups:
        groups[prefix].sort(key=lambda x: (x[0], x[1]))
    return groups


def stitch_group(
    prefix: str,
    file_list: Sequence[Tuple[int, str]],
    input_dir: str,
    output_dir: str,
    page_height_conf: Optional[int],
) -> None:
    """
    Horizontally stitch a list of images (same group) into one image and save it.

    Behavior:
    - Loads images from input_dir based on file_list (sequence of (num, filename)).
    - If page_height_conf is None, compute page height as the max of image heights.
      Otherwise, use page_height_conf as the target height.
    - Images taller than page height are resized down preserving aspect ratio.
      Smaller images are kept at their height and vertically centered on the canvas.
    - Images are pasted left-to-right in numeric/file order onto an RGBA canvas with
      BACKGROUND_COLOR and then saved as a PNG in output_dir named "{prefix}_stitched.png".

    Args:
        prefix: Group prefix used to name the output file.
        file_list: Sequence of tuples (num, filename) specifying order.
        input_dir: Directory containing the input image files.
        output_dir: Directory where the stitched image will be saved.
        page_height_conf: Optional target page height (pixels). If None, use max input height.

    Returns:
        None. The stitched image is saved to disk. Warnings are printed on load failures.
    """
    # Load images, compute sizes, optionally scale to page height
    imgs: List[Tuple[int, str, Image.Image]] = []
    for num, fname in file_list:
        path = os.path.join(input_dir, fname)
        try:
            im = Image.open(path).convert("RGBA")
        except Exception as e:
            print(f"Warning: failed to open {path}: {e}")
            continue
        imgs.append((num, fname, im))

    if not imgs:
        return

    # Determine target page height
    if page_height_conf is None:
        heights = [im.size[1] for (_, _, im) in imgs]
        page_h = max(heights)
    else:
        page_h = int(page_height_conf)

    # Resize images only if taller than page_h; keep aspect ratio.
    resized: List[Tuple[int, str, Image.Image]] = []
    for num, fname, im in imgs:
        w, h = im.size
        if h > page_h:
            new_h = page_h
            new_w = int(w * (new_h / h))
            im2 = im.resize((new_w, new_h), Image.LANCZOS)
        else:
            im2 = im.copy()
            # optionally can pad vertically later
        resized.append((num, fname, im2))

    # Compute total width and create canvas (landscape = width >= height; we assume horizontal stitch)
    total_w = sum(im.size[0] for (_, _, im) in resized)
    canvas_h = page_h
    canvas_w = max(total_w, canvas_h)  # ensure at least landscape-ish

    canvas = Image.new("RGBA", (canvas_w, canvas_h), BACKGROUND_COLOR + (255,))
    x = 0
    for _, fname, im in resized:
        w, h = im.size
        y = (canvas_h - h) // 2  # vertical center
        canvas.paste(im, (x, y), im if im.mode == "RGBA" else None)
        x += w

    out_name = f"{prefix}_stitched.png"
    out_path = os.path.join(output_dir, out_name)
    canvas_rgb = canvas.convert("RGB")
    canvas_rgb.save(out_path, format="PNG", quality=95)
    print(f"Saved: {out_path}")


def main() -> None:
    """
    Main entry point: validate input/output directories, collect images, group and stitch.

    Exits with code 1 if the input directory is not found.
    """
    inp = INPUT_DIR
    out = OUTPUT_DIR
    if not os.path.isdir(inp):
        print(f"Input directory not found: {inp}")
        sys.exit(1)
    os.makedirs(out, exist_ok=True)

    files = collect_images(inp)
    if not files:
        print("No images found in input folder.")
        return

    groups = group_files(files)

    for prefix, file_list in groups.items():
        stitch_group(prefix, file_list, inp, out, PAGE_HEIGHT)


if __name__ == "__main__":
    main()
