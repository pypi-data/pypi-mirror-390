from enum import Enum
import random

import torch
from transformers import PreTrainedTokenizer
from datasets import load_dataset

from Datasets.core import IterableDataset
from Datasets.core import GenerationSample
from fusekit.Common.EvalType import EvalType as EvalType
from Common.utils import split_alnum_and_lower
from Datasets.base import Metric

class BBHTasks(Enum):
    # multiple choice
    bbh_boolean_expressions = ('lukaemon/bbh', 'boolean_expressions', 'test')
    bbh_causal_judgement = ('lukaemon/bbh', 'causal_judgement', 'test')
    bbh_date_understanding = ('lukaemon/bbh', 'date_understanding', 'test')
    bbh_disambiguation_qa = ('lukaemon/bbh', 'disambiguation_qa', 'test')
    bbh_formal_fallacies = ('lukaemon/bbh', 'formal_fallacies', 'test')
    bbh_geometric_shapes = ('lukaemon/bbh', 'geometric_shapes', 'test')
    bbh_hyperbaton = ('lukaemon/bbh', 'hyperbaton', 'test')
    bbh_logical_deduction_five_objects = ('lukaemon/bbh', 'logical_deduction_five_objects', 'test')
    bbh_logical_deduction_seven_objects = ('lukaemon/bbh', 'logical_deduction_seven_objects', 'test')
    bbh_logical_deduction_three_objects = ('lukaemon/bbh', 'logical_deduction_three_objects', 'test')
    bbh_movie_recommendation = ('lukaemon/bbh', 'movie_recommendation', 'test')
    bbh_navigate = ('lukaemon/bbh', 'navigate', 'test')
    bbh_penguins_in_a_table = ('lukaemon/bbh', 'penguins_in_a_table', 'test')
    bbh_reasoning_about_colored_objects = ('lukaemon/bbh', 'reasoning_about_colored_objects', 'test')
    bbh_ruin_names = ('lukaemon/bbh', 'ruin_names', 'test')
    bbh_salient_translation_error_detection = ('lukaemon/bbh', 'salient_translation_error_detection', 'test')
    bbh_snarks = ('lukaemon/bbh', 'snarks', 'test')
    bbh_sports_understanding = ('lukaemon/bbh', 'sports_understanding', 'test')
    bbh_temporal_sequences = ('lukaemon/bbh', 'temporal_sequences', 'test')
    bbh_tracking_shuffled_objects_five_objects = ('lukaemon/bbh', 'tracking_shuffled_objects_five_objects', 'test')
    bbh_tracking_shuffled_objects_seven_objects = ('lukaemon/bbh', 'tracking_shuffled_objects_seven_objects', 'test')
    bbh_tracking_shuffled_objects_three_objects = ('lukaemon/bbh', 'tracking_shuffled_objects_three_objects', 'test')
    bbh_web_of_lies = ('lukaemon/bbh', 'web_of_lies', 'test')
    # free response
    bbh_dyck_languages = ('lukaemon/bbh', 'dyck_languages', 'test')
    bbh_multistep_arithmetic_two = ('lukaemon/bbh', 'multistep_arithmetic_two', 'test')
    bbh_object_counting = ('lukaemon/bbh', 'object_counting', 'test')
    bbh_word_sorting = ('lukaemon/bbh', 'word_sorting', 'test')

# the actual dataset has some garbage targets that must be overridden
_targets_override = {
    BBHTasks.bbh_movie_recommendation: ['(A)', '(B)', '(C)', '(D)', '(E)'],
    BBHTasks.bbh_ruin_names: ['(A)', '(B)', '(C)', '(D)'],
}
_free_response_tasks = [BBHTasks.bbh_dyck_languages, BBHTasks.bbh_multistep_arithmetic_two, BBHTasks.bbh_object_counting, BBHTasks.bbh_word_sorting]
all_tasks = list(BBHTasks.__members__.items())

