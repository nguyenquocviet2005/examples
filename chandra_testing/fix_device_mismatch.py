"""
This script fixes the device mismatch issue in chandra OCR.
The problem: inputs are hardcoded to CUDA but model might be on CPU.
The solution: Move inputs to the same device as the model.
"""

# Read the original hf.py
hf_path = ".venv/lib/python3.13/site-packages/chandra/model/hf.py"

with open(hf_path, 'r') as f:
    content = f.read()

# The fix: Replace hardcoded cuda with device-aware code
old_code = '''    inputs = model.processor(
        text=text,
        images=image_inputs,
        padding=True,
        return_tensors="pt",
        padding_side="left",
    )
    inputs = inputs.to("cuda")'''

new_code = '''    inputs = model.processor(
        text=text,
        images=image_inputs,
        padding=True,
        return_tensors="pt",
        padding_side="left",
    )
    # Move inputs to the same device as the model
    model_device = next(model.parameters()).device
    inputs = inputs.to(model_device)'''

if old_code in content:
    content = content.replace(old_code, new_code)
    with open(hf_path, 'w') as f:
        f.write(content)
    print("✓ Fixed device mismatch in chandra/model/hf.py")
    print("  Changed: inputs.to('cuda') → inputs.to(model_device)")
else:
    print("✗ Could not find the code to patch")
    print("  This might mean the version has changed")
