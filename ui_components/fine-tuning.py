import gradio as gr

from utils.i18n.i18n import I18nAuto, scan_language_list
from agents.rag_agent import RAGAgent
from agents.openai_agents import ChatOpenAIAgent
from agents.qwen_agents import QwenCodebaseQAAgent


def fine_tuning(i18n, qwen_agent, training_agent):

    pass