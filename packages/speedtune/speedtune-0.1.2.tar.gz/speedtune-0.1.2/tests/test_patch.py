import torch
import torch.nn as nn
from speedtune.patch import AutoPatchModelForCausalLM
import pytest
from transformers import AutoConfig
import gc # Import the garbage collection module

"""
Test suite for the patching module.
For AutoPatchModelForCausalLM, we will do the following:

1. Test initialization from pretrained for the following models:
   - gpt2
   - distilgpt2
   - facebook/opt-125m
   - facebook/opt-350m

2. Test initialization from config for all of following models:
   - apertus, arcee, aria_text, bamba, bart, bert, bert-generation, big_bird, bigbird_pegasus, biogpt, bitnet, blenderbot, blenderbot-small, bloom, blt, camembert, code_llama, codegen, cohere, cohere2, cpmant, ctrl, cwm, data2vec-text, dbrx, deepseek_v2, deepseek_v3, diffllama, doge, dots1, electra, ernie, ernie4_5, ernie4_5_moe, exaone4, falcon, falcon_h1, falcon_mamba, flex_olmo, gemma, gemma2, gemma3_text, gemma3n_text, glm, glm4, glm4_moe, gpt-sw3, gpt2, gpt_bigcode, gpt_neo, gpt_neox, gpt_neox_japanese, gpt_oss, gptj, granite, granitemoe, granitemoehybrid, granitemoeshared, helium, hunyuan_v1_dense, hunyuan_v1_moe, jamba, jetmoe, lfm2, lfm2_moe, llama, llama4, llama4_text, longcat_flash, mamba, mamba2, marian, mbart, mega, megatron-bert, minimax, ministral, mistral, mixtral, mllama, modernbert-decoder, moshi, mpt, mvp, nemotron, olmo, olmo2, olmo3, olmoe, open-llama, openai-gpt, opt, pegasus, persimmon, phi, phi3, phimoe, plbart, prophetnet, qdqbert, qwen2, qwen2_moe, qwen3, qwen3_moe, qwen3_next, recurrent_gemma, reformer, rembert, roberta, roberta-prelayernorm, roc_bert, roformer, rwkv, seed_oss, smollm3, stablelm, starcoder2, transfo-xl, vaultgemma, xglm, xlm, xlm-prophetnet, xlm-roberta, xlm-roberta-xl, xlnet, xlstm, xmod, zamba, zamba2
   - We modify the config such that each model has a maximum of 1B parameters to keep the tests lightweight.

3. For each of the above models, we will test the patching functionality by:
   - Creating random input data
   - Passing the data through the model with and without patches
   - Ensuring the output shapes are as expected
   - Ensuring that backpropagation works without errors
"""
PRETRAINED_TEST_MODELS = [
    "gpt2",
    "distilgpt2",
    "facebook/opt-125m",
    "facebook/opt-350m"
]

# ALL_MODELS = [
#     "google/bigbird-roberta-base",
#     "microsoft/BioGPT",
#     "1bitLLM/bitnet_b1_58-3B", 
#     "facebook/blenderbot-3B",
#     "facebook/blenderbot_small-90M",
#     "bigscience/bloom-560m",
#     "facebook/blt-1b",
#     "codellama/CodeLlama-7b-hf",
#     "Salesforce/codegen-350M-mono",
#     "openbmb/cpm-ant-10b",
#     "deepseek-ai/deepseek-llm-7b-base",
#     "google/electra-small-discriminator",
#     "LGAI-EXAONE/EXAONE-4.0-1.2B",
#     "tiiuae/falcon-7b",
#     "tiiuae/Falcon-H1-1.5B-Deep-Instruct",
#     "tiiuae/falcon-mamba-7b",
#     "allenai/OLMo-1B",
#     "google/gemma-2b",
#     "google/gemma-2-2b",
#     "google/gemma-3-270m",
#     "gpt2",
#     "EleutherAI/gpt-neo-125m",
#     "rinna/japanese-gpt-neox-3.6b",
#     "kyutai/helium-1-2b",
#     "jetmoe/jetmoe-8B",
#     "meta-llama/Llama-2-7b-hf",
#     "meta-llama/Llama-3.1-8B-Instruct",
#     "meta-llama/Llama-3.2-1B",
#     "mistralai/Ministral-8B-Instruct-2410",
#     "mistralai/Mistral-7B-v0.1",
#     "mistralai/Mixtral-8x7B-v0.1",
#     "mosaicml/mpt-7b",
#     "google/pegasus-large",
#     "adept/persimmon-8b-base",
#     "microsoft/phi-2",
#     "microsoft/Phi-3-mini-4k-instruct",
#     "Qwen/Qwen2.5-3B-Instruct",
#     "HuggingFaceTB/SmolLM3-3B",
#     "stabilityai/stablelm-2-1_6b",
#     "bigcode/starcoder2-3b",
#     "facebook/xglm-1.7B",
#     "xlm-roberta-base",
#     "Zyphra/Zamba2-1.2B"
# ]

