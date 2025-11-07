import torch, datetime
from pathlib import Path

from peft import get_peft_model, LoraConfig
from tqdm import tqdm

from torch import Tensor
import torch.nn as nn
from fusekit.Datasets import IterableDataset
from torch.optim.optimizer import Optimizer
from fusekit.Modeling.base import CausalModelBase
from fusekit.Common.Batching import BatchSamples, DynamicBatchLoader
from fusekit.Datasets import GenerationSample
from peft.tuners.tuners_utils import BaseTuner

import fusekit.Common.env as env

class TrainingMixin(CausalModelBase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.loss_fct = nn.CrossEntropyLoss(ignore_index=-100)

    def init_lora(self, rank=8, alpha=32, dropout=0.1):
        peft_config = LoraConfig(
            # inference_mode=False, r=8, lora_alpha=32, lora_dropout=0.1
            inference_mode=False, r=int(rank), lora_alpha=int(alpha), lora_dropout=float(dropout),
            target_modules=['q_proj', 'v_proj'],
        )
        self.sanitize()
        self.model = get_peft_model(self.model, peft_config) #, mixed=True)
        self.update()
        return self

    def finetune(self, lr, weight_decay, epochs, 
                    train_dataloader: DynamicBatchLoader, 
                    val_datasets: IterableDataset, 
                    save_path=None, 
                    overwrite=False):
        params_to_train = [(n,p) for n,p in self.model.named_parameters() if p.requires_grad]
        print(f'Number of Trainable Parameters: {sum([p.numel() for n,p in params_to_train]):,}')

        optim = torch.optim.AdamW([p for n,p in params_to_train], 
                                  lr=float(lr), 
                                  weight_decay=float(weight_decay), 
                                  betas=(0.9, 0.95), 
                                  eps=1e-5)
        
        train_loss = []
        for epoch_count in range(1, epochs+1):
            print('Epoch', epoch_count)
            cur_train_loss = self.step(train_dataloader, optim, scheduler=None)
            #train_loss.append([round(i, 5) for i in cur_train_loss])

            val_results = None
            if val_datasets is not None:
                val_results = self.validate(val_datasets)
                # remove 'all_samples', will error when saving, too much info to save

            if save_path is not None:  # save to a different location
                save_path = Path(save_path)
                if save_path.exists() and not overwrite:
                    if input("Existing file found! Overwrite? [y/N] ").strip().lower() != "y":
                        new_folder = input("Enter folder name: ")
                        save_path = save_path.parent / new_folder
                print(f'Saving to location: {save_path}')

            self.model.save_pretrained(save_path)
            # self.save_model({  # type: ignore ; save was checked to exist and be callable above
            #                 'info': {
            #                     'epoch': epoch_count,
            #                     'save_date': datetime.datetime.now().strftime("%Y-%m-%d_%H:%M:%S"),
            #                     'metada': {
            #                         'val': val_results,
            #                         },
            #                     },
            #                 'config': {
            #                     'architectures': self.model.config.architectures,
            #                     'r': self.model.peft_config['default'].r,
            #                     'lora_alpha': self.model.peft_config['default'].lora_alpha,
            #                     'lora_dropout': self.model.peft_config['default'].lora_dropout
            #                 },
            #                 'hidden_info': {  # to not clutter the txt file that shows all info
            #                     'train_loss': train_loss,
            #                     }
            #                 }, save_path=f'{save_path}.pt')
            
    def step(self, dataloader: DynamicBatchLoader, optim:Optimizer=None, scheduler=None):
        self.train(True)

        pbar = tqdm(total=len(dataloader), dynamic_ncols=True, desc="Training", unit="sample")
        for batch in dataloader:
            device = 'cpu'
            if self.device_list:
                device = self.device_list[0]

            training_inputs = batch.get_labels(training=True)
            labels = batch.get_labels()
            training_inputs.to(device)
            labels.to(device)

            output = self.model(
                input_ids=training_inputs.input_ids(),
                attention_mask=training_inputs.mask(),
                use_cache=False,  # avoids cache growth during train
            )

            output

            logits = output.logits[:,-labels['input_ids'].shape[-1]-1:,:].to(device)
            loss = self.get_loss(logits, labels['input_ids'])

            if optim is not None:
                optim.zero_grad()
                loss.backward()
                self.clip_norm()
                optim.step()
                if scheduler is not None:
                    scheduler.step()

            pbar.update(len(batch))
            pbar.set_description(f'Epoch: {1} loss {loss.item():.4f}')
            pbar.refresh()

            batch.to('cpu')
            labels.to('cpu')
        self.train(False)

    def validate(self, datasets: list[IterableDataset] | IterableDataset):
        if not isinstance(datasets, list):
            datasets = [datasets]
        
        return self.evaluate(datasets)
        # metrics = {}
        # for dataset in datasets:
        #     metrics[dataset.name], _ = dataset.accuracy()

        #     print(f'{dataset.name}:')
        #     for metric in metrics[dataset.name]:
        #         print(f'\t{metric}')

        # return metrics

    def get_loss(self, lm_logits, labels) -> Tensor:
        # shift_logits = lm_logits[..., :-1, :].contiguous()
        # shift_labels = labels[..., :].contiguous()
        # # Flatten the tokens
        # loss = self.loss_fct(shift_logits.view(-1, shift_logits.size(-1)), 
        #                 shift_labels.view(-1))

        # if torch.isnan(loss).any():
        #     print("Output")
        #     print(shift_logits.view(-1, shift_logits.size(-1)))
        #     print("Labels")
        #     print(shift_labels.view(-1))
        #     raise ValueError("Loss value is NaN")

        # Computes CE on next-token prediction: predict labels[:, 1:] from logits[:, :-1, :].
        tgt = labels[:, :]               # [B, T]
        logit = lm_logits[:, :-1, :]      # [B, T-1, V]
        logit = logit.transpose(1, 2)     # [B, V, T-1]
        
        loss = self.loss_fct(logit, tgt)

        return loss
    
    def clip_norm(self):
        _clip_ret = torch.nn.utils.clip_grad_norm_(self.model.parameters(), max_norm=1, norm_type='2')