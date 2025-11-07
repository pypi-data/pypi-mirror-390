import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from fusekit.Modeling.api_model import APIModel, SystemPrompts
from fusekit.Datasets.extensions import APISample
from anthropic import Anthropic
from PIL import Image
try:
    RESAMPLE_LANCZOS = Image.Resampling.LANCZOS  # Pillow >= 10
except AttributeError:
    RESAMPLE_LANCZOS = Image.LANCZOS
from io import BytesIO
import base64
from transformers import LlamaTokenizer
from fusekit.Common.utils import APIKeyFile
import warnings
from fusekit.Datasets import TextVisionSample, APICost
from pathlib import Path
from transformers import MllamaProcessor
import io
import fusekit.Common.env as env

class GenericClaude(APIModel):
    MAX_IMAGE_DIM = 1092 # Pixels
   
    def __init__(self, input_price, output_price, tile_images=True, mw=10, rl=40_000, tw=60):
        super().__init__(max_workers=mw, rate_limit=rl, time_window=tw)
        self.input_token_price = input_price
        self.output_token_price = output_price
        self.org = APIKeyFile.parse(env.APIKeys.claude_org)
        self.api_key = APIKeyFile.parse(env.APIKeys.claude)
        self.client = Anthropic(
    api_key=APIKeyFile.parse(env.APIKeys.claude),
    # anthropic_version="2023-06-01"
)
        # self.chosen_model = "claude"
        self.model_name = None
        self.tile_images=tile_images
        self.processor = None
    
    def encode_tile(self, tile, format):
        with io.BytesIO() as output:
            # Save each tile using an appropriate format
            tile.save(output, format=format)
            tile_bytes = output.getvalue()
            tile_encoded = base64.b64encode(tile_bytes).decode('utf-8')

            return tile_encoded
        
    def encode_image(self, image_path, debug=False):
        if not os.path.exists(image_path):
            print(f"Error: Image file does not exist: {image_path}")
            return []

        img = Image.open(image_path).convert("RGB")
        img.thumbnail((self.MAX_IMAGE_DIM, self.MAX_IMAGE_DIM), RESAMPLE_LANCZOS)

        buf = BytesIO()
        img.save(buf, format="JPEG")
        data = base64.b64encode(buf.getvalue()).decode("utf-8")
        img.close()
        return [data]
        
        # try:
        #     print(f"Processing image: {image_path}")
            
        #     if not os.path.exists(image_path):
        #         print(f"Error: Image file does not exist: {image_path}")
        #         return []
                
        #     img = Image.open(image_path)
        #     width, height = img.size
        #     print(f"Image dimensions: {width}x{height}")
            
        #     # If image is small enough, just encode once and return immediately
        #     if not self.tile_images or (width <= self.MAX_IMAGE_DIM and height <= self.MAX_IMAGE_DIM):
        #         print("Image small enough, encoding directly")
        #         with open(image_path, "rb") as f:
        #             encoded = base64.b64encode(f.read()).decode("utf-8")
        #         img.close()
        #         return [encoded]

        #     # Otherwise, tile the image
        #     print("Image too large, tiling...")
        #     tile_size = self.MAX_IMAGE_DIM
        #     image_data = []

        #     if debug:
        #         debug_dir = Path("debug_tiles")
        #         debug_dir.mkdir(exist_ok=True)

        #     tile_count = 0
        #     max_tiles = 20  # Safety limit to prevent memory issues
            
        #     for y in range(0, height, tile_size):
        #         for x in range(0, width, tile_size):
        #             if tile_count >= max_tiles:
        #                 print(f"Warning: Reached maximum tile limit ({max_tiles}), stopping")
        #                 break
                        
        #             # Calculate proper bounds
        #             x_end = min(x + tile_size, width)
        #             y_end = min(y + tile_size, height)
                    
        #             # Skip if tile would be too small
        #             if (x_end - x) < 50 or (y_end - y) < 50:
        #                 continue
                        
        #             box = (x, y, x_end, y_end)
        #             print(f"Creating tile {tile_count + 1}: box={box}")
                    
        #             try:
        #                 tile = img.crop(box)
                        
        #                 if debug:
        #                     stem = Path(image_path).stem
        #                     ext = img.format.lower() if img.format else 'png'
        #                     debug_filename = debug_dir / f"{stem}_tile_{y}_{x}.{ext}"
        #                     tile.save(debug_filename)
        #                     print(f"[DEBUG] Saved tile to: {debug_filename}")

        #                 encoded_tile = self.encode_tile(tile, img.format or 'JPEG')
        #                 if encoded_tile:  # Only add if encoding succeeded
        #                     image_data.append(encoded_tile)
        #                     tile_count += 1
                        
        #                 # Clean up tile to prevent memory issues
        #                 tile.close()
                        
        #             except Exception as tile_error:
        #                 print(f"Error processing tile at {box}: {tile_error}")
        #                 continue
                        
        #         if tile_count >= max_tiles:
        #             break
                    
        #     img.close()
        #     print(f"Created {len(image_data)} tiles")
        #     return image_data
            
        # except Exception as e:
        #     print(f"Error encoding image {image_path}: {e}")
        #     import traceback
        #     traceback.print_exc()
        #     return []

    def get_image_contents(self, sample):
        image_contents = []

        if sample.image_paths is not None:
            for image_path in sample.image_paths:
                images = self.encode_image(image_path)

                for image in images:
                    image_contents.append({
                        "type": "image",
                        "source": {
                            "type": "base64",
                            "media_type": "image/jpeg",
                            "data": image, 
                            # "detail": "high"
                        }
                    })


        # print((f'{len(image_contents)} image tiles'))
        return image_contents
    def generate(self, sample: TextVisionSample, temperature=None):
        """
        Generate a response given a sample containing text and an image.
        """
        image_data=self.get_image_contents(sample)

        try:
            image_data = self.get_image_contents(sample)
            messages = [
                {"role": "user", "content": SystemPrompts.answer_question},
                {"role": "user", "content": [{"type": "text", "text": sample.prompt}] + image_data,}
            ]

            response = self.client.messages.create(
                model=self.model_name,
                max_tokens=800,
                messages=messages,
                temperature=temperature or 0.0
            )

            if isinstance(response.content, list):
                answer = "".join(
                    (getattr(block, "text", "") + "\n")
                    for block in response.content
                    if hasattr(block, "text")
                ).strip()
            else:
                answer = response.content

            in_toks  = getattr(getattr(response, "usage", None), "input_tokens", 0)
            out_toks = getattr(getattr(response, "usage", None), "output_tokens", 0)

            # If you don’t have prices defined, set them to 0.0 in __init__
            cost = APICost(
                input_cost=in_toks * self.input_token_price,
                output_cost=out_toks * self.output_token_price
            )

            return answer, cost, in_toks + out_toks, response

        except Exception as e:
            print(f"Claude generate() failure: {e}", flush=True)
            # Return empty answer but still an APICost object so reducers don’t explode
            return "", APICost(0.0, 0.0), 0
    

    def llm_evaluate(self, sample: TextVisionSample, temperature=None):
        msg = (f"Question: {sample.prompt}, Student Answer: {sample.pred_text}, "
            f"True Answer: {sample.answer}")
        response = self.client.messages.create(
            model=self.model_name,
            max_tokens=800,
            messages=[
                {"role": "system", "content": self.eval_sys_prompt},
                {"role": "user", "content": msg}
            ],
            temperature=temperature or 0.0
        )
        if isinstance(response.content, list):
            answer = "".join(
                (getattr(block, "text", "") + "\n")
                for block in response.content
                if hasattr(block, "text")
            ).strip()
        else:
            answer = response.content

        in_toks  = getattr(getattr(response, "usage", None), "input_tokens", 0)
        out_toks = getattr(getattr(response, "usage", None), "output_tokens", 0)
        cost = APICost(in_toks * self.input_token_price,
                    out_toks * self.output_token_price)
        return answer, cost, in_toks + out_toks, response

    def evaluate_answers(self,question,pred_answer,ground_truth):
        try:
            msg = (
                f"Question: {question}\n"
                f"Student Answer: {pred_answer}\n"
                f"True Answer: {ground_truth}"
            )

            response = self.client.messages.create(
                model=self.model_name,
                max_tokens=800,
                system=getattr(self, "eval_sys_prompt", ""),  # OK if empty
                messages=[{"role": "user", "content": msg}],
                temperature=temperature or 0.0,
            )

            # Extract text from Claude response
            if isinstance(response.content, list):
                answer = "".join(
                    (getattr(block, "text", "") + "\n")
                    for block in response.content
                    if hasattr(block, "text")
                ).strip()
            else:
                answer = response.content

            # Token usage -> APICost
            in_toks  = getattr(getattr(response, "usage", None), "input_tokens", 0)
            out_toks = getattr(getattr(response, "usage", None), "output_tokens", 0)
            cost = APICost(
                input_cost=in_toks  * getattr(self, "input_token_price", 0.0),
                output_cost=out_toks * getattr(self, "output_token_price", 0.0),
            )

            return answer, cost, in_toks + out_toks

        except Exception as e:
            print(f"Claude evaluate_answers() failure: {e}", flush=True)
            # Never return None here — keeps your reducers happy
            return "", APICost(0.0, 0.0), 0


