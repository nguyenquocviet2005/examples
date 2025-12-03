# Chandra OCR Testing

Vietnamese OCR using Chandra model.

## Setup

```bash
python -m venv .venv
source .venv/bin/activate
pip install chandra-ocr pillow
```

## Run

```bash
source .venv/bin/activate

# Run OCR on an image
python test_chandra_working.py <image_path> [output_dir]

# Example
python test_chandra_working.py assets/examples/test1.jpg ./output
```

## Jupyter Notebook

```bash
jupyter notebook Chandra_OCR_Vietnamese_Exploration.ipynb
```