def modify_config_for_testing(config):
    """Modify the model config to ensure the model has at most 1B parameters.

    Args:
        config: The model configuration object.

    Returns:
        Modified configuration object.
    """
    if hasattr(config, 'n_layer'):
        config.n_layer = min(config.n_layer, 12)
    if hasattr(config, 'n_head'):
        config.n_head = min(config.n_head, 12)
    if hasattr(config, 'n_embd'):
        config.n_embd = min(config.n_embd, 768)
    if hasattr(config, 'd_model'):
        config.d_model = min(config.d_model, 768)
    if hasattr(config, 'dim'):
        config.dim = min(config.dim, 768)
    if hasattr(config, 'hidden_size'):
        config.hidden_size = min(config.hidden_size, 768)
    if hasattr(config, 'intermediate_size'):
        config.intermediate_size = min(config.intermediate_size, 3072)
    if hasattr(config, 'num_attention_heads'):
        config.num_attention_heads = min(config.num_attention_heads, 12)
    if hasattr(config, 'num_hidden_layers'):
        config.num_hidden_layers = min(config.num_hidden_layers, 12)
    return config

@pytest.mark.parametrize("model_name", PRETRAINED_TEST_MODELS)
def test_autopatchmodelforcausallm_pretrained(model_name):
    """Test AutoPatchModelForCausalLM initialization from pretrained models.

    Args:
        model_name: Name of the pretrained model.
    """
    device = 'cuda' if torch.cuda.is_available() else 'cpu'
    model = AutoPatchModelForCausalLM.from_pretrained(model_name).to(device)
    assert model is not None, f"Failed to load model from pretrained: {model_name}"

    # Create random input data
    batch_size = 2
    seq_length = 16
    input_ids = torch.randint(0, model.config.vocab_size, (batch_size, seq_length)).to(device)

    # Forward pass without patches
    outputs = model(input_ids=input_ids, return_dict=True)
    assert outputs.logits.shape == (batch_size, seq_length, model.config.vocab_size), \
        f"Unexpected output shape without patches for model {model_name}"

    # Create a model with patches
    patch_size = 4
    model_with_patches = AutoPatchModelForCausalLM.from_pretrained(model_name, patch_size=patch_size).to(device)
    assert model_with_patches is not None, f"Failed to load model with patches from pretrained: {model_name}"

    # Forward pass with patches
    outputs_with_patches = model_with_patches(input_ids=input_ids, labels=input_ids, return_dict=True)
    assert outputs_with_patches.logits.shape == (batch_size, seq_length // patch_size, model_with_patches.config.vocab_size), \
        f"Unexpected output shape with patches for model {model_name}"

    # Backpropagation test
    loss = outputs_with_patches.loss
    loss.backward()
    # Ensure backpropagation works without errors
    assert loss.item() is not None, "Backpropagation failed to compute loss."

    # **Force garbage collection to free up memory**
    del model
    del model_with_patches
    del input_ids
    del outputs
    del outputs_with_patches
    del loss
    gc.collect()
    if torch.cuda.is_available():
        torch.cuda.empty_cache()

# @pytest.mark.parametrize("model_name", ALL_MODELS)
# def test_autopatchmodelforcausallm_config(model_name):
#     """Test AutoPatchModelForCausalLM initialization from config for all models.

#     Args:
#         model_name: Name of the model architecture.
#     """
#     device = 'cuda' if torch.cuda.is_available() else 'cpu'

#     try:
#         config = AutoConfig.from_pretrained(model_name)
#     except Exception as e:
#         pytest.skip(f"Skipping model {model_name} due to config load failure: {e}")

#     # config = modify_config_for_testing(config)

#     try:
#         model = AutoPatchModelForCausalLM.from_config(config).to(device)
#     except Exception as e:
#         pytest.skip(f"Skipping model {model_name} due to model init failure: {e}")

#     assert model is not None, f"Failed to initialize model from config: {model_name}"

#     # Create random input data
#     batch_size = 2
#     seq_length = 16
#     # Ensure vocab_size is not None before using it
#     vocab_size = getattr(model.config, 'vocab_size', 50257) # Default to a common vocab size if not present
#     if vocab_size is None:
#         vocab_size = 50257
#     input_ids = torch.randint(0, vocab_size, (batch_size, seq_length)).to(device)

#     # Forward pass without patches
#     outputs = model(input_ids=input_ids)
#     assert outputs.logits.shape == (batch_size, seq_length, vocab_size), \
#         f"Unexpected output shape without patches for model {model_name}"

#     # Create a model with patches
#     patch_size = 4
#     model_with_patches = AutoPatchModelForCausalLM.from_config(config, patch_size=patch_size).to(device)
#     assert model_with_patches is not None, f"Failed to initialize model with patches from config: {model_name}"

#     # Forward pass with patches
#     outputs_with_patches = model_with_patches(input_ids=input_ids, labels=input_ids, return_dict=True)
#     assert outputs_with_patches.logits.shape == (batch_size, seq_length // patch_size, vocab_size), \
#         f"Unexpected output shape with patches for model {model_name}"

#     # Backpropagation test
#     loss = outputs_with_patches.loss
#     print(loss.item())
#     loss.backward()
#     # Ensure backpropagation works without errors
#     assert loss.item() is not None, "Backpropagation failed to compute loss."

#     # **Force garbage collection to free up memory**
#     del model
#     del model_with_patches
#     del config
#     del input_ids
#     del outputs
#     del outputs_with_patches
#     del loss
#     gc.collect()
#     if torch.cuda.is_available():
#         torch.cuda.empty_cache()

if __name__ == '__main__':
    # Example of how to run a single test for debugging
    test_autopatchmodelforcausallm_pretrained("gpt2")
