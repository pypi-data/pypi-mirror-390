import fusekit.Common.env as env
import torch
from transformers import AutoProcessor, AutoConfig
from transformers import AutoModelForCausalLM
from transformers import ProcessorMixin
from transformers.cache_utils import Cache  
import copy

from .causal_model import CausalModel
from .base import CustomProcessor



class GenericPhi3(CausalModel):
    def __init__(self,
                 model_path,
                 config=None,
                 device=None,
                 memory_limit=None,
                 precision=None,
                 force_sharding=True):
        processor: AutoProcessor = AutoProcessor.from_pretrained(model_path, 
                                                                 num_crops=4, 
                                                                 trust_remote_code=True)

        self.config = config or AutoConfig.from_pretrained(model_path, trust_remote_code=True)
        model = AutoModelForCausalLM.from_pretrained(
            model_path,
            torch_dtype=precision,
            trust_remote_code=True,
            _attn_implementation='flash_attention_2'
        )

        processor = Phi3Processor(processor)
        model.prepare_inputs_for_generation=self.prepare_inputs_for_generation

        vision_embed_size = 0
        super().__init__(model, processor, processor.tokenizer, device,
                         memory_limit, vision_embed_size=vision_embed_size, 
                         force_sharding=force_sharding, batch_images=False)


        
        
class Phi3Processor(CustomProcessor):
    def __init__(self, base_processor:ProcessorMixin):
        super().__init__(base_processor)
        self.base_processor = base_processor

    def __call__(self, *args, **kwargs):
        del kwargs['add_special_tokens']
        new_args=(args[1],args[0])
        return self.base_processor.__call__(*new_args, **kwargs)
        
    def format_message(self, text):
        return {"role": "user", "content": "<|image_1|>\n"+ text}

    def apply_chat_template(self,messages, tokenize=False, add_generation_prompt=True):
        return self.base_processor.tokenizer.apply_chat_template(messages, tokenize=tokenize, add_generation_prompt=add_generation_prompt)

# Copied from transformers.models.persimmon.modeling_persimmon.PersimmonForCausalLM.prepare_inputs_for_generation
    def prepare_inputs_for_generation(
        self, input_ids, past_key_values=None, attention_mask=None, inputs_embeds=None, **kwargs
    ):
        # When the first time input length reached long and short factor switching point, enforce re-compute cache
        # It will cause downside of slower at this single token position, however, better than current failure.
        if past_key_values and self.config.rope_scaling and input_ids.shape[1] >= self.config.original_max_position_embeddings + 1:
            past_length = past_key_values.seen_tokens if isinstance(past_key_values, Cache) else past_key_values[0][0].shape[2]
            if past_length <= self.config.original_max_position_embeddings:
                past_key_values = None

        if past_key_values is not None:
            if isinstance(past_key_values, Cache):
                cache_length = past_key_values.get_seq_length()
                past_length = past_key_values.seen_tokens
                max_cache_length = past_key_values.get_max_cache_shape()
            else:
                cache_length = past_length = past_key_values[0][0].shape[2]
                max_cache_length = None

            # Keep only the unprocessed tokens:
            # 1 - If the length of the attention_mask exceeds the length of input_ids, then we are in a setting where
            # some of the inputs are exclusively passed as part of the cache (e.g. when passing input_embeds as
            # input)
            if attention_mask is not None and attention_mask.shape[1] > input_ids.shape[1]:
                input_ids = input_ids[:, -(attention_mask.shape[1] - past_length) :]
            # 2 - If the past_length is smaller than input_ids', then input_ids holds all input tokens. We can discard
            # input_ids based on the past_length.
            elif past_length < input_ids.shape[1]:
                input_ids = input_ids[:, past_length:]
            # 3 - Otherwise (past_length >= input_ids.shape[1]), let's assume input_ids only has unprocessed tokens.

            # If we are about to go beyond the maximum cache length, we need to crop the input attention mask.
            if (
                max_cache_length is not None
                and attention_mask is not None
                and cache_length + input_ids.shape[1] > max_cache_length
            ):
                attention_mask = attention_mask[:, -max_cache_length:]

        position_ids = kwargs.get("position_ids", None)
        if attention_mask is not None and position_ids is None:
            # create position_ids on the fly for batch generation
            position_ids = attention_mask.long().cumsum(-1) - 1
            position_ids.masked_fill_(attention_mask == 0, 1)
            if past_key_values:
                position_ids = position_ids[:, -input_ids.shape[1] :]

        # if `inputs_embeds` are passed, we only want to use them in the 1st generation step
        if inputs_embeds is not None and past_key_values is None:
            model_inputs = {"inputs_embeds": inputs_embeds}
        else:
            model_inputs = {"input_ids": input_ids}

        model_inputs.update(
            {
                "position_ids": position_ids,
                "past_key_values": past_key_values,
                "use_cache": kwargs.get("use_cache"),
                "attention_mask": attention_mask,
            }
        )
        return model_inputs
    
class Phi3p5_Vision(GenericPhi3):
    def __init__(self,
                 config=None,
                 device=None,
                 memory_limit=None,
                 precision=torch.bfloat16,
                 force_sharding=True):
        
        super().__init__(env.ModelPath.phi3_5_vision,
                         config=config,
                         device=device,
                         memory_limit=memory_limit,
                         precision=precision,
                         force_sharding=force_sharding)
        
        self.model_name = "Phi3p5_Vision"