class Claude3p5_Sonnet(GenericClaude):
    def __init__(self):
        super().__init__()
        self.model_name = "claude-3-5-sonnet-20241022"

class Claude3p5_Haiku(GenericClaude):
    INPUT_PRICE = 0.80 / 1_000_000
    OUTPUT_PRICE = 4.00 / 1_000_000

    def __init__(self, tile_images=True, rate_limit=100_000):
        super().__init__(self.INPUT_PRICE, self.OUTPUT_PRICE, tile_images=tile_images, rl=rate_limit)
        self.model_name = "claude-3-5-haiku-20241022"
        
class Claude3p7_Sonnet(GenericClaude):
    def __init__(self):
        super().__init__()
        self.model_name = "claude-3-7-sonnet-20250219"

class Claude3_Opus(GenericClaude):
    def __init__(self):
        super().__init__()
        self.model_name = "claude-3-opus-20240229"

class Claude3_Sonnet(GenericClaude):
    def __init__(self):
        super().__init__()
        self.model_name = "claude-3-sonnet-20240229"

class Claude3_Haiku(GenericClaude):
    def __init__(self):
        super().__init__()
        self.model_name = "claude-3-haiku-20240307"

class Claude4_Opus(GenericClaude):
    INPUT_PRICE = 15.00 / 1_000_000
    OUTPUT_PRICE = 75.00 / 1_000_000

    def __init__(self, tile_images=True, rate_limit=450_000):
        super().__init__(Claude4_Opus.INPUT_PRICE, Claude4_Opus.OUTPUT_PRICE, tile_images=tile_images, rl=rate_limit)
        self.model_name = 'claude-opus-4-20250514'

class Claude4_Sonnet(GenericClaude):
    INPUT_PRICE = 3.00 / 1_000_000
    OUTPUT_PRICE = 15.00 / 1_000_000

    def __init__(self, tile_images=True, rate_limit=450_000):
        super().__init__(Claude4_Sonnet.INPUT_PRICE, Claude4_Sonnet.OUTPUT_PRICE, tile_images=tile_images, rl=rate_limit)
        self.model_name = 'claude-sonnet-4-20250514'