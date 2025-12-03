#!/usr/bin/env python3
"""
Chandra OCR with device mismatch fix.

This script applies a device-aware wrapper to handle GPU/CPU placement issues.
When the model is loaded on one device but inputs are expected on another,
this script ensures they're on the same device.
"""

import os
import sys
from pathlib import Path
from typing import List

# Patch chandra to use device-aware inference
from chandra.model.schema import BatchInputItem, GenerationResult
from chandra.model.util import scale_to_fit
from chandra.prompts import PROMPT_MAPPING
from chandra.settings import settings

from qwen_vl_utils import process_vision_info
from transformers import Qwen3VLForConditionalGeneration, Qwen3VLProcessor


def generate_hf_fixed(
    batch: List[BatchInputItem], model, max_output_tokens=None, **kwargs
) -> List[GenerationResult]:
    """Fixed version of generate_hf that handles device placement correctly."""
    
    if max_output_tokens is None:
        max_output_tokens = settings.MAX_OUTPUT_TOKENS

    # Get model device
    model_device = next(model.parameters()).device
    print(f"📍 Model device: {model_device}")

    messages = [process_batch_element(item, model.processor) for item in batch]
    text = model.processor.apply_chat_template(
        messages, tokenize=False, add_generation_prompt=True
    )

    image_inputs, _ = process_vision_info(messages)
    inputs = model.processor(
        text=text,
        images=image_inputs,
        padding=True,
        return_tensors="pt",
        padding_side="left",
    )
    
    # FIX: Move inputs to the SAME device as the model
    inputs = inputs.to(model_device)
    print(f"✓ Moved inputs to {model_device}")

    # Inference: Generation of the output
    generated_ids = model.generate(**inputs, max_new_tokens=max_output_tokens)
    generated_ids_trimmed = [
        out_ids[len(in_ids) :]
        for in_ids, out_ids in zip(inputs.input_ids, generated_ids)
    ]
    output_text = model.processor.batch_decode(
        generated_ids_trimmed,
        skip_special_tokens=True,
        clean_up_tokenization_spaces=False,
    )
    results = [
        GenerationResult(raw=out, token_count=len(ids), error=False)
        for out, ids in zip(output_text, generated_ids_trimmed)
    ]
    return results


def process_batch_element(item: BatchInputItem, processor):
    """Process a single batch element."""
    prompt = item.prompt
    prompt_type = item.prompt_type

    if not prompt:
        prompt = PROMPT_MAPPING[prompt_type]

    content = []
    image = scale_to_fit(item.image)  # Guarantee max size
    content.append({"type": "image", "image": image})

    content.append({"type": "text", "text": prompt})
    message = {"role": "user", "content": content}
    return message


def load_model():
    """Load Chandra model with proper device handling."""
    import torch
    
    device_map = "auto"
    if settings.TORCH_DEVICE:
        device_map = {"": settings.TORCH_DEVICE}

    kwargs = {
        "dtype": settings.TORCH_DTYPE,
        "device_map": device_map,
    }
    if settings.TORCH_ATTN:
        kwargs["attn_implementation"] = settings.TORCH_ATTN

    print("📥 Loading Chandra model...")
    model = Qwen3VLForConditionalGeneration.from_pretrained(
        settings.MODEL_CHECKPOINT, **kwargs
    )
    model = model.eval()
    processor = Qwen3VLProcessor.from_pretrained(settings.MODEL_CHECKPOINT)
    model.processor = processor
    
    # Verify model device
    model_device = next(model.parameters()).device
    print(f"✓ Model loaded on device: {model_device}")
    
    return model


def run_ocr(image_path: str, output_dir: str = None, prompt_type: str = "ocr"):
    """Run OCR on an image with device-aware inference."""
    from PIL import Image
    from chandra.output import parse_markdown
    
    if output_dir is None:
        output_dir = "./output"
    
    # Create output directory
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    
    # Load image
    print(f"\n📂 Loading image: {image_path}")
    image = Image.open(image_path).convert("RGB")
    
    # Load model
    model = load_model()
    
    # Prepare batch
    item = BatchInputItem(image=image, prompt_type=prompt_type)
    batch = [item]
    
    # Run inference with fixed device handling
    print(f"\n🔄 Running OCR inference (mode: {prompt_type})...")
    results = generate_hf_fixed(batch, model, max_output_tokens=settings.MAX_OUTPUT_TOKENS)
    
    # Process results
    result = results[0]
    if result.error:
        print(f"❌ Error: {result.error}")
        return
    
    print(f"✓ OCR completed successfully")
    print(f"📄 Tokens: {result.token_count}")
    
    # Save markdown output
    markdown_text = result.raw
    md_path = os.path.join(output_dir, f"{Path(image_path).stem}.md")
    with open(md_path, 'w', encoding='utf-8') as f:
        f.write(markdown_text)
    print(f"✓ Markdown saved to: {md_path}")
    
    # Parse and save HTML
    try:
        html_content = parse_markdown(markdown_text)
        html_path = os.path.join(output_dir, f"{Path(image_path).stem}.html")
        with open(html_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
        print(f"✓ HTML saved to: {html_path}")
    except Exception as e:
        print(f"⚠ Could not generate HTML: {e}")
    
    print(f"\n✅ OCR complete! Results saved to: {output_dir}")
    return result


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Chandra OCR with device fix")
    parser.add_argument("image_path", help="Path to image file")
    parser.add_argument("--output", "-o", default="./output", help="Output directory")
    parser.add_argument("--mode", "-m", default="ocr", choices=["ocr", "ocr_layout"], 
                       help="OCR mode")
    
    args = parser.parse_args()
    
    try:
        run_ocr(args.image_path, args.output, args.mode)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
