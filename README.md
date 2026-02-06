# Assembling image strips

**Il naissait un poulain sous les feuilles de bronze..**

![Banner Image](<img/(Toulouse)_Mon_seul_désir_(La_Dame_à_la_licorne)_-_Musée_de_Cluny_Paris.jpg> "An image depicting a piece of the lady and the unicorn tapestry.")
<br> Mon seul désir. *Musée de Cluny, Paris*.

## Genesis

> Just needed a tool to quickly proofread some snaps. The script concatenates images with shared alphabetic prefixes into horizontally stitched strips.

## Features
![Banner Image](<img/strip.gif> "A demo of the algorithm.")
<br> *Concept example*.

- Groups files by alphabetic prefix + sequential numeric suffix ordering.
- Supports **common image formats**: JPG, PNG, WEBP, BMP, TIFF.
- *Optional page-height configuration*: scale images taller than the page height while preserving aspect ratio; otherwise uses the tallest image in the group.
- Vertical centering and configurable background color.
- Saves stitched images with a `_stitched.png` prefix.

## Requirements

- Python 3.x  
- Pillow  
- regex (the third-party `regex` module)

Install dependencies:

```bash
pip install pillow regex
```

## Quickstart

- Put source images into `INPUT_DIR`.
- Adjust configuration at top of the script if needed:
  - `INPUT_DIR`, `OUTPUT_DIR`
  - `PAGE_HEIGHT` (`None` to auto-use max height in group, or set integer pixels)
  - `BACKGROUND_COLOR` (RGB tuple)
  - `SUPPORTED_EXT` (tuple of supported image extensions)

- Run:

```bash
python assemble.py
```

Output files are written into `OUTPUT_DIR` (default: `output_images`).

## Configuration example

At top of the script:

```python
INPUT_DIR = "input"
OUTPUT_DIR = "output_images"
PAGE_HEIGHT = None             # or PAGE_HEIGHT = 1200
BACKGROUND_COLOR = (255,255,255)
SUPPORTED_EXT = (".jpg", ".jpeg", ".png", ".webp", ".bmp", ".tiff")
```

### Example workflow

Files:

- `input/photo1.jpg`
- `input/photo2.jpg`
- `input/logo.png`

Result:

- `output_images/photo_stitched.png` (photo1 + photo2 stitched)  
- `output_images/logo_stitched.png` (single-image stitched output)

## Filename grouping rules

Achieved through a regex to split the filename (without extension) into:

- `prefix`: one or more letters, marks, whitespace, underscore or hyphen
- an optional numeric `num` suffix

*Examples:*

- `imgA12.jpg` → prefix `imgA`, num `12`
- `photo_3.png` → prefix `photo_`, num `3`  
- `sample.bmp` → prefix `sample`, num `0`

>[!NOTE]
> Files without a supported extension are ignored.

## Functional overview

- `collect_images`: scans `INPUT_DIR` and returns files with supported extensions.
- `group_files`: groups files by prefix, sorts each group by numeric suffix then filename for deterministic ordering.
- `stitch_group`:
  - Loads images with Pillow and converts to RGBA.
  - Determines page height: `PAGE_HEIGHT` if set, otherwise max image height in the group.
  - Resizes images taller than page height to match page height (preserves aspect ratio).
  - Computes canvas width as sum of image widths (ensures canvas width ≥ canvas height).
  - Pastes images side-by-side, vertically centered, onto an RGBA canvas using `BACKGROUND_COLOR`.
  - Converts to RGB and saves as PNG named `groupname + _stitched.png` in `OUTPUT_DIR`.
- Script prints warnings for unreadable files and prints saved output paths.

## Troubleshooting

- **"Input directory not found"**: ensure `INPUT_DIR` exists or update the path.
- **"No images found"**: verify supported extensions and that files are not hidden.
- Corrupt/unopenable images: script prints a warning and skips them.
- If Unicode filenames cause issues, ensure your environment supports UTF-8 and that the `regex` module is installed.

## Limitations

- Horizontal-only stitching: images are concatenated side-by-side (landscape orientation assumed).  
- `PAGE_HEIGHT` only scales images that are taller than the target height; shorter images are not padded vertically (they are centered).  
- The grouping regex focuses on letter/mark characters plus optional digits; unusual naming schemes may produce unexpected groups.  
- Output is flattened to RGB PNG; alpha becomes composited over `BACKGROUND_COLOR`.

## License

 Creative Commons [Zero v1.0 Universal](https://creativecommons.org/public-domain/cc0/).

🀆