class BBHDataset(IterableDataset):
    def __init__(self, tokenizer: PreTrainedTokenizer, task_type: BBHTasks, data_limit: int = -1, max_new_tokens: int = 100, num_shots: int = 0, seed: int = 42):
        super().__init__()
        self.type = EvalType.SIMILARITY
        path, name, split = task_type.value
        self.hf_dataset = (path, name, split)
        self.dataset = list(load_dataset(path=path, name=name, split=split))
        if task_type in _free_response_tasks:  # free response tasks have no targets
            self.all_targets = set()
        elif task_type in _targets_override:  # multiple choice with an overriden targets
            self.all_targets = _targets_override[task_type]
        else:  # multiple choice with the default targets
            self.all_targets = set(sample['target'] for sample in self.dataset)
        self.samples: list[BBHSample] = []
        for sample in self.dataset:  # append " Answer: " to the input
            sample['input'] = sample['input'] + '\nAnswer:'
        seeder = random.Random(seed)
        for i, sample in enumerate(self.dataset):
            if i >= data_limit and data_limit != -1:
                break
            shots = []
            if num_shots > 0:
                dataset_without_i = [sample for j, sample in enumerate(self.dataset) if j != i]
                shots = seeder.sample(dataset_without_i, num_shots)
                shots = [shot['input'] + ' ' + shot['target'] for shot in shots]
            self.samples.append(BBHSample(tokenizer, sample['input'], sample['target'], task_type, max_new_tokens=max_new_tokens, shots=shots, all_targets=self.all_targets))

class BBHSample(GenerationSample):
    def __init__(self, tokenizer: PreTrainedTokenizer, text: str, label: str, task_type: BBHTasks, max_new_tokens: int, shots: list[str] = [], all_targets: set = set()):
        super().__init__(tokenizer, text, label, max_new_tokens=max_new_tokens)
        self.task_type = task_type
        self.shots = shots
        self.all_targets = [split_alnum_and_lower(target) for target in all_targets]
        assert all(len(target) == 1 for target in self.all_targets), "All targets should have length 1"
        self.all_targets = set(target[0] for target in self.all_targets)

    def get_text(self) -> str:
        if len(self.shots) == 0:
            return self.prompt
        return '\n'.join(self.shots) + '\n' + self.prompt

    def get_labels(self) -> torch.Tensor:
        if self.labels is None:
            text_with_label = self.get_text() + ' ' + self.answer
            labels = self.tokenizer.encode(text_with_label)
            self.labels = torch.tensor(labels, dtype=torch.long).unsqueeze(0)
        return self.labels

    def get_accuracy(self):
        if self.task_type in _free_response_tasks:  # free response -> exact match
            assert self.pred_text is not None, "Prediction text is required for accuracy evaluation"
            m = Metric(self.pred_text, self.answer)
            return {"Exact Match": m.exact_match(),
                    "F1 Score": m.f1(),
                    "ROUGE-L": m.rouge_L(),
                    "BLEU": m.bleu()}
        # multiple choice -> accuracy
        gold = split_alnum_and_lower(self.answer)
        assert len(gold) == 1, "Gold label should have length 1"
        gold = gold[0]

        predicted = split_alnum_and_lower(self.pred_text)
        for i in range(len(predicted)-1, -1, -1):
            if predicted[i] in self.all_targets:
                return {"Accuracy": 1.0 if predicted[i] == gold else 0.0}
        return {"Accuracy": 0.0}

