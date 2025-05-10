import gc

from transformers import Qwen2Tokenizer, Qwen2ForCausalLM
import torch

from agents.base_agent import BaseAgent


class QwenAgent(BaseAgent):

    def __init__(self, model_name:str):
        super().__init__()
        self.model_name = model_name

    def __call__(self, user_prompt, system_prompt="You are Qwen, created by Alibaba Cloud. You are a helpful assistant.") -> str:
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]
        text = self.tokenizer.apply_chat_template(
            messages,
            tokenize=False,
            add_generation_prompt=True
        )
        model_inputs = self.tokenizer([text], return_tensors="pt").to(self.model.device)
        generated_ids = self.model.generate(**model_inputs, max_new_tokens=1024)
        generated_ids = [
            output_ids[len(input_ids):] for input_ids, output_ids in zip(model_inputs.input_ids, generated_ids)
        ]
        return self.tokenizer.batch_decode(generated_ids, skip_special_tokens=True)[0]   

    def open(self) -> None:
        self.model = Qwen2ForCausalLM.from_pretrained(
            self.model_name,
            torch_dtype="auto",
            device_map="auto",
        )
        self.tokenizer = Qwen2Tokenizer.from_pretrained(self.model_name)

    def close(self) -> None:
        del self.model
        del self.tokenizer
        gc.collect()
        torch.cuda.empty_cache()

