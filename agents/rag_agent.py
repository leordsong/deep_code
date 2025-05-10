import torch

from agents.base_agent import BaseAgent


class RAGAgent(BaseAgent):

    def __init__(self, embedding_model_name: str, db_path: str):
        super().__init__()
        self.embedding_model_name = embedding_model_name
        self.db_path = db_path
        self.vectors = []

    def open(self) -> None:
        pass

    def close(self) -> None:
        pass

    def __call__(self, query: str) -> str:
        vector = self.embedding_agent(query)
