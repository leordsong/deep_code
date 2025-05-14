import gc
import shutil
import os
import glob
from os.path import exists, join
from typing import Tuple

import torch
from transformers import AutoTokenizer, AutoModel
from typing import List, Dict 

from agents.base_agent import BaseAgent
from utils.logger import logger


def print_tree(path, extensions, level=0):

    # files = glob.glob(os.path.join(codebase, "**"),recursive=True)
    # file_paths = []
    # # for file in codebase recursively
    # for file_path in files:
    #     if os.path.isdir(file_path):
    #         continue
    #     if any(file_path.endswith(ext) for ext in extensions):
    #         logger.info(f"Indexing {file_path}...")
    #         file_paths.append(file_path)
    #         with open(file_path, "r", encoding='utf-8') as f:
    #             content = f.read()
    #             inputs = embedding_tokenizer.encode(content, return_tensors="pt").to(embedding_model.device)
    #             embedding = embedding_model(inputs).cpu()
    #             if outputs is None:
    #                 outputs = embedding
    #             else:
    #                 outputs = torch.cat((outputs, embedding), dim=0)

    basename = os.path.basename(path)
    if basename.startswith('.') or basename == '__pycache__':
        return '', []
    
    if os.path.isdir(path):
        dirname = "  " * level + basename + "/\n"
        result = ''
        files = []
        for item in os.listdir(path):
            subresult, subfiles = print_tree(os.path.join(path, item), extensions, level + 1)
            result += subresult
            files.extend(subfiles)
        if result:
            return dirname + result, files
        return '', []
    else:
        if any(basename.endswith(ext) for ext in extensions):
            return "  " * level + basename + "\n", [path]
        else:
            return '', []


class RAGAgent(BaseAgent):

    def __init__(self, embedding_model_name: str, cache, top_k:int=3, threshold:float=0.4):
        super().__init__()
        self.embedding_model_name = embedding_model_name
        self.file_paths = []
        self.vectors = cache[0] if cache else None
        if cache:
            self.file_paths = cache[1]['files']
        self.top_k = top_k
        self.embedding_model = None
        self.embedding_tokenizer = None
        self.threshold = threshold

    def open(self) -> None:
        self.embedding_tokenizer = AutoTokenizer.from_pretrained(self.embedding_model_name)
        self.embedding_model = AutoModel.from_pretrained(
            self.embedding_model_name, trust_remote_code=True,
            device_map="auto"
        )
        if self.vectors is not None:
            self.vectors = self.vectors.to(self.embedding_model.device)

    def close(self) -> None:
        self.embedding_model = self.embedding_model.cpu()
        self.embedding_model = None
        self.embedding_tokenizer = None
        if self.vectors is not None:
            self.vectors = self.vectors.cpu()
            self.vectors = None
        self.db_path = None
        gc.collect()
        torch.cuda.empty_cache()

    def __call__(self, query: str) -> List[str]:
        with torch.no_grad():
            inputs = self.embedding_tokenizer.encode(query, return_tensors="pt")
            inputs = inputs[:, :8192].to(self.embedding_model.device)
            embedding = self.embedding_model(inputs)
        
            ranks = torch.nn.functional.cosine_similarity(embedding, self.vectors, dim=1)
            topk = torch.topk(ranks, self.top_k)
            values = topk.values.cpu().numpy().tolist()
            top_k_indices = topk.indices.cpu().numpy().tolist()
            logger.info(f"Top {top_k_indices} values: {values}")
        results = []
        for i, indice in enumerate(top_k_indices):
            if values[i] < self.threshold:
                continue
            file_path = self.file_paths[indice]
            with open(file_path, "r", encoding='utf-8') as f:
                content = f.read()
                results.append(content)
        return results
    
    @staticmethod
    def indexing(
        embedding_model,
        embedding_tokenizer,
        codebase: str,
        extensions: List[str]
    ) -> Tuple[torch.Tensor, List[str], str]:
        outputs = None
        tree, files = print_tree(codebase, extensions)
        with torch.no_grad():
            for file_path in files:
                logger.info(f"Indexing {file_path}...")
                with open(file_path, "r", encoding='utf-8') as f:
                    content = f.read()
                    inputs = embedding_tokenizer.encode(content, return_tensors="pt")
                    inputs = inputs[:, :8192].to(embedding_model.device)  # Truncate to 4096 tokens
                    embedding = embedding_model(inputs).cpu()
                    if outputs is None:
                        outputs = embedding
                    else:
                        outputs = torch.cat((outputs, embedding), dim=0)

        return outputs, files, tree


if __name__ == "__main__":

    import json

    embedding_model_name = "Salesforce/codet5p-110m-embedding"
    db_path = r".\cache\test2"
    vectors = torch.load(os.path.join(db_path, "vectors.pt")) if exists(os.path.join(db_path, "vectors.pt")) else None
    configs = json.load(open(os.path.join(db_path, "configs.json"))) if exists(os.path.join(db_path, "configs.json")) else None

    with RAGAgent(embedding_model_name, (vectors, configs)) as embedding_agent:
        if vectors is None:
            vectors, file_paths, tree = RAGAgent.indexing(
                embedding_model=embedding_agent.embedding_model,
                embedding_tokenizer=embedding_agent.embedding_tokenizer,
                codebase=r".",
                extensions=[".py"]
            )
            embedding_agent.vectors = vectors
            embedding_agent.file_paths = file_paths

        query = "dify results"
        results = embedding_agent(query)
        logger.info(f"Query: {query}")
        for i, result in enumerate(results):
            logger.info(f"Result {i}: {result}")
        

