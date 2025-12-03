#!/usr/bin/env python3
"""
Test Chandra with Qwen2-VL 2B lightweight model
This is a drop-in replacement that uses 6GB VRAM instead of 16GB+
"""

import os
import sys
from pathlib import Path

# ============================================================================
# MEMORY OPTIMIZATION
# ============================================================================
# Enable memory fragmentation fix BEFORE importing torch
os.environ['PYTORCH_CUDA_ALLOC_CONF'] = 'expandable_segments:True'

# Switch to lightweight model
os.environ['MODEL_CHECKPOINT'] = 'Qwen/Qwen2-VL-2B-Instruct'

# Optional: Use float16 for extra memory savings (may affect accuracy slightly)
# os.environ['TORCH_DTYPE'] = 'float16'

# ============================================================================
# IMPORTS
# ============================================================================
import torch
import argparse
from typing import Optional
import time

def check_gpu():
    """Check GPU availability and memory"""
    if torch.cuda.is_available():
        print(f"✓ CUDA available: {torch.cuda.get_device_name(0)}")
        print(f"  Total VRAM: {torch.cuda.get_device_properties(0).total_memory / 1e9:.1f} GB")
        print(f"  Free VRAM: {torch.cuda.mem_get_info()[0] / 1e9:.1f} GB")
    else:
        print("⚠ CUDA not available, will use CPU (very slow)")
    print()

def load_model():
    """Load Qwen2-VL 2B model using InferenceManager"""
    print("Loading Qwen2-VL 2B model (6GB VRAM required)...")
    start_time = time.time()
    
    try:
        # Import after environment variables are set
        from chandra.model import InferenceManager
        
        # Initialize InferenceManager with HuggingFace method
        # MODEL_CHECKPOINT env var is automatically picked up by settings
        manager = InferenceManager(method='hf')
        
        elapsed = time.time() - start_time
        print(f"✓ Model loaded in {elapsed:.1f}s")
        
        # Check memory after loading
        if torch.cuda.is_available():
            used = (torch.cuda.get_device_properties(0).total_memory - torch.cuda.mem_get_info()[1]) / 1e9
            print(f"  VRAM used: {used:.1f} GB")
        
        return manager
    except Exception as e:
        print(f"✗ Error loading model: {e}")
        if "CUDA out of memory" in str(e):
            print("\n  💡 Tips to reduce VRAM:")
            print("     1. Close other GPU applications")
            print("     2. Use CPU mode: export TORCH_DEVICE=cpu")
            print("     3. Try PaddleOCR instead (uses <1GB)")
        sys.exit(1)