BBHBooleanExpressions = lambda tokenizer, data_limit=-1, max_new_tokens=100, num_shots=0: BBHDataset(tokenizer, BBHTasks.bbh_boolean_expressions, data_limit=data_limit, max_new_tokens=max_new_tokens, num_shots=num_shots)
BBHCausalJudgement = lambda tokenizer, data_limit=-1, max_new_tokens=100, num_shots=0: BBHDataset(tokenizer, BBHTasks.bbh_causal_judgement, data_limit=data_limit, max_new_tokens=max_new_tokens, num_shots=num_shots)
BBHDateUnderstanding = lambda tokenizer, data_limit=-1, max_new_tokens=100, num_shots=0: BBHDataset(tokenizer, BBHTasks.bbh_date_understanding, data_limit=data_limit, max_new_tokens=max_new_tokens, num_shots=num_shots)
BBHDisambiguationQA = lambda tokenizer, data_limit=-1, max_new_tokens=100, num_shots=0: BBHDataset(tokenizer, BBHTasks.bbh_disambiguation_qa, data_limit=data_limit, max_new_tokens=max_new_tokens, num_shots=num_shots)
BBHFormalFallacies = lambda tokenizer, data_limit=-1, max_new_tokens=100, num_shots=0: BBHDataset(tokenizer, BBHTasks.bbh_formal_fallacies, data_limit=data_limit, max_new_tokens=max_new_tokens, num_shots=num_shots)
BBHGeometricShapes = lambda tokenizer, data_limit=-1, max_new_tokens=100, num_shots=0: BBHDataset(tokenizer, BBHTasks.bbh_geometric_shapes, data_limit=data_limit, max_new_tokens=max_new_tokens, num_shots=num_shots)
BBHHyperbaton = lambda tokenizer, data_limit=-1, max_new_tokens=100, num_shots=0: BBHDataset(tokenizer, BBHTasks.bbh_hyperbaton, data_limit=data_limit, max_new_tokens=max_new_tokens, num_shots=num_shots)
BBHLogicalDeductionFiveObjects = lambda tokenizer, data_limit=-1, max_new_tokens=100, num_shots=0: BBHDataset(tokenizer, BBHTasks.bbh_logical_deduction_five_objects, data_limit=data_limit, max_new_tokens=max_new_tokens, num_shots=num_shots)
BBHLogicalDeductionSevenObjects = lambda tokenizer, data_limit=-1, max_new_tokens=100, num_shots=0: BBHDataset(tokenizer, BBHTasks.bbh_logical_deduction_seven_objects, data_limit=data_limit, max_new_tokens=max_new_tokens, num_shots=num_shots)
BBHLogicalDeductionThreeObjects = lambda tokenizer, data_limit=-1, max_new_tokens=100, num_shots=0: BBHDataset(tokenizer, BBHTasks.bbh_logical_deduction_three_objects, data_limit=data_limit, max_new_tokens=max_new_tokens, num_shots=num_shots)
BBHMovieRecommendation = lambda tokenizer, data_limit=-1, max_new_tokens=100, num_shots=0: BBHDataset(tokenizer, BBHTasks.bbh_movie_recommendation, data_limit=data_limit, max_new_tokens=max_new_tokens, num_shots=num_shots)
BBHNavigate = lambda tokenizer, data_limit=-1, max_new_tokens=100, num_shots=0: BBHDataset(tokenizer, BBHTasks.bbh_navigate, data_limit=data_limit, max_new_tokens=max_new_tokens, num_shots=num_shots)
BBHPenguinsInATable = lambda tokenizer, data_limit=-1, max_new_tokens=100, num_shots=0: BBHDataset(tokenizer, BBHTasks.bbh_penguins_in_a_table, data_limit=data_limit, max_new_tokens=max_new_tokens, num_shots=num_shots)
BBHReasoningAboutColoredObjects = lambda tokenizer, data_limit=-1, max_new_tokens=100, num_shots=0: BBHDataset(tokenizer, BBHTasks.bbh_reasoning_about_colored_objects, data_limit=data_limit, max_new_tokens=max_new_tokens, num_shots=num_shots)
BBHRuinNames = lambda tokenizer, data_limit=-1, max_new_tokens=100, num_shots=0: BBHDataset(tokenizer, BBHTasks.bbh_ruin_names, data_limit=data_limit, max_new_tokens=max_new_tokens, num_shots=num_shots)
BBHSalientTranslationErrorDetection = lambda tokenizer, data_limit=-1, max_new_tokens=100, num_shots=0: BBHDataset(tokenizer, BBHTasks.bbh_salient_translation_error_detection, data_limit=data_limit, max_new_tokens=max_new_tokens, num_shots=num_shots)
BBHSnarks = lambda tokenizer, data_limit=-1, max_new_tokens=100, num_shots=0: BBHDataset(tokenizer, BBHTasks.bbh_snarks, data_limit=data_limit, max_new_tokens=max_new_tokens, num_shots=num_shots)
BBHSportsUnderstanding = lambda tokenizer, data_limit=-1, max_new_tokens=100, num_shots=0: BBHDataset(tokenizer, BBHTasks.bbh_sports_understanding, data_limit=data_limit, max_new_tokens=max_new_tokens, num_shots=num_shots)
BBHTemporalSequences = lambda tokenizer, data_limit=-1, max_new_tokens=100, num_shots=0: BBHDataset(tokenizer, BBHTasks.bbh_temporal_sequences, data_limit=data_limit, max_new_tokens=max_new_tokens, num_shots=num_shots)
BBHTrackingShuffledObjectsFiveObjects = lambda tokenizer, data_limit=-1, max_new_tokens=100, num_shots=0: BBHDataset(tokenizer, BBHTasks.bbh_tracking_shuffled_objects_five_objects, data_limit=data_limit, max_new_tokens=max_new_tokens, num_shots=num_shots)
BBHTrackingShuffledObjectsSevenObjects = lambda tokenizer, data_limit=-1, max_new_tokens=100, num_shots=0: BBHDataset(tokenizer, BBHTasks.bbh_tracking_shuffled_objects_seven_objects, data_limit=data_limit, max_new_tokens=max_new_tokens, num_shots=num_shots)
BBHTrackingShuffledObjectsThreeObjects = lambda tokenizer, data_limit=-1, max_new_tokens=100, num_shots=0: BBHDataset(tokenizer, BBHTasks.bbh_tracking_shuffled_objects_three_objects, data_limit=data_limit, max_new_tokens=max_new_tokens, num_shots=num_shots)
BBHWebOfLies = lambda tokenizer, data_limit=-1, max_new_tokens=100, num_shots=0: BBHDataset(tokenizer, BBHTasks.bbh_web_of_lies, data_limit=data_limit, max_new_tokens=max_new_tokens, num_shots=num_shots)

