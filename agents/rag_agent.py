import gc
import shutil
import os
import glob

import torch
from transformers import AutoTokenizer, AutoModel
from typing import List, Dict 

from agents.base_agent import BaseAgent


class RAGAgent(BaseAgent):

    def __init__(self, embedding_model_name: str, db_path: str, top_k:int=3):
        super().__init__()
        self.embedding_model_name = embedding_model_name
        self.db_path = db_path
        self.file_paths = []
        self.vectors = None
        if db_path:
            self.vectors = torch.load(os.path.join(db_path, "vectors.pt"))
            with open(os.path.join(db_path, "file_paths.txt"), "r") as f:
                for line in f:
                    self.file_paths.append(line.strip())
        self.top_k = top_k
        self.embedding_model = None
        self.embedding_tokenizer = None

    def open(self) -> None:
        self.embedding_tokenizer = AutoTokenizer.from_pretrained(self.embedding_model_name)
        self.embedding_model = AutoModel.from_pretrained(
            self.embedding_model_name, trust_remote_code=True,
            device_map="auto"
        )
        if self.vectors:
            self.vectors = self.vectors.to(self.embedding_model.device)

    def close(self) -> None:
        self.embedding_model = self.embedding_model.cpu()
        self.embedding_model = None
        self.embedding_tokenizer = None
        if self.vectors:
            self.vectors = self.vectors.cpu()
            self.vectors = None
        self.db_path = None
        gc.collect()
        torch.cuda.empty_cache()

    def __call__(self, query: str) -> List[str]:
        with torch.no_grad():
            inputs = self.embedding_tokenizer.encode(query, return_tensors="pt").to(self.embedding_model.device)
            embedding = self.embedding_model(inputs)
        
        ranks = torch.nn.functional.cosine_similarity(embedding, self.vectors, dim=1)
        top_k_indices = torch.topk(ranks, self.top_k).indices
        top_k_indices = top_k_indices.cpu().numpy().tolist()
        results = []
        for i in top_k_indices:
            file_path = self.file_paths[i]
            with open(file_path, "r") as f:
                content = f.read()
                results.append(content)
        return results
    
    @staticmethod
    def indexing(
        embedding_model,
        embedding_tokenizer,
        codebase: str,
        extensions: List[str],
        db_path: str,
    ) -> None:
        outputs = torch.empty((0, embedding_model.config.hidden_size))
        files = glob.glob(os.path.join(codebase, "**"), recursive=True)
        file_paths = []
        # for file in codebase recursively
        for file_path in files:
            if os.path.isdir(file_path):
                continue
            if any(file_path.endswith(ext) for ext in extensions):
                file_paths.append(file_path)
                with open(file_path, "r") as f:
                    content = f.read()
                    inputs = embedding_tokenizer.encode(content, return_tensors="pt").to(embedding_model.device)
                    embedding = embedding_model(inputs).cpu()
                    outputs = torch.cat((outputs, embedding), dim=0)
        torch.save(outputs, os.path.join(db_path, "vectors.pt"))
        with open(os.path.join(db_path, "file_paths.txt"), "w") as f:
            for file_path in file_paths:
                f.write(file_path + "\n")
        

