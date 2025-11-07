import torch
from transformers import PreTrainedTokenizer, ProcessorMixin
from fusekit.Datasets import SpecialTokens
from fusekit.Datasets import GenericSample, GenerationSample, APICost
import sys 
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
import fusekit.Common.utils as utils

from PIL import Image
from io import BytesIO
import base64

class TextVisionSample(GenerationSample):
    def __init__(self, processor: ProcessorMixin, image_paths, image_desc,
                 text, label, max_new_tokens=0, uid=None, preload=True):
        tokenizer = None if processor is None else processor.tokenizer
        super().__init__(tokenizer, text, label,
                         max_new_tokens=max_new_tokens, uid=uid, preload=preload)
        self.processor = processor
        self.image_paths = image_paths
        self.image_desc = image_desc
        self.image=True
        self.input_text = None
        self.image_ctx = None
        self.processed_input = None

    def __repr__(self):
        api_cost = repr(self.eval_cost) if isinstance(self.eval_cost, APICost) else "No Cost Information"

        return f"Text: {self.prompt}\n" + \
               f"Label: {self.answer}\n" + \
               f"Image: {self.image_paths}\n" + \
               f"Image Description: {self.image_desc}\n" + \
               f"Prediction: {self.pred_text}\n" + \
               f"LLM Eval: {self.llm_eval}\n" + \
               api_cost

    def get_input_text(self):
        if self.input_text is None:
            formatted_text = [self.processor.format_message(self.prompt)]

            self.input_text = self.processor.apply_chat_template(
                formatted_text, add_generation_prompt=True)
        return self.input_text

    def _get_image_contents(self):
        images=[Image.open(image_path) for image_path in self.image_paths]

        # Determine final image size
        total_width = sum(img.width for img in images)
        max_height = max(img.height for img in images)
        
        # Create a new image with enough space
        combined = Image.new("RGB", (total_width, max_height), color=(255, 255, 255))
        
        # Paste each image side-by-side (top-aligned)
        x_offset = 0
        for img in images:
            combined.paste(img, (x_offset, 0))
            x_offset += img.width
        return combined
        
    def get_processed_input(self):
        if self.processed_input is None:
            
            
            image=self._get_image_contents()
            
            self.processed_input = self.processor(image, 
                                       self.get_input_text(),
                                       padding=True,   
                                       add_special_tokens=False,
                                       return_tensors="pt")

        return self.processed_input

    def get_inputs(self):
        if self.inputs is None:
            self.inputs = self.get_processed_input()['input_ids']
        return self.inputs
                    
    def get_image_ctx(self):
        if self.image_ctx is None:
            self.image_ctx = list(self.get_processed_input().items())[2:]
        return self.image_ctx


class MultiChoiceQA(GenericSample):
    LABELS = ['A. ', 'B. ', 'C. ', 'D. ', 'E. ']

    def __init__(self, tokenizer: PreTrainedTokenizer,
                 uid, question, options, label, label_idx):
        super().__init__(tokenizer=tokenizer)
        self.uid = uid
        self.question = question
        self.options = options
        self.label_text = label
        self.label_idx = label_idx
        self.sample_width = len(options)
        self.loglikelihood = [None] * self.sample_width

    def get_text(self, show_label=False, spt=SpecialTokens()) -> str:
        # <s> [CLS] self.question [SEP] self.options [SEP] self.label </s>
        text = f'{self.question}' + '\n'
        text += '\n'.join(self.options) + '\n'
        if show_label:
            text += f'Answer: {self.label_text[0]}' + '\n'
        else:
            text = [f'{text}Answer: {candidate[0]}' + '\n' 
                    for candidate in self.options]
        return text

    def get_inputs(self) -> torch.Tensor:
        if self.inputs is None:
            candidates = self.get_text()
            inputs = [self.tokenizer.encode(candidate)
                           for candidate in candidates]
            inputs = utils.padding.right(inputs)
            self.inputs = torch.tensor(inputs, dtype=torch.long)
        return self.inputs
    
    def get_labels(self) -> torch.Tensor:
        if self.labels is None:
            labels = self.tokenizer.encode(self.get_text(show_label=True))
            self.labels = torch.tensor(labels, dtype=torch.long).unsqueeze(0)
        return self.labels
    
    def get_accuracy(self):
        if any(loglikelihood is None for loglikelihood in self.loglikelihood):
            raise ValueError("Log-likelihood values are not fully computed.")
        
        predicted_idx = self.loglikelihood.index(max(self.loglikelihood))
        return {"Accuracy": 1.0 if predicted_idx == self.label_idx else 0.0}

@DeprecationWarning
class APISample(GenerationSample):
    def __init__(self, processor: ProcessorMixin, image,
                 text, label, api_name, max_new_tokens=0,
                 max_size=(1568, 1568),     # Max width x height for claude
                 target_size=5_242_880,     # ~5 MB in bytes (5 * 1024 * 1024 = 5,242,880) for claude
                 max_iterations=7           #for claude
                 ):
        
        super().__init__(processor.tokenizer, text, label,
                         max_new_tokens=max_new_tokens)
        
        self.image_path = image
        self.text = text

        self.max_size=max_size
        self.target_size=target_size
        self.max_iterations=max_iterations
        self.api_name=api_name

    
    def get_image(self):
        
        return self.encode_image()

    def get_inputs(self):
        question=self.get_text()
        image=self.get_image()
        return (question,image)
                    
    def encode_image(self):
        if self.api_name=="claude":
            image=self.resize_and_compress_image()
        elif self.api_name=="gemeni":
            return self.image_path
        else:
            with open(self.image_path, "rb") as image_file:
                image=image_file.read()

        return base64.b64encode(image).decode('utf-8')
            

    def resize_and_compress_image(self):
        """
        Resizes and compresses an image to meet API requirements.
        """
        with Image.open(self.image_path) as img:
            # Convert to RGB if needed
            if img.mode != "RGB":
                img = img.convert("RGB")

            
            img.thumbnail(self.max_size)

            low_q, high_q = 1, 100
            best_q = None
            best_img_bytes = None

            for _ in range(self.max_iterations):
                mid_q = (low_q + high_q) // 2

                buffer = BytesIO()
                img.save(buffer, format="JPEG", quality=mid_q)
                size_now = buffer.tell()

                if size_now <= self.target_size:
                    
                    best_q = mid_q
                    best_img_bytes = buffer.getvalue()
                    low_q = mid_q + 1
                else:
                    high_q = mid_q - 1

                if low_q > high_q:
                    
                    break

            # If we never got under target_size, best_img_bytes remains None
            if best_img_bytes is None:
                final_q = min(low_q, high_q)
                buffer = BytesIO()
                img.save(buffer, format="JPEG", quality=final_q)
                best_img_bytes = buffer.getvalue()
            else:
              
                buffer = BytesIO()
                img.save(buffer, format="JPEG", quality=best_q)
                best_img_bytes = buffer.getvalue()
                
            return base64.b64encode(best_img_bytes).decode('utf-8')