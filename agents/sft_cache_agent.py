from os.path import exists, join
import json

from agents.base_agent import BaseAgent


class SFTCacheAgent(BaseAgent):
    def __init__(self, cache_path):
        super().__init__()
        
        self.cache = {
            'qa': [],
            'sys': [],
        }
        self.cache_path = cache_path # join(cache_path, "ft_data.json")
        if exists(self.cache_path):
            self.cache = json.load(open(self.cache_path, "r"))

    def __call__(self):
        pass

    def add_data(self, text, qa=True):
        if qa:
            self.cache['qa'].append(text)
        else:
            self.cache['sys'].append(text)
        with open(self.cache_path, "w") as f:
            json.dump(self.cache, f)


    def get_data(self, qa=True):
        if qa:
            return self.cache['qa']
        else:
            return self.cache['sys']

    def load_all(self, json_list_file, qa=True):
        with open(json_list_file, "r") as f:
            lines = json.load(f)
        self.cache['qa' if qa else 'sys'].extend(lines)
        with open(self.cache_path, "w") as f:
            json.dump(self.cache, f)

    def open(self):
        pass

    def close(self):
        pass

    @staticmethod
    def from_qwen_to_text(tokenizer, new_answer, user_prompt, system_prompt) -> str:
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
            {"role": "assistant", "content": new_answer}
        ]
        text = tokenizer.apply_chat_template(
            messages,
            tokenize=False,
            add_generation_prompt=False
        )
        return text