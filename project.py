import sys
import os
import argparse
import json

import gradio as gr

from utils.i18n.i18n import I18nAuto, scan_language_list
from ui_components.qa import qa
from ui_components.design import system_design
from agents.rag_agent import RAGAgent
from agents.qwen_agents import QwenCodebaseQAAgent, QwenCodebaseSystemDesignAgent, QwenAgent
from agents.openai_agents import OpenAICodebaseQAAgent, OpenAICodebaseSystemDesignAgent
import torch


def init_project(language, project_name):

    os.environ["language"] = language
    i18n = I18nAuto(language=language)

    cache_path = os.path.join("cache", project_name)
    if not os.path.exists(cache_path):
        return None
    
    with open(os.path.join(cache_path, "configs.json"), "r") as f:
        configs = json.load(f)

    # configs = {
    #     "files": files,
    #     "tree": tree,
    #     "embedding_model": embedding_model_path,
    #     "base_model": model_path,
    #     "extensions": exts,
    #     "api_key": deepseek_api_key,
    #     "project_path": project_path,
    #     "project_name": project_name,
    # }
    vectors = torch.load(os.path.join(cache_path, "vectors.pt"))
    qwen_agent = QwenAgent(configs["base_model"])
    embedding_agent = RAGAgent(configs["embedding_model"], (vectors, configs))
    qwen_agent.__enter__()
    embedding_agent.__enter__()
    qa_agent = QwenCodebaseQAAgent(qwen_agent)
    sys_agent = QwenCodebaseSystemDesignAgent(qwen_agent)
    qa_ds_agent = None
    sys_ds_agent = None
    if configs["api_key"]:
        qa_ds_agent = OpenAICodebaseQAAgent(
            configs["api_key"]
        )
        sys_ds_agent = OpenAICodebaseSystemDesignAgent(
            configs["api_key"]
        )
        

    with gr.Blocks() as demo:
        gr.Markdown('# ' + i18n("title"))

        with gr.Tabs():

            with gr.TabItem(i18n("QA")):
                qa(i18n, qa_agent, embedding_agent, qa_ds_agent, None)

            with gr.TabItem(i18n("SystemDesign")):
                system_design(i18n, sys_agent, embedding_agent, configs["tree"], sys_ds_agent, None)

            with gr.TabItem(i18n("Fine-tuning"), visible=False):
                pass

    return demo, (qwen_agent, embedding_agent, qa_agent, sys_agent)
    

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Project Management")
    parser.add_argument(
        "--language",
        type=str,
        default="Auto",
        help="Language for the UI, default is Auto"
    )
    parser.add_argument(
        "--project",
        type=str,
        required=True,
        help="The name of the project to load"
    )

    args = parser.parse_args()

    demo, agents = init_project(args.language, args.project)

    demo.queue().launch(  # concurrency_count=511, max_size=1022
        server_name="0.0.0.0",
        inbrowser=True,
        # quiet=True,
    )