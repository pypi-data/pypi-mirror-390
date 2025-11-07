import sys
import os
import json
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from fusekit.Common.utils import APIKeyFile, jsonl
import fusekit.Common.env as env

from fusekit.Common.EvalType import EvalType as EvalType
from transformers import AutoTokenizer
import yaml  
from typing import List, Dict, Any, Optional
from abc import ABC, abstractmethod
from fusekit.Common.multithread import APIThreadPool
from fusekit.Modeling.base import APIModelBase, GenericModel, SystemPrompts
from fusekit.Datasets.core import IterableDataset
from fusekit.Datasets import TextVisionSample, APICost, GenerationSample
from tqdm import tqdm
import torch
import pickle

class APIModel(APIModelBase):
    def __init__(self, max_workers=4, rate_limit=5000, time_window=60):
        super().__init__()
        self.eval_sys_prompt=SystemPrompts.eval_sys_prompt
        self.thread_pool = APIThreadPool(max_workers=max_workers, 
                                         rate_limit=rate_limit, 
                                         time_window=time_window)
        try:
            self.tokenizer = AutoTokenizer.from_pretrained(env.ModelPath.llama3_11b_vision)
            if self.tokenizer.pad_token is None:
                self.tokenizer.pad_token = self.tokenizer.eos_token
        except Exception as e:
            print(f"Failed to initialize tokenizer: {e}")
            raise
    
    def tokenize_response(self, text: str) -> torch.Tensor:
        """Tokenize response text using the Llama tokenizer"""
        encoded = self.tokenizer.encode(
            text,
            add_special_tokens=False,
            return_tensors="pt"
        )
        return encoded.squeeze()

    def decode_tokens(self, tokens: torch.Tensor) -> str:
        """Decode tokens back to text"""
        return self.tokenizer.decode(tokens, skip_special_tokens=True)
    
    def generate(self, sample: TextVisionSample):
        raise NotImplementedError
    
    def llm_evaluate(self, sample: GenerationSample):
        raise NotImplementedError
    
    def inference(self, datasets: List[IterableDataset] | IterableDataset, save_file=None):
        if not isinstance(datasets, list):
            datasets = [datasets]
        for dataset in datasets:
            self.inference_dataset(dataset, save_file=save_file)

    def inference_dataset(self, dataset: IterableDataset, save_file=None):
        with tqdm(total=len(dataset), desc='Inferencing Question', unit="sample") as pbar:
            for i in range(0, len(dataset), self.thread_pool.max_workers):
                batch = dataset[i:i + self.thread_pool.max_workers]
                self.thread_pool.process_batch(batch, self._generate)
                with open(env.results / 'temp/MapDesc_Temp.pkl', 'wb') as f:
                    pickle.dump(dataset, f)
                pbar.update(len(batch))

        if save_file is not None:
            save_file = f'describer_{self.model_name}_{len(dataset)}' + save_file
            self.save_dataset(dataset, save_file)

        total_cost = APICost(0.0, 0.0)
        for sample in dataset:
            total_cost += sample.eval_cost

        print(total_cost)
        
    def evaluate_options(self, dataset: IterableDataset, skip_generation, llm_judge):
        temp_dir = env.results / 'temp'
        temp_dir.mkdir(parents=True, exist_ok=True)
        if not skip_generation:
            with tqdm(total=len(dataset), desc='Generating Samples', unit="sample") as pbar:
                for i in range(0, len(dataset), self.thread_pool.max_workers):
                    batch = dataset[i:i + self.thread_pool.max_workers]
                    self.thread_pool.process_batch(batch, self._generate)
                    with open(temp_dir / 'Gen_Temp.pkl', 'wb') as f:
                        pickle.dump(dataset, f)
                    pbar.update(len(batch))

        if llm_judge is not None:
            self.judge_answers(dataset, llm_judge)

        dataset.cost()

    def judge_answers(self, dataset, llm_judge):
        temp_dir = env.results / 'temp'
        temp_dir.mkdir(parents=True, exist_ok=True)
        with tqdm(total=len(dataset), desc='Evaluating Samples', unit="sample") as pbar:
            for i in range(0, len(dataset), self.thread_pool.max_workers):
                batch = [(sample, llm_judge) for sample in dataset[i:i + self.thread_pool.max_workers]]
                self.thread_pool.process_batch(batch, lambda args: self._evaluate(*args))
                with open(temp_dir / 'Eval_Temp.pkl', 'wb') as f:
                    pickle.dump(dataset, f)
                pbar.update(len(batch))

    def _generate(self, sample: TextVisionSample):
        sample.pred_text, sample.eval_cost, tokens_used, sample.raw_output = self.generate(sample)
        sample.update_tokens_used(tokens_used)
        #print(f"api_model.py: Tokens Used: {tokens_used}")

        return tokens_used

    def _evaluate(self, sample: TextVisionSample, llm_judge: GenericModel):
        if sample.pred_text is None:
            raise ValueError("sample.pred_text is None")
        sample.llm_eval, eval_cost, tokens_used, sample.raw_output = llm_judge.llm_evaluate(sample)
        if sample.eval_cost is not None:
            sample.eval_cost += eval_cost
        else:
            sample.eval_cost = eval_cost

        sample.update_tokens_used(tokens_used)

        return tokens_used

    def generate_questions(self, map, num_questions=20):
        raise NotImplementedError
        #TODO

    @DeprecationWarning
    def _evaluate_dataset(self, dataset: IterableDataset):
        tasks = []

        for sample in dataset:
            task = {
                'question': sample.get_text(),
                'image_path': sample.image,
                'sample': sample
            }
            tasks.append(task)
        
        with tqdm(total=len(tasks), desc='Processing Samples', unit="sample") as pbar:
            for i in range(0, len(tasks), self.thread_pool.max_workers):
                batch = tasks[i:i + self.thread_pool.max_workers]
                results = self.thread_pool.process_batch(batch, self.process_question)
                
                # Update samples with tokenized responses
                for task, result in zip(batch, results):
                    if isinstance(result, dict) and "error" in result:
                        print(f"Error processing sample: {result['error']}")
                    else:
                        tokens = self.tokenize_response(result)
                        task['sample'].outs = tokens
                
                pbar.update(len(batch))

    def process_question(self, task):
        # Unpack question and image_path from the dict:
        question = task['question']
        image_path = task['image_path']
    
        chosen_model = self.chosen_model
        config = self.config

        if chosen_model == "claude":
            answer = self.claude_vqa(question, image_path, config)
        elif chosen_model == 'openai':
            answer = self.openai_vqa(question, image_path, config)
        elif chosen_model == "gemini":
            answer = self.gemini_vqa(question, image_path, config)

        return answer