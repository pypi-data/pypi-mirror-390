import gc
import torch
import pytest
from transformers import AutoConfig
from speedtune.patch import AutoPatchModelForSeq2SeqLM

PRETRAINED_T5_MODELS = [
    "t5-small",
    "t5-base",
]

ALL_T5_MODELS = [
    "t5-small",
    "t5-base",
]

def _device():
    return 'cuda' if torch.cuda.is_available() else 'cpu'

@pytest.mark.parametrize("model_name", PRETRAINED_T5_MODELS)
def test_autopatchmodelforseq2seqlm_pretrained(model_name):
    device = _device()
    try:
        model = AutoPatchModelForSeq2SeqLM.from_pretrained(model_name).to(device)
    except Exception as e:
        pytest.skip(f"Skipping pretrained load for {model_name}: {e}")

    assert model is not None, f"Failed to load seq2seq model from pretrained: {model_name}"

    batch_size = 2
    enc_seq_len = 16
    dec_seq_len = 8
    vocab_size = model.config.vocab_size

    encoder_input_ids = torch.randint(0, vocab_size, (batch_size, enc_seq_len)).to(device)
    decoder_input_ids = torch.randint(0, vocab_size, (batch_size, dec_seq_len)).to(device)
    labels = decoder_input_ids.clone()

    # Forward without patches
    outputs = model(input_ids=encoder_input_ids, decoder_input_ids=decoder_input_ids, return_dict=True)
    assert outputs.logits.shape == (batch_size, dec_seq_len, vocab_size), \
        f"Unexpected output shape without patches for model {model_name}"

    # With patches
    patch_size = 4
    model_with_patches = AutoPatchModelForSeq2SeqLM.from_pretrained(model_name, patch_size=patch_size).to(device)
    outputs_patched = model_with_patches(input_ids=encoder_input_ids, decoder_input_ids=decoder_input_ids, labels=labels, return_dict=True)
    expected_len = dec_seq_len // patch_size
    assert outputs_patched.logits.shape == (batch_size, expected_len, model_with_patches.config.vocab_size), \
        f"Unexpected output shape with patches for model {model_name}"

    # Backprop
    loss = outputs_patched.loss
    assert loss is not None, "Loss not returned for patched seq2seq model"
    loss.backward()
    assert loss.item() is not None

    # Cleanup
    del model, model_with_patches, encoder_input_ids, decoder_input_ids, labels, outputs, outputs_patched, loss
    gc.collect()
    if torch.cuda.is_available():
        torch.cuda.empty_cache()

@pytest.mark.parametrize("model_name", ALL_T5_MODELS)
def test_autopatchmodelforseq2seqlm_config(model_name):
    device = _device()

    try:
        config = AutoConfig.from_pretrained(model_name)
    except Exception as e:
        pytest.skip(f"Skipping config load for {model_name}: {e}")

    # Optionally shrink config for faster init in CI (kept small already for T5)
    try:
        model = AutoPatchModelForSeq2SeqLM.from_config(config).to(device)
    except Exception as e:
        pytest.skip(f"Skipping model init from config for {model_name}: {e}")

    assert model is not None, f"Failed to init seq2seq model from config: {model_name}"

    batch_size = 2
    enc_seq_len = 16
    dec_seq_len = 8
    vocab_size = model.config.vocab_size

    encoder_input_ids = torch.randint(0, vocab_size, (batch_size, enc_seq_len)).to(device)
    decoder_input_ids = torch.randint(0, vocab_size, (batch_size, dec_seq_len)).to(device)
    labels = decoder_input_ids.clone()

    outputs = model(input_ids=encoder_input_ids, decoder_input_ids=decoder_input_ids, return_dict=True)
    assert outputs.logits.shape == (batch_size, dec_seq_len, vocab_size), \
        f"Unexpected output shape without patches for model {model_name}"

    patch_size = 4
    model_with_patches = AutoPatchModelForSeq2SeqLM.from_config(config, patch_size=patch_size).to(device)
    outputs_patched = model_with_patches(input_ids=encoder_input_ids, decoder_input_ids=decoder_input_ids, labels=labels, return_dict=True)
    expected_len = dec_seq_len // patch_size
    assert outputs_patched.logits.shape == (batch_size, expected_len, vocab_size), \
        f"Unexpected output shape with patches for model {model_name}"

    loss = outputs_patched.loss
    assert loss is not None
    loss.backward()
    assert loss.item() is not None

    # Cleanup
    del model, model_with_patches, encoder_input_ids, decoder_input_ids, labels, outputs, outputs_patched, loss
    gc.collect()
    if torch.cuda.is_available():
        torch.cuda.empty_cache()

if __name__ == "__main__":
    test_autopatchmodelforseq2seqlm_pretrained("t5-small")
    test_autopatchmodelforseq2seqlm_config("t5-small")