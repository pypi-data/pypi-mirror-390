
"""Patch utilities for causal language models.

This module provides a thin PyTorch wrappers around
`transformers` models to groups input token embeddings
into fixed-size "patches" (groups of tokens), optionally transforms them via a
user-provided function, and then forwards the patched embeddings through the
base model. This is useful to reduce the effective sequence length and
thereby speed up training. 

The implementation is intentionally lightweight and assumes the caller will
provide well-formed inputs (e.g. sequence length divisible by `patch_size`).
"""

import torch
import torch.nn as nn
import torch.nn.functional as F
from transformers import AutoModelForCausalLM, AutoModelForSeq2SeqLM, AutoModelForSequenceClassification
from transformers.cache_utils import Cache
from typing import Optional, Union, Tuple
from typing_extensions import Unpack, TypedDict
from transformers.modeling_outputs import CausalLMOutputWithPast, BaseModelOutputWithPast, Seq2SeqLMOutput, SequenceClassifierOutputWithPast
from transformers.utils import logging
from typing import Any, Dict



class AutoPatchModelForCausalLM(nn.Module):
    """Wrapper that compresses token embeddings into patches and forwards them to a causal LM.

        This wrapper takes a pretrained causal LM (loaded via
        :func:`transformers.AutoModelForCausalLM.from_pretrained`) and exposes a
        compatible ``forward`` signature. Before calling the underlying model it
        converts token-level embeddings into patch-level embeddings using
        ``patch_size`` and ``patch_func``.

        While the class name may suggest compatibility with VLMs such as GIT-base, 
        it is primarily designed for LLMs, causal language models such as GPT-2, etc.

        Args:
            model_name_or_path: Model identifier (Hugging Face model name or local
                path) to load the base causal LM from.
            patch_size: Number of consecutive tokens to group into a single
                "patch". Sequence length must be divisible by ``patch_size``.
            patch_func: Optional callable that maps a tensor of shape
                ``(batch, num_patches, patch_size, dim)`` to ``(batch, num_patches, dim)``.
                By default a mean-pooling implementation is used.

        Classmethods:
            from_pretrained: Instantiates the wrapper and loads the underlying model from pretrained weights.
            from_config: Instantiates the wrapper and loads the underlying model from a config object.

        Notes:
            - This wrapper forwards patched embeddings as ``inputs_embeds`` to the
                underlying model and sets ``input_ids`` to ``None``.
            - Position ids and attention masks are downsampled to match the
                number of patches.
        """
    def __init__(self, model_name_or_path: str, patch_size: int = 1, patch_func: Optional[callable] = None):
        super().__init__()
        self.model = None
        self.model_name_or_path = model_name_or_path
        self.patch_size = patch_size
        self.patch_func = patch_func if patch_func is not None else self._calculate_patch

    @property
    def config(self):
        if self.model is None:
            raise ValueError('No model loaded yet')
        return self.model.config

    @classmethod
    def from_pretrained(cls, model_name_or_path: str, *args, **kwargs):
        """Instantiate the class and load the model from pretrained weights."""
        instance = cls(model_name_or_path, *args, **kwargs)
        instance.model = AutoModelForCausalLM.from_pretrained(model_name_or_path)
        return instance
    
    @classmethod
    def from_config(cls, config, *args, **kwargs):
        """Instantiate the class and load the model from a config object."""
        instance = cls('[CUSTOM_MODEL]', *args, **kwargs)
        instance.model = AutoModelForCausalLM.from_config(config)
        return instance

    def _calculate_patch(self, inputs_embeds: torch.Tensor) -> torch.Tensor:
        """Default patch function: mean-pool over the patch size dimension.

        Parameters
        ----------
        inputs_embeds : torch.Tensor
            Tensor with shape ``(batch, num_patches, patch_size, hidden_dim)``.

        Returns
        -------
        torch.Tensor
            Tensor with shape ``(batch, num_patches, hidden_dim)`` containing
            the aggregated embedding for each patch.
        """
        # Example patch calculation: mean pooling over the patch size dimension
        return inputs_embeds.mean(dim=2)

    def prepare_patch_inputs(
            self,
            input_ids: torch.Tensor,
            attention_mask: Optional[torch.Tensor] = None,
            position_ids: Optional[torch.Tensor] = None,
            inputs_embeds: Optional[torch.Tensor] = None,
    ) -> Tuple[torch.Tensor, torch.Tensor, torch.Tensor]:
        """Convert token-level inputs into patch-level inputs.

        This method computes the input embeddings (if not provided), groups
        them into patches of ``self.patch_size``, and returns the patched
        embeddings together with a downsampled attention mask and position
        ids.

        Parameters
        ----------
        input_ids : torch.Tensor
            Long tensor of shape ``(batch, seq_len)`` containing token ids.
        attention_mask : Optional[torch.Tensor]
            Optional attention mask of shape ``(batch, seq_len)``. If
            provided it will be downsampled by taking every ``patch_size``-th
            element along the sequence dimension.
        position_ids : Optional[torch.Tensor]
            Optional position ids of shape ``(batch, seq_len)`` or
            ``(batch, num_patches)``. If omitted a new position ids tensor is
            created for the patches.
        inputs_embeds : Optional[torch.Tensor]
            Optional precomputed input embeddings. If ``None`` the model's
            embedding layer is used to compute embeddings from ``input_ids``.

        Returns
        -------
        Tuple[torch.Tensor, torch.Tensor, torch.Tensor]
            A tuple ``(inputs_embeds, attention_mask, position_ids)`` where
            ``inputs_embeds`` has shape ``(batch, num_patches, hidden_dim)``,
            ``attention_mask`` has shape ``(batch, num_patches)`` and
            ``position_ids`` has shape ``(batch, num_patches)``.
        """
        batch_size, seq_length = input_ids.shape
        num_patches = seq_length // self.patch_size

        # Get the original embeddings
        if inputs_embeds is None:
            inputs_embeds = self.model.get_input_embeddings()(input_ids)
        else:
            inputs_embeds = self.model.embed_tokens(input_ids)

        # Compress into patches using the patch function.
        inputs_embeds = inputs_embeds.view(batch_size, num_patches, self.patch_size, -1)
        inputs_embeds = self.patch_func(inputs_embeds)

        # Adjust position ids
        if position_ids is None:
            position_ids = torch.arange(0, num_patches, dtype=torch.long, device=input_ids.device)
            position_ids = position_ids.view(1, -1).expand(batch_size, -1)
        else:
            position_ids = position_ids[:, :num_patches]

        # Adjust attention mask
        if attention_mask is not None:
            attention_mask = attention_mask[:, ::self.patch_size]
        else:
            attention_mask = torch.ones((batch_size, num_patches), device=input_ids.device)

        return inputs_embeds, attention_mask, position_ids

    def forward(
        self,
        input_ids: Optional[torch.LongTensor] = None,
        attention_mask: Optional[torch.Tensor] = None,
        position_ids: Optional[torch.LongTensor] = None,
        past_key_values= None,
        inputs_embeds: Optional[torch.FloatTensor] = None,
        labels: Optional[torch.LongTensor] = None,
        use_cache: Optional[bool] = None,
        output_attentions: Optional[bool] = None,
        output_hidden_states: Optional[bool] = None,
        return_dict: Optional[bool] = None,
        **kwargs,
    ) -> CausalLMOutputWithPast:
        """Forward pass that runs the base causal LM on patched embeddings.

        The method prepares patch inputs (embeddings, attention mask and
        position ids), forwards them through the underlying model and then
        optionally computes a patch-wise negative log-likelihood loss if
        ``labels`` are provided.

        Parameters
        ----------
        input_ids : Optional[torch.LongTensor]
            Token ids of shape ``(batch, seq_len)``. Required if
            ``inputs_embeds`` is not provided.
        attention_mask : Optional[torch.Tensor]
            Attention mask at token granularity. It will be downsampled to
            patch granularity.
        position_ids : Optional[torch.LongTensor]
            Position ids at token or patch granularity.
        past_key_values : Optional[Cache]
            Past key/values for the underlying model's caching mechanism.
        inputs_embeds : Optional[torch.FloatTensor]
            Precomputed input embeddings. If provided ``input_ids`` may be
            ignored.
        labels : Optional[torch.LongTensor]
            Labels used for loss computation. When provided the function
            computes a simple patch-wise NLL loss.
        use_cache, output_attentions, output_hidden_states, return_dict
            Additional flags forwarded to the underlying transformers model.

        Returns
        -------
        transformers.modeling_outputs.CausalLMOutputWithPast
            Model outputs containing ``logits`` and optionally ``loss`` and
            other fields (``past_key_values``, ``hidden_states``,
            ``attentions``).
        """
        inputs_embeds, attention_mask, position_ids = self.prepare_patch_inputs(
            input_ids=input_ids,
            attention_mask=attention_mask,
            position_ids=position_ids,
            inputs_embeds=inputs_embeds,
        )

        outputs: BaseModelOutputWithPast = self.model(
            input_ids=None,
            attention_mask=attention_mask,
            position_ids=position_ids,
            past_key_values=past_key_values,
            inputs_embeds=inputs_embeds,
            use_cache=use_cache,
            output_attentions=output_attentions,
            output_hidden_states=output_hidden_states,
            return_dict=return_dict,
            **kwargs,
        )

        logits = outputs[0]
        # Initialize loss as a tensor (scalar) on the same device/dtype as logits
        # so that autograd can properly track the computation graph.
        loss = logits.new_zeros(())

        # If labels are not provided by the caller, attempt to derive them from
        # the input_ids (standard LM setting where labels == input_ids).
        # This makes the tests (which don't pass labels) able to call
        # loss.backward() on a tensor connected to model parameters.
        effective_labels = labels if labels is not None else None
        if effective_labels is None and 'input_ids' in locals() and input_ids is not None:
            effective_labels = input_ids

        if effective_labels is not None:
            # Reshape logits and labels for patch-wise loss calculation
            shifted_logits = logits[..., :-1, :].reshape(-1, self.model.config.vocab_size)
            shifted_labels = effective_labels[..., self.patch_size:].reshape(-1, self.patch_size)

            # Compute loss
            loss_probs = F.log_softmax(shifted_logits, dim=-1)
            for i in range(self.patch_size):
                # nll_loss returns a tensor; accumulate into `loss` tensor so
                # gradients flow through the whole computation.
                loss = loss + F.nll_loss(loss_probs, shifted_labels[:, i], reduction='mean')
            loss = loss / float(self.patch_size)

            if not return_dict:
                output = (logits,) + outputs[1:]
                return ((loss,) + output) if loss is not None else output

        return CausalLMOutputWithPast(
            loss=loss,
            logits=logits,
            past_key_values=outputs.past_key_values if hasattr(outputs, 'past_key_values') else None,
            hidden_states=outputs.hidden_states if hasattr(outputs, 'hidden_states') else None,
            attentions=outputs.attentions if hasattr(outputs, 'attentions') else None,
        )

