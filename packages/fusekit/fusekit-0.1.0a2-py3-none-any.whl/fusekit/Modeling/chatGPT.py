import sys
import os
import fusekit.Common.env as env
from fusekit.Common.utils import APIKeyFile
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from fusekit.Modeling import APIModel, SystemPrompts
from fusekit.Datasets import TextVisionSample, APICost, GenerationSample
from openai import OpenAI
import base64
import io
from PIL import Image
from io import BytesIO
from transformers import LlamaTokenizer
from transformers import MllamaProcessor
from fusekit.Common.utils import APIKeyFile
import warnings
from pathlib import Path

class GenericChatGPT(APIModel):
    MAX_IMAGE_DIM = 2000 # Pixels
    MAX_IMAGE_SIZE = 50_000_000 # Bytes

    def __init__(self, input_price, output_price, tile_images=True, mw=10, rl=800_000, tw=60):
        super().__init__(max_workers=mw, rate_limit=rl, time_window=tw)
        self.input_price = input_price
        self.output_price = output_price
        self.tile_images = tile_images
                   
        self.org = APIKeyFile.parse(env.APIKeys.openai_org)
        self.api_key = APIKeyFile.parse(env.APIKeys.openai)
        self.client = OpenAI(api_key=self.api_key, organization=self.org)
        self.processor = None

        if not self.tile_images:
            print("WARNING: Image tiling has been disabled. To enable set tile_images=True")

    def encode_tile(self, tile, format):
        with io.BytesIO() as output:
            # Save each tile using an appropriate format
            tile.save(output, format=format)
            tile_bytes = output.getvalue()
            tile_encoded = base64.b64encode(tile_bytes).decode('utf-8')

            return tile_encoded

    def encode_image(self, image_path, debug=False):
        with open(image_path, "rb") as image:
            img = Image.open(image_path)

            width, height = img.size
            # If image is small enough, just encode once and return immediately.
            if not self.tile_images or width <= GenericChatGPT.MAX_IMAGE_DIM and height <= GenericChatGPT.MAX_IMAGE_DIM:
                img.close()
                with open(image_path, "rb") as f:
                    return [base64.b64encode(f.read()).decode("utf-8")]

            # Otherwise, tile the image
            tile_size = GenericChatGPT.MAX_IMAGE_DIM
            image_data = []

            if debug:
                debug_dir = Path("debug_tiles")
                debug_dir.mkdir(exist_ok=True)

            for y in range(0, height, tile_size):
                for x in range(0, width, tile_size):
                    # Define bounding box for each tile
                    box = (x, y, x + tile_size, y + tile_size)
                    tile = img.crop(box)

                    # (1) If debug, save tile to disk
                    if debug:
                        # e.g. image.jpg -> 'image' for stem
                        # Use original file stem + tile coords
                        stem = Path(image_path).stem
                        # Lowercase format to create consistent file extension
                        ext = img.format.lower() if img.format else 'png'
                        debug_filename = debug_dir / f"{stem}_tile_{y}_{x}.{ext}"
                        
                        tile.save(debug_filename)
                        print(f"[DEBUG] Saved tile to: {debug_filename}")

                    # (2) Encode the tile and append to our results
                    encoded_tile = self.encode_tile(tile, img.format)
                    image_data.append(encoded_tile)
            img.close()
        return image_data
    
    def parse_response(self, response):
        answer = response.choices[0].message.content
        cost = APICost(response.usage.prompt_tokens * self.input_price,
                       response.usage.completion_tokens * self.output_price)
        tokens = response.usage.total_tokens
        return answer, cost, tokens, response
    
    def get_image_contents(self, sample):
        image_contents = []

        if sample.image_paths is not None:
            for image_path in sample.image_paths:
                images = self.encode_image(image_path)

                for image in images:
                    image_contents.append({
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/jpeg;base64,{image}",
                            "detail": "high"
                        }
                    })

        # print((f'{len(image_contents)} image tiles'))
        return image_contents
    
    def run(self, messages):
        response = self.client.chat.completions.create(
            model=self.model_name,
            messages=messages
        )

        return self.parse_response(response)
    
    def generate_image(self, sample: GenerationSample, system_prompt):
        # Construct the messages payload for the API call.
        messages = [
            {"role": "user", "content": system_prompt},
            {"role": "user","content": [{"type": "text", "text": sample.prompt}]}
        ]

        return self.run(messages)
    
    def generate(self, sample: TextVisionSample, temperature=None):
        image_contents = self.get_image_contents(sample)        

        # Construct the messages payload for the API call.
        messages = [
            {"role": "user", "content": SystemPrompts.answer_question},
            {"role": "user","content": [
                {"type": "text", "text": sample.prompt},
                ] + image_contents}
        ]

        return self.run(messages)
        
    def llm_evaluate(self, sample: TextVisionSample, temperature=None): 
        msg=f'DESCRIPTION: "{sample.image_desc}",\n' + \
            f'QUESTION: "{sample.prompt}",\n' + \
            f'STUDENT ANSWER: "{sample.pred_text}",\n' + \
            f'CORRECT ANSWER: "{sample.answer}"\n' + \
            'GRADE: '
        
        messages = [
                {"role": "user", "content": SystemPrompts.eval_sys_prompt},  # Precondition prompt
                {"role": "user", "content": [{"type": "text", "text": msg}]},                     # Actual msg
                ]
        
        return self.run(messages)

    # def generate_image_description(self, sample: TextVisionSample):
    #     image_contents = self.get_image_contents(sample)  

    #     messages = [
    #             {"role": "user", "content": fusekit.Modeling.SystemPrompts.answer_question},  # Precondition prompt
    #             {"role": "user", "content": [
    #                 {"type": "text", "text": f'{sample.text} '}
    #                 ] + image_contents},                     # Actual msg
    #             ]
        
    #     return self.run(messages)


