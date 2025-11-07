# speedtune

Lightweight helpers to "patch" token embeddings for causal and seq2seq
transformer models. Grouping tokens into fixed-size patches reduces the
effective sequence length and can speed up training or inference for long
inputs. The project provides a thin wrapper around Hugging Face
transformers models that computes patch-level embeddings and forwards them to
the base model while preserving a compatible `forward` API.

## Features

- Compress token embeddings into patches (mean pooling by default).
- Forward patched embeddings to causal LMs and seq2seq LMs (seq2seq implementation pending).
- Optional user-provided patch function for custom aggregation.

## Quick install

This package requires PyTorch and Hugging Face Transformers. Because PyTorch
is platform-specific (CPU vs GPU/CUDA), install it first following the
official instructions for your platform, then install this package.

Example (Windows PowerShell):

```powershell
# create venv and activate
python -m venv .venv; .\.venv\Scripts\Activate.ps1

# Install PyTorch for your platform first. Example CPU-only wheel:
pip install "torch>=2.0.0" --index-url https://download.pytorch.org/whl/cpu

# Then install transformers and this package
pip install "transformers>=4.30.0"
pip install -U pip build wheel twine

# Build and install the local wheel for development/testing
python -m build
pip install dist\speedtune-0.1.1py3-none-any.whl
```

## Minimal usage example

```python
import torch
from speedtune.speedtune import AutoPatchModelForCausalLM

# Create wrapper around a pretrained model (small model for quick tests)
model = AutoPatchModelForCausalLM.from_pretrained("gpt2", patch_size=2)
model.eval()

input_ids = torch.tensor([[50256, 50257, 50258, 50259]])  # example token ids
outputs = model(input_ids=input_ids)
logits = outputs.logits
```

## Testing

Run the unit tests with `pytest` after installing test dependencies:

```powershell
# from the repo root
pip install pytest
pytest -q
```

## License

This project is MIT licensed (see `LICENSE`).