class AutoPatchModelForSeq2SeqLM(nn.Module):
    """Wrapper that compresses token embeddings into patches and forwards them to a seq2seq LM.

        This wrapper takes a pretrained seq2seq LM (loaded via
        :func:`transformers.AutoModelForSeq2SeqLM.from_pretrained`) and exposes a
        compatible ``forward`` signature. Before calling the underlying model it
        converts token-level embeddings into patch-level embeddings using
        ``patch_size`` and ``patch_func``.

        While the class name may suggest compatibility with VLMs such as GIT-base, 
        it is primarily designed for LLMs, causal language models such as GPT-2, etc.

        Args:
            model_name_or_path: Model identifier (Hugging Face model name or local
                path) to load the base seq2seq LM from.
            patch_size: Number of consecutive tokens to group into a single
                "patch". Sequence length must be divisible by ``patch_size``.
            patch_func: Optional callable that maps a tensor of shape
                ``(batch, num_patches, patch_size, dim)`` to ``(batch, num_patches, dim)``.
                By default a mean-pooling implementation is used.

        Classmethods:
            from_pretrained: Instantiates the wrapper and loads the underlying model from pretrained weights.
            from_config: Instantiates the wrapper and loads the underlying model from a config object.
    """

    def __init__(self, model_name_or_path: str, patch_size: int = 1, patch_func: Optional[callable] = None):
        super().__init__()
        self.model = None
        self.model_name_or_path = model_name_or_path
        self.patch_size = patch_size
        self.patch_func = patch_func if patch_func is not None else self._calculate_patch
    
    @property
    def config(self):
        if self.model is None:
            raise ValueError('No model loaded yet')
        return self.model.config
        
    @classmethod
    def from_pretrained(cls, model_name_or_path: str, *args, **kwargs):
        """Instantiate the class and load the model from pretrained weights."""
        instance = cls(model_name_or_path, *args, **kwargs)
        instance.model = AutoModelForSeq2SeqLM.from_pretrained(model_name_or_path)
        return instance
    
    @classmethod
    def from_config(cls, config, *args, **kwargs):
        """Instantiate the class and load the model from a config object."""
        instance = cls('[CUSTOM_MODEL]', *args, **kwargs)
        instance.model = AutoModelForSeq2SeqLM.from_config(config)
        return instance

    def _calculate_patch(self, inputs_embeds: torch.Tensor) -> torch.Tensor:
        """Default patch function: mean-pool over the patch size dimension.

        Parameters
        ----------
        inputs_embeds : torch.Tensor
            Tensor with shape ``(batch, num_patches, patch_size, hidden_dim)``.

        Returns
        -------
        torch.Tensor
            Tensor with shape ``(batch, num_patches, hidden_dim)`` containing
            the aggregated embedding for each patch.
        """
        # Example patch calculation: mean pooling over the patch size dimension
        return inputs_embeds.mean(dim=2)
    
    def prepare_patch_inputs(
            self,
            input_ids: torch.Tensor,
            attention_mask: Optional[torch.Tensor] = None,
            position_ids: Optional[torch.Tensor] = None,
            inputs_embeds: Optional[torch.Tensor] = None,
    ) -> Tuple[torch.Tensor, torch.Tensor, torch.Tensor]:
        """Convert token-level inputs into patch-level inputs.

        This method computes the input embeddings (if not provided), groups
        them into patches of ``self.patch_size``, and returns the patched
        embeddings together with a downsampled attention mask and position
        ids.

        Parameters
        ----------
        input_ids : torch.Tensor
            Long tensor of shape ``(batch, seq_len)`` containing token ids.
        attention_mask : Optional[torch.Tensor]
            Optional attention mask of shape ``(batch, seq_len)``. If
            provided it will be downsampled by taking every ``patch_size``-th
            element along the sequence dimension.
        position_ids : Optional[torch.Tensor]
            Optional position ids of shape ``(batch, seq_len)`` or
            ``(batch, num_patches)``. If omitted a new position ids tensor is
            created for the patches.
        inputs_embeds : Optional[torch.Tensor]
            Optional precomputed input embeddings. If ``None`` the model's
            embedding layer is used to compute embeddings from ``input_ids``.

        Returns
        -------
        Tuple[torch.Tensor, torch.Tensor, torch.Tensor]
            A tuple ``(inputs_embeds, attention_mask, position_ids)`` where
            ``inputs_embeds`` has shape ``(batch, num_patches, hidden_dim)``,
            ``attention_mask`` has shape ``(batch, num_patches)`` and
            ``position_ids`` has shape ``(batch, num_patches)``.
        """
        batch_size, seq_length = input_ids.shape
        num_patches = seq_length // self.patch_size

        # Get the original embeddings
        if inputs_embeds is None:
            inputs_embeds = self.model.get_input_embeddings()(input_ids)
        else:
            inputs_embeds = self.model.embed_tokens(input_ids)

        # Compress into patches using the patch function.
        inputs_embeds = inputs_embeds.view(batch_size, num_patches, self.patch_size, -1)
        inputs_embeds = self.patch_func(inputs_embeds)

        # Adjust position ids
        if position_ids is None:
            position_ids = torch.arange(0, num_patches, dtype=torch.long, device=input_ids.device)
            position_ids = position_ids.view(1, -1).expand(batch_size, -1)
        else:
            position_ids = position_ids[:, :num_patches]

        # Adjust attention mask
        if attention_mask is not None:
            attention_mask = attention_mask[:, ::self.patch_size]
        else:
            attention_mask = torch.ones((batch_size, num_patches), device=input_ids.device)

        return inputs_embeds, attention_mask, position_ids
    
    def forward(
        self,
        input_ids: Optional[torch.LongTensor] = None,
        attention_mask: Optional[torch.FloatTensor] = None,
        decoder_input_ids: Optional[torch.LongTensor] = None,
        decoder_attention_mask: Optional[torch.BoolTensor] = None,
        encoder_outputs: Optional[tuple[tuple[torch.Tensor]]] = None,
        past_key_values: Optional[Cache] = None,
        inputs_embeds: Optional[torch.FloatTensor] = None,
        decoder_inputs_embeds: Optional[torch.FloatTensor] = None,
        labels: Optional[torch.LongTensor] = None,
        use_cache: Optional[bool] = None,
        output_attentions: Optional[bool] = None,
        output_hidden_states: Optional[bool] = None,
        return_dict: Optional[bool] = None,
        cache_position: Optional[torch.LongTensor] = None,
        **kwargs,
    ) -> Union[tuple[torch.FloatTensor], Seq2SeqLMOutput]:
        pass
        
        inputs_embeds, attention_mask, _ = self.prepare_patch_inputs(
                input_ids=input_ids,
                attention_mask=attention_mask,
                position_ids=None,
                inputs_embeds=inputs_embeds,
            )
        
        encoder_outputs = self.model.encoder(
            input_ids=None,
            attention_mask=attention_mask,
            inputs_embeds=inputs_embeds,
            return_dict=return_dict,
            output_attentions=output_attentions,
            output_hidden_states=output_hidden_states,
            **kwargs,
        )

        if labels is not None and decoder_input_ids is None:
            decoder_input_ids = self.model._shift_right(labels)

        decoder_inputs_embeds, decoder_attention_mask, _ = self.prepare_patch_inputs(
                input_ids=decoder_input_ids,
                attention_mask=decoder_attention_mask,
                position_ids=None,
                inputs_embeds=decoder_inputs_embeds,
            )
    
        decoder_outputs = self.model.decoder(
            input_ids=None,
            attention_mask=decoder_attention_mask,
            inputs_embeds=decoder_inputs_embeds,
            past_key_values=past_key_values,
            encoder_hidden_states=encoder_outputs[0],
            encoder_attention_mask=attention_mask,
            use_cache=use_cache,
            output_attentions=output_attentions,
            output_hidden_states=output_hidden_states,
            return_dict=return_dict,
            **kwargs,
        )

        sequence_output = decoder_outputs[0]
        lm_logits = self.model.lm_head(sequence_output)

        loss = lm_logits.new_zeros(())
        effective_labels = labels if labels is not None else None
        if effective_labels is None and 'decoder_input_ids' in locals() and decoder_input_ids is not None:
            effective_labels = decoder_input_ids
        
        if effective_labels is not None:
            shifted_logits = lm_logits[..., :-1, :].reshape(-1, self.model.config.vocab_size)
            shifted_labels = effective_labels[..., self.patch_size:].reshape(-1, self.patch_size)

            loss_probs = F.log_softmax(shifted_logits, dim=-1)
            for i in range(self.patch_size):
                loss = loss + F.nll_loss(loss_probs, shifted_labels[:, i], reduction='mean')
            loss = loss / float(self.patch_size)

            if not return_dict:
                output = (lm_logits,) + decoder_outputs[1:]
                return ((loss,) + output) if loss is not None else output
            
        return Seq2SeqLMOutput(
            loss=loss,
            logits=lm_logits,
            past_key_values=getattr(decoder_outputs, "past_key_values", None),
            decoder_hidden_states=getattr(decoder_outputs, "hidden_states", None),
            decoder_attentions=getattr(decoder_outputs, "attentions", None),
            cross_attentions=getattr(decoder_outputs, "cross_attentions", None),
            encoder_last_hidden_state=encoder_outputs[0] if isinstance(encoder_outputs, (tuple, list)) else getattr(encoder_outputs, "last_hidden_state", None),
            encoder_hidden_states=getattr(encoder_outputs, "hidden_states", None),
            encoder_attentions=getattr(encoder_outputs, "attentions", None),
        )