# Subclasses simply set the model name and instantiate without parameters.
class GPT4o(GenericChatGPT):
    INPUT_PRICE = 2.50 / 1_000_000
    OUTPUT_PRICE = 10.00 / 1_000_000

    def __init__(self, tile_images=True, rate_limit=800_000):
        super().__init__(GPT4o.INPUT_PRICE, GPT4o.OUTPUT_PRICE, tile_images=tile_images, rl=rate_limit)
        self.model_name = "gpt-4o"

class GPT4p1(GenericChatGPT):
    INPUT_PRICE = 2.00 / 1_000_000
    OUTPUT_PRICE = 8.00 / 1_000_000

    def __init__(self, tile_images=True, rate_limit=800_000):
        super().__init__(GPT4p1.INPUT_PRICE, GPT4p1.OUTPUT_PRICE, tile_images=tile_images, rl=rate_limit)
        self.model_name = "gpt-4.1"
        
class GPT4o_mini(GenericChatGPT):
    INPUT_PRICE = 0.15 / 1_000_000
    OUTPUT_PRICE = 0.60 / 1_000_000

    def __init__(self, tile_images=True, rate_limit=4_000_000):
        super().__init__(GPT4o_mini.INPUT_PRICE, GPT4o_mini.OUTPUT_PRICE, tile_images=tile_images, rl=rate_limit)
        self.model_name = "gpt-4o-mini"

class GPTo1(GenericChatGPT):
    INPUT_PRICE = 15.00 / 1_000_000
    OUTPUT_PRICE = 60.00 / 1_000_000

    def __init__(self, tile_images=True, rate_limit=5000):
        super().__init__(GPTo1.INPUT_PRICE, GPTo1.OUTPUT_PRICE, tile_images=tile_images, rl=rate_limit)
        self.model_name = "o1"

class GPTo3(GenericChatGPT):
    INPUT_PRICE = 2.00 / 1_000_000
    OUTPUT_PRICE = 8.00 / 1_000_000

    def __init__(self, tile_images=True, rate_limit=5000):
        super().__init__(GPTo3.INPUT_PRICE, GPTo3.OUTPUT_PRICE, tile_images=tile_images, rl=rate_limit)
        self.model_name = "o3"

class GPTo1_preview(GenericChatGPT):
    def __init__(self, tile_images=True, rate_limit=500):
        super().__init__(GPTo1.INPUT_PRICE, GPTo1.OUTPUT_PRICE, tile_images=tile_images, rl=rate_limit)
        self.model_name = "o1-preview"

class GPTo1_mini(GenericChatGPT):
    INPUT_PRICE = 1.10 / 1_000_000
    OUTPUT_PRICE = 4.40 / 1_000_000

    def __init__(self, tile_images=True, rate_limit=4_000_000):
        super().__init__(GPTo1_mini.INPUT_PRICE, GPTo1_mini.OUTPUT_PRICE, tile_images=tile_images, rl=rate_limit)
        self.model_name = "o1-mini"

class GPTo3_mini(GenericChatGPT):

    def __init__(self, tile_images=True, rate_limit=4_000_000):
        super().__init__(GPTo1_mini.INPUT_PRICE, GPTo1_mini.OUTPUT_PRICE, tile_images=tile_images, rl=rate_limit)
        self.model_name = "o3-mini"

class GPTo4_mini(GenericChatGPT):

    def __init__(self, tile_images=True, rate_limit=4_000_000):
        super().__init__(GPTo1_mini.INPUT_PRICE, GPTo1_mini.OUTPUT_PRICE, tile_images=tile_images, rl=rate_limit)
        self.model_name = "o4-mini"

class GPTImage1(GenericChatGPT):
    INPUT_PRICE = 5.00 / 1_000_000
    OUTPUT_PRICE = 0.00 

    def __init__(self, rate_limit=2_000_000):
        super().__init__(GPTImage1.INPUT_PRICE, GPTImage1.OUTPUT_PRICE, rl=rate_limit)
        self.model_name = 'GPT-Image-1'

class GPT5(GenericChatGPT):
    INPUT_PRICE = 1.25 / 1_000_000
    OUTPUT_PRICE = 10.00 / 1_000_000

    def __init__(self, tile_images=True, rate_limit=4_000_000):
        super().__init__(GPT5.INPUT_PRICE, GPT5.OUTPUT_PRICE, tile_images=tile_images, rl=rate_limit)
        self.model_name = "gpt-5"

class GPT5_mini(GenericChatGPT):
    INPUT_PRICE = 0.25 / 1_000_000
    OUTPUT_PRICE = 2.00 / 1_000_000

    def __init__(self, tile_images=True, rate_limit=4_000_000):
        super().__init__(GPT5_mini.INPUT_PRICE, GPT5_mini.OUTPUT_PRICE, tile_images=tile_images, rl=rate_limit)
        self.model_name = "gpt-5-mini"

class GPT5_nano(GenericChatGPT):
    INPUT_PRICE = 0.05 / 1_000_000
    OUTPUT_PRICE = 0.40 / 1_000_000

    def __init__(self, tile_images=True, rate_limit=4_000_000):
        super().__init__(GPT5_nano.INPUT_PRICE, GPT5_nano.OUTPUT_PRICE, tile_images=tile_images, rl=rate_limit)
        self.model_name = "gpt-5-nano"