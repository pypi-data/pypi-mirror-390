import fusekit.Common.env as env
import torch
from transformers import AutoProcessor, LlavaForConditionalGeneration
from transformers import ProcessorMixin, GenerationConfig

from .causal_model import CausalModel
from .base import CustomProcessor


class GenericPixtral(CausalModel):
    def __init__(self,
                 model_path,
                 config=None,
                 device=None,
                 memory_limit=None,
                 precision=None,
                 force_sharding=True):


        processor = AutoProcessor.from_pretrained(model_path, trust_remote_code=True)
        model = LlavaForConditionalGeneration.from_pretrained(model_path, trust_remote_code=True)
        processor = Pixtral12BProcessor(processor)
        vision_embed_size = 0
        super().__init__(model, processor, processor.tokenizer, device,
                         memory_limit, vision_embed_size=vision_embed_size, 
                         force_sharding=force_sharding, batch_images=False)
        
        orig_generate = model.generate
        def patched_generate(*args, **kwargs):
            kwargs.setdefault("pad_token_id", processor.tokenizer.eos_token_id)
            return orig_generate(*args, **kwargs)
        model.generate = patched_generate

class Pixtral12BProcessor(CustomProcessor):
    def __init__(self, base_processor:ProcessorMixin):
        super().__init__(base_processor)
        self.base_processor = base_processor
    
    def __call__(self, *args, **kwargs):
        del kwargs['padding']
        return self.base_processor.__call__(*args, **kwargs)
        
class Pixtral_12b(GenericPixtral):
    def __init__(self,
                 config=None,
                 device=None,
                 memory_limit=None,
                 precision=torch.bfloat16,
                 force_sharding=True):
        
        super().__init__(env.ModelPath.pixtral_12b,
                         config=config,
                         device=device,
                         memory_limit=memory_limit,
                         precision=precision,
                         force_sharding=force_sharding)
        
        self.model_name = "Pixtral_12b"