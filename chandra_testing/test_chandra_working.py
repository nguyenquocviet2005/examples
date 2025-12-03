#!/usr/bin/env python3
"""
✅ Working Chandra Test Script - For 8GB GPU
Uses the ACTUAL Chandra API with proper Vietnamese support
"""

import os
import sys
from pathlib import Path
from typing import Optional
import logging

# Set GPU memory optimization BEFORE importing torch
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
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def process_vietnamese_ocr(
    image_path: str,
    output_dir: str = "./chandra_output"
) -> Optional[dict]:
    """
    Process Vietnamese OCR with Chandra using proper API.
    
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
        print("🚀 Chandra Vietnamese OCR - Proper API Version")
        print("="*60)
        
        print(f"\n📸 Image: {image_file.name}")
        print(f"📁 Output: {output_path.absolute()}")
        
        # Step 1: Initialize InferenceManager (the correct way!)
        print("\n[1/4] Initializing InferenceManager...")
        manager = InferenceManager(method='hf')
        print("✅ InferenceManager ready")
        
        # Step 2: Load image
        print("\n[2/4] Loading image...")
        image = load_image(str(image_file))
        print(f"✅ Image loaded: {image.size}")
        
        # Step 3: Create batch input (proper format)
        print("\n[3/4] Preparing batch input...")
        batch_item = BatchInputItem(
            image=image,
            prompt=None,  # Use default OCR layout prompt
            prompt_type='ocr_layout'
        )
        print("✅ Batch item created")
        
        # Step 4: Run inference
        print("\n[4/4] Running OCR inference...")
        print("⏳ This may take 30-60 seconds on first run (model downloading)...")
        
        results = manager.generate([batch_item])
        result = results[0]
        
        print("✅ OCR complete!")
        
        # Extract results
        markdown_text = result.markdown
        html_output = result.html
        token_count = result.token_count
        
        print("\n" + "-"*60)
        print("📊 Results:")
        print("-"*60)
        print(f"Tokens used: {token_count}")
        print(f"Output characters: {len(markdown_text)}")
        
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
            'image_size': image.size
        }
        
    except RuntimeError as e:
        if "out of memory" in str(e).lower():
            logger.error("❌ Out of memory! Your GPU is too small.")
            print("\nSuggested solutions:")
            print("1. Use CPU instead:")
            print("   export TORCH_DEVICE=cpu")
            print("\n2. Use vLLM server (optimized):")
            print("   pip install vllm")
            print("   chandra_vllm  # in one terminal")
            print("\n3. Use hosted service:")
            print("   https://www.datalab.to/playground")
            return None
        else:
            logger.error(f"❌ Runtime error: {e}")
            return None
    except Exception as e:
        logger.error(f"❌ Error: {e}", exc_info=True)
        return None


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python test_chandra_working.py <image_path> [output_dir]")
        print("\nExample:")
        print("  python test_chandra_working.py assets/examples/test1.jpg")
        print("  python test_chandra_working.py assets/examples/test1.jpg ./my_output")
        sys.exit(1)
    
    image_path = sys.argv[1]
    output_dir = sys.argv[2] if len(sys.argv) > 2 else "./chandra_output"
    
    result = process_vietnamese_ocr(image_path, output_dir)
    
    if result is None:
        sys.exit(1)
    
    print("\n✅ All operations completed successfully!")
