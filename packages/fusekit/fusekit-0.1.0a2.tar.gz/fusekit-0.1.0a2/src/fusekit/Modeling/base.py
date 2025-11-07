import os, copy, torch
from pathlib import Path

# from fusekit.Datasets import IterableDataset
from transformers import PreTrainedModel, ProcessorMixin, PreTrainedTokenizer
from fusekit.Datasets import IterableDataset, APICost
from typing import List
from tqdm import tqdm
from abc import ABC, abstractmethod

import fusekit.Common.env as env
import fusekit.Common.utils as utils

class GenericModel(ABC):
    def __init__(self):
        self.model_name = 'GenericModel'

    # def evaluate(self, datasets: list):
    #     raise NotImplementedError
        
    @staticmethod
    def parse_device(device) -> list | None:
        if device:
            device_list = [device] if isinstance(device, int) else device
        else:
            device_list = None
        return device_list
    
    def evaluate(self, datasets: List[IterableDataset] | IterableDataset, llm_judge=None, save_file=None, skip_generation=False):
        if not isinstance(datasets, list):
            datasets = [datasets]
        for dataset in datasets:
            self.evaluate_dataset(dataset, llm_judge=llm_judge, save_file=save_file, skip_generation=skip_generation)

    def evaluate_dataset(self, dataset: IterableDataset, llm_judge=None, save_file=None, skip_generation=False):
        self.evaluate_options(dataset, skip_generation, llm_judge)

        if save_file is not None:
            save_file = f'answerer_{self.model_name}_llmjudge_{llm_judge.model_name}_{len(dataset)}' + save_file if llm_judge is not None else save_file
            os.makedirs(env.results / 'temp', exist_ok=True)
            self.save_dataset(dataset, save_file)

    def evaluate_options(self, dataset, skip_generation, llm_judge):
        raise NotImplementedError
    
    def judge_answers(self, dataset, llm_judge):
        raise NotImplementedError
    
    def save_dataset(self, dataset: IterableDataset, save_file):
        save_folder = env.results / self.model_name
        dataset.dump_inference(save_folder / save_file)

class CustomProcessor(ProcessorMixin):
    def __init__(self, base_processor:ProcessorMixin):
        self.__dict__ = copy.copy(base_processor.__dict__)
        self.base_processor = base_processor

    def __call__(self, *args, **kwargs):
        return self.base_processor.__call__(*args, **kwargs)

    def format_message(self, text):
        return {"role": "user", "content": [
                {"type": "image"},
                {"type": "text", "text": text}
            ]}
    
class APIModelBase(GenericModel):
    def __init__(self):
        super().__init__()
        self.model_name = 'APIModelBase'


class CausalModelBase(PreTrainedModel, GenericModel):
    def __init__(self, 
                 model: PreTrainedModel, 
                 processor: ProcessorMixin|None,
                 tokenizer: PreTrainedTokenizer,
                 device: list[int]|int|None,):
        super().__init__(model.config)
        self.model_name = 'CausalModelBase'
        self.model = model
        self.processor = processor
        self.tokenizer = tokenizer

    def sanitize(self):
        pass

    def update(self):
        pass

    def save_model(self, checkpoint, save_path=None):
        checkpoint['parameters'] = {k:v for k,v in self.model.named_parameters() if v.requires_grad}

        if save_path is not None:  # save to a different location
            save_path = Path(save_path)
            if save_path.exists():
                if input("Existing file found! Overwrite? [y/N] ").strip().lower() != "y":
                    print("Aborted! Checkpoint not saved")
                save_path.stem = input("Enter filename: ")
            torch.save(checkpoint, save_path)
            print(f'Saving to location: {save_path}')

class SystemPrompts:
    def gen_question(example_file, num_questions=30):
        prompt =    "You are an expert cartographer, and you need to build a set of questions to test map understanding " + \
                    "knowledge. Come up with difficult questions based only on the map provided. You may only " + \
                    "use information present in the map itself, no external knowledge related to the history of the event in " + \
                    "question. For example, prior knowledge of history, locations, geography, or other information cannot be leveraged in " + \
                    "answering questions. The questions should require the answerer to reference only the map. Ask questions that require critical thinking and expert levels of " + \
                    "understanding of the map, instead of reading text. Avoid counting questions where the answer is " + \
                    "greater than 10. Avoid using cardinal directions unless an indiciation of North is made on the map. If there is " + \
                    "no indication of cardinality, use right, left, top, and bottom of the map instead. Ensure that the questions " + \
                    "are not tautological, e.g., the answer is in the question itself. Finally, verify that if you " + \
                    "say something is to the right of something else, that it can in fact be found in the area specified. The questions " + \
                    "must be answerable based only the on map presented, and not be questions about content that exists beyond the map. " + \
                    "For all questions that you generate should be answerable in theory. Don't ask how questions.\n" + \
                    f"Generate {num_questions} questions that are answerable by only looking at the map.\n" + \
                    "Below is a list of 50 example questions with description of the map pertaining to the question. " + \
                    "Output only the questions a jsonl file where each line looks like:\n" + \
                    "{\"Question\": \"generated_question\"}\n" + \
                    "\nEXAMPLES:\n\n"
        
        data = utils.jsonl.read(example_file)
        
        examples = ""
        for example in data:
            examples += str(example) + "\n"

        return prompt + examples

    eval_sys_prompt = \
        "Evaluate the answer of a student to a question. You will be provided with " + \
        "the question, a student's answer, and the correct answer. Your task is " + \
        "to evaluate the student’s response and determine whether it is Correct or " + \
        "Incorrect. Grade the student answers based ONLY on their factual accuracy. " + \
        "It is OK if the student answer contains more information than the true " + \
        "answer, as long as it is relatively succinct. " + \
        "Ignore differences in punctuation, capitalization, and phrasing " + \
        "between the student’s answer and the true answer. Be lenient, but if the student lists all possible answers, " + \
        "mark the answer incorrect. You may use the description of the image to infer if the student and correct " + \
        "describe the same thing. For example, a WW2 map from the US perspective may have a correct answer enemy and " + \
        "and the student says Germany; this would still be correct. For instances where the answer is a measurement, " + \
        "accept answers within 10\% of the correct answer. For instances when the correct answer is a range of measurements, " + \
        "accept the student answer if it falls within that range. Example Format:\n" + \
        "DESCRIPTION: \"[description here]\",\n" + \
        "QUESTION: \"[question here]\",\n" + \
        "STUDENT ANSWER: \"[student's answer here]\",\n" + \
        "CORRECT ANSWER: \"[correct answer here]\",\n" + \
        "GRADE: [Correct or Incorrect here]\n" + \
        "The correct answer may contain multiple versions of the same correct answer. If the student matches one then it is correct" + \
        "Your response should include only the verdict without any justification or reasoning. " + \
        "Only answer either Correct or Incorrect, no other additional words. "

    image_tile_description = \
        "Images presented are tiles from one single image. " + \
        "The tiles are presented from top to bottom, left to " + \
        "right. Tiles are padded with black pixels.\n"

    answer_question = \
        image_tile_description + "Answer the " + \
        "question considering all image tiles. Your answers should be relatively concise. "
    
    describe_image = \
        "Very briefly describe this image. "
    
    locate_image = \
        "Give a general location for this image in as few words as possible. Do not use periods. If the image is of an imaginary location, respond with only the word 'None'"
