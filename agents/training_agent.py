from typing import Optional
from os.path import join

from datasets import Dataset
import torch
from torch.nn.utils.rnn import pad_sequence
from transformers import AutoModelForCausalLM, AutoTokenizer, TrainingArguments, Trainer, EarlyStoppingCallback
from peft import LoraConfig, get_peft_model

from agents.base_agent import BaseAgent
from utils.logger import logger


def initialize_qwen2_peft(
    model,
    lora_r: int = 8,
    lora_alpha: int = 16,
    lora_dropout: float = 0.05,
    lora_modules = None,
    task_type='SEQ_CLS',
):
    if lora_modules is None and model.config.__class__.__name__ in [
        # "LlamaConfig",
        # "MistralConfig",
        # "GemmaConfig",
        "Qwen2Config",
        'DefusionConfig',
    ]:
        lora_modules = [
            "q_proj",
            "v_proj",
            "k_proj",
            "o_proj",
            "gate_proj",
            "up_proj",
            "down_proj",
        ]
    elif lora_modules is None:
        raise ValueError("lora_modules must be specified for this model.")

    config = LoraConfig(
        r=lora_r,
        lora_alpha=lora_alpha,
        target_modules=lora_modules,
        lora_dropout=lora_dropout,
        bias="none",
        task_type=task_type,
    )

    model = get_peft_model(model, config)
    model.config.gradient_checkpointing = True
    logger.info(f"Model's Lora trainable parameters:")
    model.print_trainable_parameters()
    return model


class PadCollator:

    def __init__(self, tokenizer, max_length:Optional[int], device=None):
        self.max_length = max_length
        self.tokenizer = tokenizer
        self.pad_token_id = tokenizer.pad_token_id
        self.device = device

    def __call__(self, batch):
        input_ids = [torch.tensor(b['input_ids']) for b in batch]
        attention_mask = [torch.tensor(b['attention_mask']) for b in batch]
        labels = [b['label'] for b in batch]
        # Pad or truncate the sequences to the maximum length
        input_ids = pad_sequence(
            input_ids,
            True, self.pad_token_id)
        attention_mask = pad_sequence(
            attention_mask,
            True, 0)

        # check length
        if self.max_length is not None and input_ids.size(1) > self.max_length:
            input_ids = input_ids[:, :self.max_length]
            attention_mask = attention_mask[:, :self.max_length]

        # check device
        if self.device:
            input_ids = input_ids.to(self.device)
            attention_mask = attention_mask.to(self.device)
        labels = torch.tensor(labels, dtype=torch.long, device=self.device)

        return {
            'input_ids': input_ids,
            'attention_mask': attention_mask,
            'labels': labels
        }


class TrainingAgent(BaseAgent):

    def __init__(
            self,
            name:str,
            model_path:str,
            max_length:Optional[int]=None,
            device=None,
            batch_size:int=16,
            learning_rate:float=1e-5,
            num_epochs:int=3,
            weight_decay:float=0.01,
            ckpt_dir:str='./model_checkpoints',
            resume:bool=False,
            enable_lora:bool=False,
        ):
        self.name = name
        self.model_path = model_path
        self.max_length = max_length
        self.device = device
        self.batch_size = batch_size
        self.learning_rate = learning_rate
        self.num_epochs = num_epochs
        self.weight_decay = weight_decay
        self.ckpt_dir = join(ckpt_dir, self.name)
        self.resume = resume
        self.enable_lora = enable_lora

    def open(self) -> None:
        self.model = AutoModelForCausalLM.from_pretrained(
            self.model_path,
            torch_dtype="auto",
            device=self.device,
        )
        self.tokenizer = AutoTokenizer.from_pretrained(self.model_path)
        self.collator = PadCollator(self.tokenizer, self.max_length, self.device)
        self.training_args = TrainingArguments(
            output_dir=self.ckpt_dir,
            per_device_train_batch_size=self.batch_size, # Adjust batch size based on your GPU memory
            # gradient_accumulation_steps=2,
            per_device_eval_batch_size=self.batch_size,
            eval_strategy="steps",
            eval_steps=500,
            logging_steps=500,
            save_steps=500,
            save_total_limit=2,
            num_train_epochs=2, # Adjust number of epochs as needed
            learning_rate=5e-5,
            warmup_steps=500,
            weight_decay=0.01,
            metric_for_best_model="eval_loss",
            load_best_model_at_end=True,
            ddp_find_unused_parameters=False,
        )
        if self.enable_lora:
            self.model = initialize_qwen2_peft(self.model)



    def __call__(self, dataset:Dataset, eval_dataset:Dataset) -> None:
        trainer = Trainer(
            model=self.model,
            args=self.training_args,
            train_dataset=dataset,
            eval_dataset=eval_dataset,
            data_collator=self.collator,
            callbacks=[
                EarlyStoppingCallback(early_stopping_patience=3, early_stopping_threshold=0.01)
            ]
        )

        # 8. Train!
        trainer.train(resume_from_checkpoint=self.resume)
        trainer.save_model(self.ckpt_dir) # Save trained model