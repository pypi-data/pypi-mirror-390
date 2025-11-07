import fusekit.Common.env as env
import torch
from transformers import LlavaNextProcessor, LlavaNextConfig
from transformers import LlavaNextForConditionalGeneration

from .causal_model import CausalModel
from .base import CustomProcessor

class GenericLlavaNext(CausalModel):
    def __init__(self,
                 model_path,
                 config=None,
                 device=None,
                 memory_limit=None,
                 precision=None,
                 force_sharding=True):
        processor: LlavaNextProcessor = LlavaNextProcessor.from_pretrained(model_path)
        self.config = config or LlavaNextConfig.from_pretrained(model_path)
        model = LlavaNextForConditionalGeneration.from_pretrained(
            model_path,
            torch_dtype=precision,
            config=self.config
        )

        processor = CustomProcessor(processor)

        vision_embed_size = model.vision_tower.vision_model.embeddings.embed_dim
        #print(model.vision_tower.vision_model.embeddings)
        #print(vision_embed_size)
        super().__init__(model, processor, processor.tokenizer, device,
                         memory_limit, vision_embed_size=vision_embed_size, 
                         force_sharding=force_sharding, batch_images=False)
        

class LlavaNext_7b_Vicuna(GenericLlavaNext):
    def __init__(self,
                 config=None,
                 device=None,
                 memory_limit=None,
                 precision=torch.bfloat16,
                 force_sharding=True):
        
        super().__init__(env.ModelPath.llava_next_7b_vicuna,
                         config=config,
                         device=device,
                         memory_limit=memory_limit,
                         precision=precision,
                         force_sharding=force_sharding)
        
        self.model_name = "LlavaNext_7b_Vicuna"

class LlavaNext_13b_Vicuna(GenericLlavaNext):
    def __init__(self,
                 config=None,
                 device=None,
                 memory_limit=None,
                 precision=torch.bfloat16,
                 force_sharding=True):
        
        super().__init__(env.ModelPath.llava_next_13b_vicuna,
                         config=config,
                         device=device,
                         memory_limit=memory_limit,
                         precision=precision,
                         force_sharding=force_sharding)
        
        self.model_name = "LlavaNext_13b_Vicuna"

class LlavaNext_7b_Mistral(GenericLlavaNext):
    def __init__(self,
                 config=None,
                 device=None,
                 memory_limit=None,
                 precision=torch.bfloat16,
                 force_sharding=True):
        
        super().__init__(env.ModelPath.llava_next_7b_mistral,
                         config=config,
                         device=device,
                         memory_limit=memory_limit,
                         precision=precision,
                         force_sharding=force_sharding)
        
        orig_generate = self.model.generate
        def patched_generate(*args, **kwargs):
            kwargs.setdefault("pad_token_id", self.processor.tokenizer.eos_token_id)
            return orig_generate(*args, **kwargs)
        self.model.generate = patched_generate
        
        self.model_name = "LlavaNext_7b_Mistral"

class LlavaNext_34b(GenericLlavaNext):
    def __init__(self,
                 config=None,
                 device=None,
                 memory_limit=None,
                 precision=torch.bfloat16,
                 force_sharding=True):
        
        super().__init__(env.ModelPath.llava_next_34b,
                         config=config,
                         device=device,
                         memory_limit=memory_limit,
                         precision=precision,
                         force_sharding=force_sharding)
        
        self.model_name = "LlavaNext_34b"

class LlavaNext_72b(GenericLlavaNext):
    def __init__(self,
                 config=None,
                 device=None,
                 memory_limit=None,
                 precision=torch.bfloat16,
                 force_sharding=True):
        
        super().__init__(env.ModelPath.llava_next_72b,
                         config=config,
                         device=device,
                         memory_limit=memory_limit,
                         precision=precision,
                         force_sharding=force_sharding)
        
        self.model_name = "LlavaNext_72b"

class LlavaNext_110b(GenericLlavaNext):
    def __init__(self,
                 config=None,
                 device=None,
                 memory_limit=None,
                 precision=torch.bfloat16,
                 force_sharding=True):
        
        super().__init__(env.ModelPath.llava_next_110b,
                         config=config,
                         device=device,
                         memory_limit=memory_limit,
                         precision=precision,
                         force_sharding=force_sharding)
        
        self.model_name = "LlavaNext_110b"