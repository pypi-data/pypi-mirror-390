import torch
import random
from transformers import PreTrainedTokenizer
from copy import copy
from pathlib import Path
from typing import overload
from typing import Union, List

from fusekit.Datasets.base import Metric, APICost

class GenericSample:
    def __init__(self, tokenizer: PreTrainedTokenizer, max_new_tokens=0, uid=None):
        self.uid = uid
        self.inputs = None
        self.labels = None
        self.image = False
        self.tokenizer = tokenizer
        self.processor = None
        self.max_new_tokens = max_new_tokens

        self.pred = None
        self.done = False
        self.type = None
        self.sample_width = 1

    def get_text(self) -> str:
        return NotImplementedError
    
    def get_inputs(self) -> torch.Tensor:
        return NotImplementedError
    
    def get_labels(self) -> torch.Tensor:
        return NotImplementedError

    def get_pred(self) -> torch.Tensor:
        if self.pred is None:
            self.pred = self.get_inputs()
        return self.pred
    
    def encode(self, text):
        return self.tokenizer.encode(text, add_special_tokens=False)
    
    def get_accuracy(self) -> dict:
        m = Metric(self.outs, self.label)
        return {"Exact Match": m.exact_match()}
    

class GenerationSample(GenericSample):
    def __init__(self, tokenizer: PreTrainedTokenizer,
                 prompt, answer, max_new_tokens=0, uid=None, preload=True):
        super().__init__(tokenizer, max_new_tokens=max_new_tokens, uid=uid)
        self.prompt = "Prompt: " + prompt + "\nAnswer: "
        self.answer = answer
        self.outs = None # This should be a tokenized list
        self.pred_text = None # Untokenized outputs from model
        self.llm_eval = None # Untokenized response from LLM-As-A-Judge
        self.eval_cost = None
        self.tokens_used = 0
        self.raw_output = None

    def __repr__(self):
        return f"Text: {self.get_text()}\n" + \
               f"Label: {self.answer}\n" + \
               f"Prediction: {self.pred_text}\n" + \
               f"LLM Eval: {self.llm_eval}\n" + \
               repr(self.eval_cost)

    def get_text(self) -> str:
        return self.prompt
    
    def get_inputs(self) -> torch.Tensor:
        if self.inputs is None:
            inputs = self.tokenizer.encode(self.get_text())
            self.inputs = torch.tensor(inputs, dtype=torch.long).unsqueeze(0)
        return self.inputs
    
    def update_tokens_used(self, n: int):
        self.tokens_used += n
    
    def get_accuracy(self) -> dict:
        if self.llm_eval is not None:
            return {"LLM-As-A-Judge": 1 if self.llm_eval == "Correct" else 0}
        elif self.labels is not None:
            m = Metric(self.outs, self.labels)
            return {"Exact Match": m.exact_match(),
                    "F1 Score": m.f1(),
                    "ROUGE-L": m.rouge_L(),
                    "BLEU": m.bleu()}
        else:
            return {}

class IterableDataset():
    def __init__(self, *args, **kwargs):
        self._init_args = args
        self._init_kwargs = kwargs
        self.samples = [GenericSample]
        self._index = 0
        self.type = None
        self.name = 'Placeholder Dataset Name'

    def __iter__(self):
        self._index = 0
        return self
    
    def __next__(self):
        if self._index < len(self.samples):
            result = self.samples[self._index]
            self._index += 1
            return result
        else:
            raise StopIteration
        
    def __getitem__(self, index) -> GenericSample:
        return self.samples[index]
    
    def __len__(self):
        count = 0
        for sample in self.samples:
            count += sample.sample_width
        return count

    def merge(self, datasets: Union["IterableDataset", list["IterableDataset"]], name: str, seed=0):
        if not isinstance(datasets, list):
            datasets = [datasets]
        for dataset in datasets:
            # Extend with actual sample objects
            self.samples.extend(dataset.samples)
        random.seed(seed)
        random.shuffle(self.samples)
        self.name = name

        return self
    
    def save_jsondata(self, data_list, savepath):
        if savepath is not None:
            savepath.parent.mkdir(parents=True, exist_ok=True)
            with open(savepath, 'w', encoding='utf-8') as f:
                for entry in data_list:
                    f.write(entry + '\n')

        return data_list
    
    def cost(self):
        total_cost = APICost(0.0, 0.0)
        for sample in self:
            if isinstance(sample, GenerationSample):
                total_cost += sample.eval_cost

        print(total_cost)

    def accuracy(self):
        raw_metrics = {}
        dataset_metrics = {}
        for sample in self:
            metric_dict = sample.get_accuracy()
            for key, value in metric_dict.items():
                if key not in raw_metrics:
                    raw_metrics[key] = [value]
                else:
                    raw_metrics[key].append(value)

        for key, value in raw_metrics.items():
            values = 0
            for metric in value:
                values += metric
            avg = values/len(raw_metrics[key])
            print(f'{key}: {avg}')
            dataset_metrics[key] = avg

        return dataset_metrics, raw_metrics

    @overload
    def dump_inference(self) -> list[str]: ...
    @overload
    def dump_inference(self, savepath: Path) -> list[str]: ...

    def dump_inference(self, savepath: Path | None = None) -> list[str]:
        raise NotImplementedError
    
    def load_inference(self, filename):
        raise NotImplementedError
    
    def get_uid(self, uid):
        for sample in self.samples:
            if sample.uid == uid:
                return sample
        raise ValueError(f"No sample found with uid: {uid}")
    
    def random_subset(self, subset_length, seed=None):
        if subset_length is None:
            return self

        """Generate a random subset of the dataset with the specified 'total width'."""
        if seed is not None:
            random.seed(seed)

        if subset_length > len(self):
            raise ValueError("Subset length exceeds the total width of the dataset.")

        selected_samples = []
        total_width = 0

        # Shuffle indices to randomly access samples
        indices = list(range(len(self.samples)))
        random.shuffle(indices)

        # Attempt to collect samples until we reach the desired total width
        for idx in indices:
            sample = self.samples[idx]
            if total_width + sample.sample_width <= subset_length:
                selected_samples.append(sample)
                total_width += sample.sample_width
                if total_width == subset_length:
                    break

        # Check if we have successfully collected enough width
        if total_width < subset_length:
            raise ValueError("Couldn't reach the exact subset length due to sample widths configuration.")

        # Return a new IterableDataset containing only the selected samples
        new_dataset = copy(self)
        new_dataset.samples = selected_samples

        print(f"Created random subset of size {subset_length}.")
        return new_dataset
    
class Multi(IterableDataset):
    def __init__(self, tokenizer, datasets: Union["IterableDataset", list["IterableDataset"]], name: str, seed=0):
        if not isinstance(datasets, list):
            datasets = [datasets]

        return datasets[0](tokenizer).merge([dataset(tokenizer, data_limit=1000) for dataset in datasets[1:]], name=name, seed=seed)
    
