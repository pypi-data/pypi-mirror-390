import fusekit.Common.env as env
import torch
from transformers import LlamaTokenizer, LlamaConfig, LlamaForCausalLM

from .causal_model import CausalModel

class GenericLlama2(CausalModel):
    def __init__(self,
                 model_path,
                 config=None,
                 device=None,
                 memory_limit=None,
                 precision=None,
                 force_sharding=True):
        tokenizer: LlamaTokenizer = LlamaTokenizer.from_pretrained(model_path)
        tokenizer.add_special_tokens({"pad_token":"<pad>"})

        self.config = config or LlamaConfig.from_pretrained(model_path)
        model = LlamaForCausalLM.from_pretrained(model_path,
                                                 torch_dtype=precision,
                                                 config=self.config)
        
        # self.config.pad_token_id = tokenizer.pad_token_id
        
        # model.resize_token_embeddings(len(tokenizer))

        super().__init__(model, None, tokenizer,
                         device=device,
                         memory_limit=memory_limit, 
                         force_sharding=force_sharding)
        
        orig_generate = model.generate
        def patched_generate(*args, **kwargs):
            kwargs.setdefault("pad_token_id", tokenizer.eos_token_id)
            return orig_generate(*args, **kwargs)
        model.generate = patched_generate

    def save_model(self, checkpoint, save_path=None):
        checkpoint['parameters'] = {k:v 
                                    for k,v in self.model.named_parameters()
                                    if v.requires_grad}
        super().save_model(checkpoint, save_path=save_path)


class Llama2_7b(GenericLlama2):
    def __init__(self, 
                 config=None,
                 device=None,
                 memory_limit=None,
                 precision=torch.bfloat16,
                 force_sharding=True):
        
        super().__init__(env.ModelPath.llama2_7b, 
                         config=config, 
                         device=device,
                         memory_limit=memory_limit,
                         precision=precision, 
                         force_sharding=force_sharding)
        
        self.model_name = "Llama2_7b"