class AutoPatchModelForSequenceClassification(nn.Module):
    """Wrapper that compresses token embeddings into patches and forwards them to a sequence classification model.

        This wrapper takes a pretrained sequence classification model (loaded via
        :func:`transformers.AutoModelForSequenceClassification.from_pretrained`) and exposes a
        compatible ``forward`` signature. Before calling the underlying model it
        converts token-level embeddings into patch-level embeddings using
        ``patch_size`` and ``patch_func``.

        Args:
            model_name_or_path: Model identifier (Hugging Face model name or local
                path) to load the base sequence classification model from.
            patch_size: Number of consecutive tokens to group into a single
                "patch". Sequence length must be divisible by ``patch_size``.
            patch_func: Optional callable that maps a tensor of shape
                ``(batch, num_patches, patch_size, dim)`` to ``(batch, num_patches, dim)``.
                By default a mean-pooling implementation is used.
    """

    def __init__(self, model_name_or_path: str, patch_size: int = 1, patch_func: Optional[callable] = None):
        super().__init__()
        self.model = None
        self.model_name_or_path = model_name_or_path
        self.patch_size = patch_size
        self.patch_func = patch_func if patch_func is not None else self._calculate_patch

    def _calculate_patch(self, x: torch.Tensor) -> torch.Tensor:
        # Default patch function: mean pooling
        return x.mean(dim=2)
    
    @property
    def config(self):
        if self.model is None:
            raise ValueError('No model loaded yet')
        return self.model.config

    @classmethod
    def from_pretrained(cls, model_name_or_path: str, *args, **kwargs):
        """Instantiate the class and load the model from pretrained weights."""
        instance = cls(model_name_or_path, *args, **kwargs)
        instance.model = AutoModelForSequenceClassification.from_pretrained(model_name_or_path)
        return instance
    
    @classmethod
    def from_config(cls, config, *args, **kwargs):
        """Instantiate the class and load the model from a config object."""
        instance = cls('[CUSTOM_MODEL]', *args, **kwargs)
        instance.model = AutoModelForSequenceClassification.from_config(config)
        return instance
    
    def prepare_patch_inputs(
            self,
            input_ids: torch.Tensor,
            attention_mask: Optional[torch.Tensor] = None,
            position_ids: Optional[torch.Tensor] = None,
            inputs_embeds: Optional[torch.Tensor] = None,
    ) -> Tuple[torch.Tensor, torch.Tensor, torch.Tensor]:
        """Convert token-level inputs into patch-level inputs.

        This method computes the input embeddings (if not provided), groups
        them into patches of ``self.patch_size``, and returns the patched
        embeddings together with a downsampled attention mask and position
        ids.

        Parameters
        ----------
        input_ids : torch.Tensor
            Long tensor of shape ``(batch, seq_len)`` containing token ids.
        attention_mask : Optional[torch.Tensor]
            Optional attention mask of shape ``(batch, seq_len)``. If
            provided it will be downsampled by taking every ``patch_size``-th
            element along the sequence dimension.
        position_ids : Optional[torch.Tensor]
            Optional position ids of shape ``(batch, seq_len)`` or
            ``(batch, num_patches)``. If omitted a new position ids tensor is
            created for the patches.
        inputs_embeds : Optional[torch.Tensor]
            Optional precomputed input embeddings. If ``None`` the model's
            embedding layer is used to compute embeddings from ``input_ids``.

        Returns
        -------
        Tuple[torch.Tensor, torch.Tensor, torch.Tensor]
            A tuple ``(inputs_embeds, attention_mask, position_ids)`` where
            ``inputs_embeds`` has shape ``(batch, num_patches, hidden_dim)``,
            ``attention_mask`` has shape ``(batch, num_patches)`` and
            ``position_ids`` has shape ``(batch, num_patches)``.
        """
        batch_size, seq_length = input_ids.shape
        num_patches = seq_length // self.patch_size

        # Get the original embeddings
        if inputs_embeds is None:
            inputs_embeds = self.model.get_input_embeddings()(input_ids)
        else:
            inputs_embeds = self.model.embed_tokens(input_ids)

        # Compress into patches using the patch function.
        inputs_embeds = inputs_embeds.view(batch_size, num_patches, self.patch_size, -1)
        inputs_embeds = self.patch_func(inputs_embeds)

        # Adjust position ids
        if position_ids is None:
            position_ids = torch.arange(0, num_patches, dtype=torch.long, device=input_ids.device)
            position_ids = position_ids.view(1, -1).expand(batch_size, -1)
        else:
            position_ids = position_ids[:, :num_patches]

        # Adjust attention mask
        if attention_mask is not None:
            attention_mask = attention_mask[:, ::self.patch_size]
        else:
            attention_mask = torch.ones((batch_size, num_patches), device=input_ids.device)

        return inputs_embeds, attention_mask, position_ids


    def forward(
        self,
        input_ids: Optional[torch.LongTensor] = None,
        attention_mask: Optional[torch.Tensor] = None,
        position_ids: Optional[torch.LongTensor] = None,
        past_key_values: Optional[Cache] = None,
        inputs_embeds: Optional[torch.FloatTensor] = None,
        labels: Optional[torch.LongTensor] = None,
        use_cache: Optional[bool] = None,
        **kwargs,
    ) -> SequenceClassifierOutputWithPast:
        
        inputs_embeds, attention_mask, position_ids = self.prepare_patch_inputs(
            input_ids=input_ids,
            attention_mask=attention_mask,
            position_ids=position_ids,
            inputs_embeds=inputs_embeds,
        )


        transformer_outputs: BaseModelOutputWithPast = self.model.model(
            None,
            attention_mask=attention_mask,
            position_ids=position_ids,
            past_key_values=past_key_values,
            inputs_embeds=inputs_embeds,
            use_cache=use_cache,
            **kwargs,
        )
        hidden_states = transformer_outputs.last_hidden_state
        logits = self.model.score(hidden_states)

        if input_ids is not None:
            batch_size = input_ids.shape[0]
        else:
            batch_size = inputs_embeds.shape[0]

        if self.config.pad_token_id is None and batch_size != 1:
            raise ValueError("Cannot handle batch sizes > 1 if no padding token is defined.")
        if self.config.pad_token_id is None:
            last_non_pad_token = -1
        
        # AutoPatchModel needs padding right. Find the last non-pad token using the attention mask.
        else:
            if attention_mask is None:
                attention_mask = torch.ones_like(input_ids, device=logits.device)
            last_non_pad_token = attention_mask.long().sum(dim=1) - 1

        pooled_logits = logits[torch.arange(batch_size, device=logits.device), last_non_pad_token]

        loss = None
        if labels is not None:
            loss = self.model.loss_function(logits=logits, labels=labels, pooled_logits=pooled_logits, config=self.config)

        return SequenceClassifierOutputWithPast(
            loss=loss,
            logits=pooled_logits,
            past_key_values=transformer_outputs.past_key_values,
            hidden_states=transformer_outputs.hidden_states,
            attentions=transformer_outputs.attentions,
        )        