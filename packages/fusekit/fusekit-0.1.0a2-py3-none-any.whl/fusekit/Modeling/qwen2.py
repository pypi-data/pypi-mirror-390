import fusekit.Common.env as env
import torch
from transformers import Qwen2VLProcessor, Qwen2VLConfig
from transformers import Qwen2VLForConditionalGeneration

from .causal_model import CausalModel
from .base import CustomProcessor

class GenericQwen2(CausalModel):
    def __init__(self,
                 model_path,
                 config=None,
                 device=None,
                 memory_limit=None,
                 precision=None,
                 force_sharding=True):
        processor: Qwen2VLProcessor = Qwen2VLProcessor.from_pretrained(model_path)
        self.config = config or Qwen2VLConfig.from_pretrained(model_path)
        model = Qwen2VLForConditionalGeneration.from_pretrained(
            model_path,
            torch_dtype=precision,
            config=self.config
        )

        processor = CustomProcessor(processor)

        vision_embed_size = model.visual.patch_embed.embed_dim
        vision_embed_size = 0
        #print(model.visual.patch_embed)
        #print(vision_embed_size)
        super().__init__(model, processor, processor.tokenizer, device,
                         memory_limit, vision_embed_size=vision_embed_size, 
                         force_sharding=force_sharding, batch_images=False)


class Qwen2_2b(GenericQwen2):
    def __init__(self,
                 config=None,
                 device=None,
                 memory_limit=None,
                 precision=torch.bfloat16,
                 force_sharding=True):
        
        super().__init__(env.ModelPath.qwen2_2b,
                         config=config,
                         device=device,
                         memory_limit=memory_limit,
                         precision=precision,
                         force_sharding=force_sharding)
        
        self.model_name = "Qwen2_2b"

class Qwen2_7b(GenericQwen2):
    def __init__(self,
                 config=None,
                 device=None,
                 memory_limit=None,
                 precision=torch.bfloat16,
                 force_sharding=True):
        
        super().__init__(env.ModelPath.qwen2_7b,
                         config=config,
                         device=device,
                         memory_limit=memory_limit,
                         precision=precision,
                         force_sharding=force_sharding)
        
        self.model_name = "Qwen2_7b"