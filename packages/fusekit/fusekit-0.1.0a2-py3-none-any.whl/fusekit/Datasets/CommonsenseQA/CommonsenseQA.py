import fusekit.Common.env as env
import fusekit.Common.utils as utils

from fusekit.Datasets.base import SpecialTokens
from fusekit.Datasets.core import IterableDataset
from fusekit.Datasets.extensions import MultiChoiceQA
from fusekit.Common.EvalType import EvalType as EvalType

class CommonsenseQA(IterableDataset):
    def __init__(self, tokenizer, split='train', num_shots=0, data_limit=-1):
        super().__init__()
        self.name = 'CommonsenseQA'
        self.type = EvalType.LOGLIKELIHOOD

        if split == 'train':
            data = utils.jsonl.read(env.DatasetPath.commonsenseqa /
                                    'train_rand_split.jsonl')
        elif split == 'val':
            data = utils.jsonl.read(env.DatasetPath.commonsenseqa /
                                    'dev_rand_split.jsonl')
        else:
            raise ValueError('Unknown data split for CommonsenseQA: ' + split)
        
        if data_limit < 0 or data_limit + num_shots > len(data):
            data_limit = len(data)
        else:
            data_limit = data_limit + num_shots

        # Prepend prompts with n-shot examples
        n_shot_text = ''
        for line in data[:num_shots]:
            example = MultiChoiceQA(tokenizer, *self.parse_line(line))
            n_shot_text = (
                n_shot_text + example.get_text(show_label=True) +
                '\n'
            )

        self.samples: list[MultiChoiceQA] = []
        for line in data[num_shots:data_limit]:
            uid, question, options, label, label_idx = self.parse_line(line)
            question = n_shot_text + question
            
            self.samples.append(MultiChoiceQA(tokenizer, uid=uid, 
                                          question=question,
                                          options=options, 
                                          label=label,
                                          label_idx=label_idx))

    def parse_line(self, line):
        options = [option['text'] for option in line['question']['choices']]
        label = next(option['text'] 
                     for option in line['question']['choices'] 
                     if option['label'] == line['answerKey'])
        uid = line['id']
        question = "Question: " + line['question']['stem']

        label_idx = options.index(label)

        options = [label + option 
                   for label, option in zip(MultiChoiceQA.LABELS, options)]
        label = options[label_idx]

        return (uid, question, options, label, label_idx)