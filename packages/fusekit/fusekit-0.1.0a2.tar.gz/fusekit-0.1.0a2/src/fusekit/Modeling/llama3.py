import fusekit.Common.env as env
import torch
from transformers import MllamaProcessor, MllamaConfig
from transformers import MllamaForConditionalGeneration
from transformers import LlamaTokenizer, LlamaConfig, LlamaForCausalLM, PreTrainedTokenizerFast
from transformers import AutoTokenizer, AutoModelForCausalLM, AutoConfig

from .causal_model import CausalModel
from .base import CustomProcessor

class GenericLlama3(CausalModel):
    def __init__(self,
                 model_path,
                 config=None,
                 device=None,
                 memory_limit=None,
                 precision=None,
                 force_sharding=True):
        tokenizer: AutoTokenizer = AutoTokenizer.from_pretrained(model_path)
        #tokenizer.add_special_tokens({"pad_token":"<pad>"})

        self.config = config or AutoConfig.from_pretrained(model_path)
        model = AutoModelForCausalLM.from_pretrained(model_path,
                                                 torch_dtype=precision,
                                                 config=self.config)
        
        #self.config.pad_token_id = tokenizer.pad_token_id

        #model.resize_token_embeddings(len(tokenizer), mean_resizing=False)

        super().__init__(model, None, tokenizer,
                         device=device,
                         memory_limit=memory_limit, 
                         force_sharding=force_sharding)
        
        orig_generate = model.generate
        def patched_generate(*args, **kwargs):
            kwargs.setdefault("pad_token_id", tokenizer.eos_token_id)
            return orig_generate(*args, **kwargs)
        model.generate = patched_generate

class Llama3_8b(GenericLlama3):
    def __init__(self,
                 config=None,
                 device=None,
                 memory_limit=None,
                 precision=torch.bfloat16,
                 force_sharding=True):
        
        super().__init__(env.ModelPath.llama3_8b,
                         config=config,
                         device=device,
                         memory_limit=memory_limit,
                         precision=precision,
                         force_sharding=force_sharding)
        
        self.model_name = "Llama3_8b"


class GenericLlama3Vision(CausalModel):
    def __init__(self,
                 model_path,
                 config=None,
                 device=None,
                 memory_limit=None,
                 precision=None,
                 force_sharding=True):
        processor: MllamaProcessor = MllamaProcessor.from_pretrained(model_path)
        self.config = config or MllamaConfig.from_pretrained(model_path)
        model = MllamaForConditionalGeneration.from_pretrained(
            model_path,
            torch_dtype=precision
        )

        processor = CustomProcessor(processor)

        vision_embed_size = model.vision_model.hidden_size
        super().__init__(model, processor, processor.tokenizer, device,
                         memory_limit, vision_embed_size=vision_embed_size, 
                         force_sharding=force_sharding, batch_images=False)

        self.model_name = "GenericLlama3"
        

class Llama3_11b_vision(GenericLlama3Vision):
    def __init__(self,
                 config=None,
                 device=None,
                 memory_limit=None,
                 precision=torch.bfloat16,
                 force_sharding=True):
        
        super().__init__(env.ModelPath.llama3_11b_vision,
                         config=config,
                         device=device,
                         memory_limit=memory_limit,
                         precision=precision,
                         force_sharding=force_sharding)
        
        self.model_name = "Llama3_11b"

class Llama3_90b_vision_instruct(GenericLlama3Vision):
    def __init__(self,
                 config=None,
                 device=None,
                 memory_limit=None,
                 precision=torch.bfloat16,
                 force_sharding=True):
        
        super().__init__(env.ModelPath.llama3_90b_vision_instruct,
                         config=config,
                         device=device,
                         memory_limit=memory_limit,
                         precision=precision,
                         force_sharding=force_sharding)
        
        self.model_name = "Llama3_90b"