def process_image(manager, image_path: str, output_dir: Optional[str] = None) -> dict:
    """Process a single image with OCR using InferenceManager"""
    from PIL import Image
    from chandra.input import load_image
    from chandra.model.schema import BatchInputItem
    from chandra.prompts import PROMPT_MAPPING
    
    image_path = Path(image_path)
    
    if not image_path.exists():
        print(f"✗ Image not found: {image_path}")
        return None
    
    print(f"\nProcessing: {image_path.name}")
    print("-" * 60)
    
    start_time = time.time()
    
    try:
        # Load image
        image = load_image(str(image_path))
        
        # Create batch input with OCR layout prompt
        batch_item = BatchInputItem(
            image=image,
            prompt=None,  # Will use default prompt
            prompt_type='ocr_layout'  # Use layout-preserving OCR
        )
        
        # Run inference
        results = manager.generate([batch_item])
        result = results[0]
        
        elapsed = time.time() - start_time
        
        # Extract text from markdown output
        text = result.markdown
        token_count = result.token_count
        
        # Print results
        print(f"✓ Processing completed in {elapsed:.1f}s")
        print(f"  Text extracted: {len(text)} characters")
        print(f"  Token count: {token_count}")
        
        # Show preview
        preview = text[:300].replace('\n', ' ').strip()
        print(f"  Preview: {preview}...")
        
        # Check for Vietnamese characters
        vietnamese_chars = set('àáảãạăằắẳẵặâầấẩẫậèéẻẽẹêềếểễệìíỉĩịòóỏõọôồốổỗộơờớởỡợùúủũụưừứửữựỳýỷỹỵđ'
                                'ÀÁẢÃẠĂẰẮẲẴẶÂẦẤẨẪẬÈÉẺẼẸÊỀẾ ểễệìíỉĩịòóỏõọôồốổỗộơờớởỡợùúủũụưừứửữựỳýỷỹỵđ')
        has_vietnamese = any(c in vietnamese_chars for c in text)
        print(f"  Vietnamese text detected: {'Yes ✓' if has_vietnamese else 'No'}")
        
        # Save output if requested
        if output_dir:
            output_path = Path(output_dir) / f"{image_path.stem}.md"
            output_path.parent.mkdir(parents=True, exist_ok=True)
            output_path.write_text(text)
            print(f"  Saved to: {output_path}")
        
        # Check GPU memory after processing
        if torch.cuda.is_available():
            used = (torch.cuda.get_device_properties(0).total_memory - torch.cuda.mem_get_info()[1]) / 1e9
            free = torch.cuda.mem_get_info()[0] / 1e9
            print(f"  GPU Memory - Used: {used:.1f}GB, Free: {free:.1f}GB")
        
        return {
            'image': str(image_path),
            'success': True,
            'text_length': len(text),
            'token_count': token_count,
            'has_vietnamese': has_vietnamese,
            'processing_time': elapsed,
        }
        
    except Exception as e:
        elapsed = time.time() - start_time
        print(f"✗ Error processing image: {e}")
        return {
            'image': str(image_path),
            'success': False,
            'error': str(e),
            'processing_time': elapsed,
        }

def main():
    parser = argparse.ArgumentParser(
        description='Test Chandra OCR with Qwen2-VL 2B lightweight model (Vietnamese support)',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Single image
  python test_qwen2vl.py assets/examples/test1.jpg
  
  # Multiple images with output directory
  python test_qwen2vl.py assets/examples/*.jpg --output ./ocr_results
  
  # Single image with memory monitoring
  python test_qwen2vl.py assets/examples/test1.jpg --monitor
        """
    )
    
    parser.add_argument('images', nargs='+', help='Image file(s) or glob pattern(s)')
    parser.add_argument('--output', '-o', help='Output directory for results')
    parser.add_argument('--monitor', action='store_true', help='Print memory usage details')
    parser.add_argument('--cpu', action='store_true', help='Force CPU mode (very slow)')
    
    args = parser.parse_args()
    
    # Handle CPU mode
    if args.cpu:
        os.environ['TORCH_DEVICE'] = 'cpu'
        print("⚠ Using CPU mode (will be very slow)")
    
    # Print header
    print("=" * 60)
    print("Chandra OCR with Qwen2-VL 2B Lightweight Model")
    print("=" * 60)
    print()
    
    # Check GPU
    check_gpu()
    
    # Expand glob patterns
    image_files = []
    for pattern in args.images:
        matching = list(Path('.').glob(pattern))
        if matching:
            image_files.extend(matching)
        else:
            image_files.append(Path(pattern))
    
    if not image_files:
        print("✗ No images found")
        sys.exit(1)
    
    print(f"Found {len(image_files)} image(s) to process\n")
    
    # Load model once
    manager = load_model()
    
    # Process all images
    results = []
    for image_path in image_files:
        result = process_image(manager, str(image_path), args.output)
        if result:
            results.append(result)
    
    # Summary
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    successful = sum(1 for r in results if r.get('success', False))
    print(f"Processed: {successful}/{len(results)} images successfully")
    
    if successful > 0:
        total_time = sum(r['processing_time'] for r in results if r.get('success'))
        avg_time = total_time / successful
        print(f"Total time: {total_time:.1f}s")
        print(f"Average time per image: {avg_time:.1f}s")
        
        with_vietnamese = sum(1 for r in results if r.get('has_vietnamese'))
        print(f"Vietnamese text detected: {with_vietnamese}/{successful} images")
    
    if args.output:
        print(f"\n✓ Results saved to: {args.output}")

if __name__ == '__main__':
    main()
