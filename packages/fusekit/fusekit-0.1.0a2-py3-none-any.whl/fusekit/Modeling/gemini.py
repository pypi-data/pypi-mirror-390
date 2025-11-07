import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))


import tempfile
from fusekit.Modeling.api_model import APIModel, SystemPrompts
from fusekit.Datasets.extensions import APISample
from PIL import Image
from io import BytesIO
import base64
import yaml
from typing import Optional
from google import genai
from transformers import LlamaTokenizer 
import fusekit.Common.env as env
import warnings
from fusekit.Common.utils import APIKeyFile
from fusekit.Datasets import TextVisionSample, APICost
from transformers import MllamaProcessor
import io

os.environ.pop("GOOGLE_GENAI_USE_VERTEXAI", None)
os.environ.pop("GENAI_USE_VERTEXAI", None)

class _FilesAPI:
    def __init__(self, client):
        self._client = client

    def upload(self, file):
        # Always hand a real filesystem path to the SDK
        from pathlib import Path
        import tempfile
        if hasattr(file, "read"):
            with tempfile.NamedTemporaryFile(delete=False, suffix=".bin") as f:
                f.write(file.read())
                path = Path(f.name)
        else:
            path = Path(str(file))
        return self._client.files.upload(file=path)

class _ModelsAPI:
    """Thin wrapper over the v1 client models API (no global configure)."""
    def __init__(self, client):
        self._client = client

    def generate_content(self, model: str, contents, **kwargs):
        return self._client.models.generate_content(model=model, contents=contents, **kwargs)

class GeminiClientShim:
    """Mimics a minimal `client` with .files.upload and .models.generate_content."""
    def __init__(self, api_key: str):
        # Keep these to avoid the Vertex/RAG discovery path
        os.environ.pop("GOOGLE_GENAI_USE_VERTEXAI", None)
        os.environ.pop("GENAI_USE_VERTEXAI", None)

        # v1 unified client (no genai.configure)
        self._client = genai.Client(api_key=api_key)
        self.files = self._client.files                 # instance Files API
        self.models = _ModelsAPI(self._client)          # instance Models API

class GenericGemini(APIModel):
    """Common Gemini helpers that honor Tier 1 rate limits by default."""

    # https://ai.google.dev/gemini-api/docs/rate-limits#tier-1
    TIER1_LIMITS = {
        "gemini-1.5-pro": {"requests_per_minute": 2, "tokens_per_minute": 32_000},
        "gemini-1.5-flash-8b": {"requests_per_minute": 15, "tokens_per_minute": 1_000_000},
        "gemini-1.5-flash": {"requests_per_minute": 15, "tokens_per_minute": 1_000_000},
        "gemini-2.0-flash": {"requests_per_minute": 15, "tokens_per_minute": 1_000_000},
        "gemini-2.0-flash-lite": {"requests_per_minute": 15, "tokens_per_minute": 1_000_000},
        "gemini-2.5-pro": {"requests_per_minute": 2, "tokens_per_minute": 32_000},
        "gemini-2.5-flash": {"requests_per_minute": 15, "tokens_per_minute": 1_000_000},
        "gemini-2.5-flash-lite": {"requests_per_minute": 15, "tokens_per_minute": 1_000_000},
    }

    DEFAULT_TOKENS_PER_MINUTE = 800_000
    DEFAULT_REQUESTS_PER_MINUTE = 10

    def __init__(
        self,
        input_price: float = 0.0,
        output_price: float = 0.0,
        *,
        model_name: Optional[str] = None,
        mw: int = 10,
        rl: Optional[int] = None,
        tw: int = 60,
    ):
        limits = self.TIER1_LIMITS.get(
            model_name,
            {
                "requests_per_minute": self.DEFAULT_REQUESTS_PER_MINUTE,
                "tokens_per_minute": self.DEFAULT_TOKENS_PER_MINUTE,
            },
        )

        requests_per_minute = limits.get("requests_per_minute")
        tokens_per_minute = limits.get("tokens_per_minute")

        effective_workers = mw
        if requests_per_minute is not None:
            effective_workers = max(1, min(mw, requests_per_minute))

        if rl is None:
            effective_rate_limit = tokens_per_minute or self.DEFAULT_TOKENS_PER_MINUTE
        else:
            effective_rate_limit = (
                min(rl, tokens_per_minute)
                if tokens_per_minute is not None
                else rl
            )

        super().__init__(
            max_workers=effective_workers,
            rate_limit=effective_rate_limit,
            time_window=tw,
        )
        self.input_price = input_price
        self.output_price = output_price
        self.model_name = model_name

        self.api_key = APIKeyFile.parse(env.APIKeys.gemini)
        self.client = GeminiClientShim(self.api_key)

        self.chosen_model = "gemini"
        self.eval_sys_prompt = SystemPrompts.eval_sys_prompt

        self.processor = None

    def get_image_contents(self, sample):
        if sample.image_paths is not None:
            images = [Image.open(path) for path in sample.image_paths]

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

            with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmp:
                combined.save(tmp, format="PNG")
                return tmp.name  # absolute path to temp file

        raise ValueError("sample.image_paths is None; cannot build image contents.")

    
    def generate(self, sample: TextVisionSample, temperature=None):
        """
        Generate a response from Gemini given a sample containing text and an image.
        The method uploads the image file using Gemini's upload_file function,
        then calls generate_content with a list containing the image and text.
        
        Args:
            sample: A TextVisionSample with attributes 'text' and 'image_path'.
            temperature: (Optional) A temperature parameter (not used by Gemini in this example).
            
        Returns:
            A tuple (answer, cost) where cost is an APICost instance (here defaulted to zero).
        """

        if self.model_name is None:
            raise ValueError("GenericGemini model_name must be set before generate().")

        image_contents = self.get_image_contents(sample)

        uploaded_file = None
        response = None
        try:
            # Upload the image file. (Gemini requires the file to be uploaded first.)
            uploaded_file = self.client.files.upload(file=image_contents)

            response = self.client.models.generate_content(
                model=self.model_name,
                contents=[SystemPrompts.answer_question, uploaded_file, sample.prompt])
        finally:
            # Construct the content payload: image, then a couple of newlines, then the text.
            os.remove(image_contents)
            if uploaded_file is not None:
                try:
                    self.client.files.delete(name=uploaded_file.name)
                except Exception as delete_error:
                    warnings.warn(
                        f"Failed to delete uploaded file {uploaded_file.name}: {delete_error}",
                        RuntimeWarning,
                        stacklevel=2,
                    )

        if response is None:
            raise RuntimeError("Gemini generate_content returned no response")

        answer = response.text
        tokens_used = response.usage_metadata.total_token_count
        # Gemini currently does not provide token usage info.
        cost = APICost(response.usage_metadata.prompt_token_count * self.input_price,
                       response.usage_metadata.candidates_token_count * self.output_price)
        return answer, cost, tokens_used, response #dummy variable to let code work.

    def evaluate_answers(self, question, pred_answer, ground_truth):
        """
        Evaluate the given answers by constructing an evaluation prompt.
        
        Args:
            question: The original question.
            pred_answer: The predicted answer.
            ground_truth: The true answer.
        
        Returns:
            The evaluation result as text.
        """
        if self.model_name is None:
            raise ValueError("GenericGemini model_name must be set before evaluate_answers().")
        msg = (f"Question: {question}, Student Answer: {pred_answer}, "
               f"True Answer: {ground_truth}")
        model = genai.GenerativeModel(model_name=self.model_name)
        response = model.generate_content([self.eval_sys_prompt, "\n\n", msg])
        return response.text


