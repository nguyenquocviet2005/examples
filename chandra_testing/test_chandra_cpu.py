#!/usr/bin/env python3
"""
✅ Working Chandra Test Script - CPU Mode for 8GB GPU
Uses CPU to avoid GPU memory limitations
Processing: ~45-60 seconds per image (vs 30 seconds on GPU)
"""

import os
import sys
from pathlib import Path
from typing import Optional
import logging
import time

# Set device to CPU BEFORE importing torch
os.environ['TORCH_DEVICE'] = 'cpu'
os.environ['PYTORCH_ALLOC_CONF'] = 'expandable_segments:True'

try:
    from PIL import Image
    from chandra.model import InferenceManager
    from chandra.model.schema import BatchInputItem
    from chandra.input import load_image
except ImportError as e:
    print(f"❌ Import Error: {e}")
    print("\nMake sure Chandra is installed:")
    print("  pip install chandra-ocr")
    sys.exit(1)

# Configure logging
logging.basicConfig(level=logging.WARNING)  # Reduce verbosity
logger = logging.getLogger(__name__)


def process_vietnamese_ocr_cpu(
    image_path: str,
    output_dir: str = "./chandra_output"
) -> Optional[dict]:
    """
    Process Vietnamese OCR with Chandra using CPU mode.
    
    ⚠️  This is SLOW but works on any hardware!
    Processing time: 45-60 seconds per image
    
    Args:
        image_path: Path to the image file
        output_dir: Directory to save results
        
    Returns:
        Dictionary with OCR results or None on error
    """
    # Validate input
    image_file = Path(image_path)
    if not image_file.exists():
        logger.error(f"❌ Image not found: {image_path}")
        return None
    
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    try:
        print("\n" + "="*60)
        print("🚀 Chandra Vietnamese OCR - CPU Mode")
        print("="*60)
        print("⏳ WARNING: Using CPU (slow but reliable)")
        print("   Expected time: 45-60 seconds per image\n")
        
        print(f"📸 Image: {image_file.name}")
        print(f"📁 Output: {output_path.absolute()}")
        
        # Step 1: Initialize InferenceManager on CPU
        print("\n[1/4] Initializing InferenceManager (CPU mode)...")
        start_time = time.time()
        manager = InferenceManager(method='hf')
        elapsed = time.time() - start_time
        print(f"✅ InferenceManager ready ({elapsed:.1f}s)")
        
        # Step 2: Load image
        print("\n[2/4] Loading image...")
        image = load_image(str(image_file))
        print(f"✅ Image loaded: {image.size}")
        
        # Step 3: Create batch input
        print("\n[3/4] Preparing batch input...")
        batch_item = BatchInputItem(
            image=image,
            prompt=None,
            prompt_type='ocr_layout'
        )
        print("✅ Batch item created")
        
        # Step 4: Run inference on CPU
        print("\n[4/4] Running OCR inference on CPU...")
        print("⏳ Processing (this will take 45-60 seconds)...")
        
        start_time = time.time()
        results = manager.generate([batch_item])
        elapsed = time.time() - start_time
        
        result = results[0]
        print(f"✅ OCR complete! ({elapsed:.1f}s)")
        
        # Extract results
        markdown_text = result.markdown
        html_output = result.html
        token_count = result.token_count
        
        print("\n" + "-"*60)
        print("📊 Results:")
        print("-"*60)
        print(f"Tokens used: {token_count}")
        print(f"Output characters: {len(markdown_text)}")
        print(f"Processing time: {elapsed:.1f} seconds")
        
        # Save outputs
        output_files = {}
        
        # Save markdown
        md_file = output_path / f"{image_file.stem}.md"
        md_file.write_text(markdown_text, encoding='utf-8')
        output_files['markdown'] = str(md_file)
        print(f"\n💾 Markdown saved: {md_file}")
        
        # Save HTML
        html_file = output_path / f"{image_file.stem}.html"
        html_file.write_text(html_output, encoding='utf-8')
        output_files['html'] = str(html_file)
        print(f"💾 HTML saved: {html_file}")
        
        # Print preview
        print("\n" + "-"*60)
        print("📄 Text Preview (first 500 chars):")
        print("-"*60)
        preview = markdown_text[:500]
        print(preview)
        if len(markdown_text) > 500:
            print(f"\n... ({len(markdown_text) - 500} more characters)")
        
        print("\n" + "="*60)
        print("✅ SUCCESS! Vietnamese OCR complete")
        print("="*60)
        
        return {
            'markdown': markdown_text,
            'html': html_output,
            'token_count': token_count,
            'output_files': output_files,
            'image_size': image.size,
            'processing_time': elapsed
        }
        
    except Exception as e:
        logger.error(f"❌ Error: {e}", exc_info=True)
        print(f"\n❌ Error: {e}")
        return None


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python test_chandra_cpu.py <image_path> [output_dir]")
        print("\nExample:")
        print("  python test_chandra_cpu.py assets/examples/test1.jpg")
        print("  python test_chandra_cpu.py assets/examples/test1.jpg ./my_output")
        print("\nNote: Processing time is ~45-60 seconds per image on CPU")
        sys.exit(1)
    
    image_path = sys.argv[1]
    output_dir = sys.argv[2] if len(sys.argv) > 2 else "./chandra_output"
    
    result = process_vietnamese_ocr_cpu(image_path, output_dir)
    
    if result is None:
        print("\n❌ Processing failed")
        sys.exit(1)
    
    print("\n✅ All operations completed successfully!")
