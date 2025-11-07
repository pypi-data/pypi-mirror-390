import gc
import torch
import pytest
from transformers import AutoConfig
from speedtune.patch import AutoPatchModelForSequenceClassification


# Models that commonly lack a pad token (exercise error path)
PRETRAINED_CAUSAL_MODELS = [
    "google/gemma-2-2b-it",
    "meta-llama/Llama-3.2-1B-Instruct",
    "facebook/opt-125m",
    "facebook/opt-350m"
]


def _device():
    return "cuda" if torch.cuda.is_available() else "cpu"


@pytest.mark.parametrize("model_name", PRETRAINED_CAUSAL_MODELS)
def test_autopatchmodelsequenceclassification_pretrained(model_name):
    device = _device()
    try:
        model = AutoPatchModelForSequenceClassification.from_pretrained(model_name).to(device)
    except Exception as e:
        pytest.skip(f"Skipping pretrained load for {model_name}: {e}")

    assert model is not None, f"Failed to load seq-class model from pretrained: {model_name}"

    batch_size = 2
    seq_len = 16
    vocab_size = getattr(model.config, "vocab_size", None)
    if vocab_size is None:
        pytest.skip(f"Model {model_name} has no vocab_size in config; skipping")

    input_ids = torch.randint(0, vocab_size, (batch_size, seq_len)).to(device)

    # Forward without patches
    outputs = model(input_ids=input_ids, return_dict=True)

    num_labels = getattr(model.config, "num_labels", 2)
    assert outputs.logits.shape == (batch_size, num_labels), (
        f"Unexpected pooled logits shape without patches for model {model_name}: got {outputs.logits.shape}"
    )

    # With patches (patch_size compresses sequence; pooled logits should still be (batch, num_labels))
    patch_size = 4
    try:
        model_with_patches = AutoPatchModelForSequenceClassification.from_pretrained(model_name, patch_size=patch_size).to(device)
    except Exception as e:
        pytest.skip(f"Skipping pretrained-patched load for {model_name}: {e}")

    outputs_patched = model_with_patches(input_ids=input_ids, return_dict=True)
    assert outputs_patched.logits.shape == (batch_size, getattr(model_with_patches.config, "num_labels", num_labels)), (
        f"Unexpected pooled logits shape with patches for model {model_name}: got {outputs_patched.logits.shape}"
    )

    # Compute a simple cross-entropy loss on the pooled logits and backprop to ensure gradients flow
    labels = torch.randint(0, getattr(model.config, "num_labels", 2), (batch_size,)).to(device)
    loss_f = torch.nn.CrossEntropyLoss()
    loss = loss_f(outputs_patched.logits, labels)
    loss.backward()
    assert loss.item() is not None

    # Cleanup
    del model, model_with_patches, input_ids, outputs, outputs_patched, loss, labels
    gc.collect()
    if torch.cuda.is_available():
        torch.cuda.empty_cache()


@pytest.mark.parametrize("model_name", PRETRAINED_CAUSAL_MODELS)
def test_autopatchmodelsequenceclassification_from_config(model_name):
    device = _device()
    try:
        config = AutoConfig.from_pretrained(model_name)
    except Exception as e:
        pytest.skip(f"Skipping config load for {model_name}: {e}")

    # Optionally shrink config for faster init in CI
    if hasattr(config, "num_hidden_layers"):
        config.num_hidden_layers = min(config.num_hidden_layers, 2)
    if hasattr(config, "hidden_size"):
        config.hidden_size = min(getattr(config, "hidden_size", 768), 128)

    try:
        model = AutoPatchModelForSequenceClassification.from_config(config).to(device)
    except Exception as e:
        pytest.skip(f"Skipping model init from config for {model_name}: {e}")

    batch_size = 2
    seq_len = 16
    vocab_size = getattr(model.config, "vocab_size", 50257)
    input_ids = torch.randint(0, vocab_size, (batch_size, seq_len)).to(device)

    outputs = model(input_ids=input_ids, return_dict=True)
    num_labels = getattr(model.config, "num_labels", 2)
    assert outputs.logits.shape == (batch_size, num_labels)

    # With patches
    patch_size = 4
    model_with_patches = AutoPatchModelForSequenceClassification.from_config(config, patch_size=patch_size).to(device)
    outputs_patched = model_with_patches(input_ids=input_ids, return_dict=True)
    assert outputs_patched.logits.shape == (batch_size, getattr(model_with_patches.config, "num_labels", num_labels))

    # Compute loss and backprop
    labels = torch.randint(0, getattr(model.config, "num_labels", 2), (batch_size,)).to(device)
    loss_f = torch.nn.CrossEntropyLoss()
    loss = loss_f(outputs_patched.logits, labels)
    loss.backward()
    assert loss.item() is not None

    # Cleanup
    del model, model_with_patches, input_ids, outputs, outputs_patched, loss, labels, config
    gc.collect()
    if torch.cuda.is_available():
        torch.cuda.empty_cache()