BBHDyckLanguages = lambda tokenizer, data_limit=-1, max_new_tokens=100, num_shots=0: BBHDataset(tokenizer, BBHTasks.bbh_dyck_languages, data_limit=data_limit, max_new_tokens=max_new_tokens, num_shots=num_shots)
BBHMultistepArithmeticTwo = lambda tokenizer, data_limit=-1, max_new_tokens=100, num_shots=0: BBHDataset(tokenizer, BBHTasks.bbh_multistep_arithmetic_two, data_limit=data_limit, max_new_tokens=max_new_tokens, num_shots=num_shots)
BBHObjectCounting = lambda tokenizer, data_limit=-1, max_new_tokens=100, num_shots=0: BBHDataset(tokenizer, BBHTasks.bbh_object_counting, data_limit=data_limit, max_new_tokens=max_new_tokens, num_shots=num_shots)
BBHWordSorting = lambda tokenizer, data_limit=-1, max_new_tokens=100, num_shots=0: BBHDataset(tokenizer, BBHTasks.bbh_word_sorting, data_limit=data_limit, max_new_tokens=max_new_tokens, num_shots=num_shots)

all_bbh_mc_datasets = [BBHBooleanExpressions, BBHCausalJudgement, BBHDateUnderstanding, BBHDisambiguationQA, BBHFormalFallacies, BBHGeometricShapes, BBHHyperbaton, BBHLogicalDeductionFiveObjects, BBHLogicalDeductionSevenObjects, BBHLogicalDeductionThreeObjects, BBHMovieRecommendation, BBHNavigate, BBHPenguinsInATable, BBHReasoningAboutColoredObjects, BBHRuinNames, BBHSalientTranslationErrorDetection, BBHSnarks, BBHSportsUnderstanding, BBHTemporalSequences, BBHTrackingShuffledObjectsFiveObjects, BBHTrackingShuffledObjectsSevenObjects, BBHTrackingShuffledObjectsThreeObjects, BBHWebOfLies]
all_bbh_free_response_datasets = [BBHDyckLanguages, BBHMultistepArithmeticTwo, BBHObjectCounting, BBHWordSorting]