class Gemini1p5_Pro(GenericGemini):
    def __init__(self):
        super().__init__(model_name="gemini-1.5-pro")

class Gemini1p5_Flash_8B(GenericGemini):
    def __init__(self):
        super().__init__(model_name="gemini-1.5-flash-8b")


class Gemini1p5_Flash(GenericGemini):
    def __init__(self):
        super().__init__(model_name="gemini-1.5-flash")

class Gemini2_Flash(GenericGemini):
    def __init__(self):
        super().__init__(model_name="gemini-2.0-flash")

class Gemini2p5_Pro(GenericGemini):
    INPUT_PRICE = 2.50 / 1_000_000
    OUTPUT_PRICE = 15.00 / 1_000_000

    def __init__(self, rate_limit: Optional[int] = None):
        super().__init__(
            Gemini2p5_Pro.INPUT_PRICE,
            Gemini2p5_Pro.OUTPUT_PRICE,
            model_name="gemini-2.5-pro",
            rl=rate_limit,
        )

class Gemini2p5_Flash(GenericGemini):
    INPUT_PRICE = 0.30 / 1_000_000
    OUTPUT_PRICE = 2.50 / 1_000_000

    def __init__(self, rate_limit: Optional[int] = None):
        super().__init__(
            Gemini2p5_Flash.INPUT_PRICE,
            Gemini2p5_Flash.OUTPUT_PRICE,
            model_name="gemini-2.5-flash",
            rl=rate_limit,
        )


class Gemini2p5_Flash_Lite(GenericGemini):
    INPUT_PRICE = 0.10 / 1_000_000
    OUTPUT_PRICE = 0.40 / 1_000_000

    def __init__(self, rate_limit: Optional[int] = None):
        super().__init__(
            Gemini2p5_Flash_Lite.INPUT_PRICE,
            Gemini2p5_Flash_Lite.OUTPUT_PRICE,
            model_name="gemini-2.5-flash-lite",
            rl=rate_limit,
        )

class Gemini2_Flash(GenericGemini):
    def __init__(self):
        super().__init__(model_name="gemini-2.0-flash")

class Gemini2_Flash_Lite(GenericGemini):
    def __init__(self):
        super().__init__(model_name="gemini-2.0-flash-lite")