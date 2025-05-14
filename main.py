import sys
import os
import shutil
import subprocess
from subprocess import Popen
import json

import gradio as gr
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer, AutoModel

from config import REASONING_MODELS, EMBEDDING_MODELS, LOCAL_MODELS
from utils.i18n.i18n import I18nAuto, scan_language_list
from agents.rag_agent import RAGAgent
from agents.qwen_agents import QwenAgent
from utils.logger import logger



language = sys.argv[-1] if sys.argv[-1] in scan_language_list() else "Auto"
os.environ["language"] = language
i18n = I18nAuto(language=language)

project_page = None

def main():
    with gr.Blocks() as demo:
        gr.Markdown('# ' + i18n("title"))

        projects = gr.State([])

        projects_list = [directory for directory in os.listdir("cache") if os.path.isdir(os.path.join("cache", directory))]

        with gr.Group():
            status_info = gr.Textbox(label=i18n("project_status"), visible=False)
            kill_project_btn = gr.Button(i18n("kill_project"), visible=False)
        

        with gr.Group():
            projects_dropdown = gr.Dropdown(label=i18n("select_project_name"), choices=projects_list)
            join_project = gr.Button(i18n("join_project"))

        with gr.Group():
            gr.Markdown('## ' + i18n("create_project"))
            project_name = gr.Textbox(label=i18n("project_name"), value="")

            project_path = gr.Textbox(label=i18n("project_path"), value="")

            extensions = gr.Textbox(
                label=i18n("extensions"),
                value=",".join(["py", "java", "cpp", "js"]),
            )
            
            project_model = gr.Dropdown(label=i18n("select_model"), choices=list(LOCAL_MODELS.keys()))

            project_embedding_model = gr.Dropdown(label=i18n("select_embedding_model"), choices=list(EMBEDDING_MODELS.keys()))

            deepseek_api_key = gr.Textbox(label=i18n("deepseek_api_key"), value="")

            create_project = gr.Button(i18n("create_project"))

        @create_project.click(
            inputs=[projects, project_name, project_path, extensions, project_model, project_embedding_model, deepseek_api_key],
            outputs=[projects_dropdown, status_info, kill_project_btn]
        )
        def create_project(
            projects, project_name, project_path, extensions, project_model,
            project_embedding_model,
            deepseek_api_key,
            pg_bar=gr.Progress()
        ):
            logger.info(f"Creating project {project_name} at {project_path}")
            pg_bar(0.1, desc=i18n("creating_project"))

            project_path = os.path.abspath(project_path)
            cache_path = os.path.join("cache", project_name)
            if os.path.exists(cache_path):
                logger.error(f'Project {project_name} already exists')
                raise gr.Error(i18n("project_already_exists"))

            projects.append(project_name)

            pg_bar(0.2, desc=i18n("loading_project_model"))
            model_path = LOCAL_MODELS[project_model]
            with QwenAgent(model_path) as _:
                pass

            pg_bar(0.4, desc=i18n("loading_embedding_model"))
            embedding_model_path = EMBEDDING_MODELS[project_embedding_model]
            with RAGAgent(embedding_model_path, db_path=None) as rag_agent:
                pg_bar(0.6, desc=i18n("traversing_project_path"))
                exts = extensions.split(",")
                vectors, files, tree = RAGAgent.indexing(
                    embedding_model=rag_agent.embedding_model,
                    embedding_tokenizer=rag_agent.embedding_tokenizer,
                    codebase=project_path,
                    extensions=exts
                )

            if not files:
                raise gr.Error(i18n("no_files_found"))

            pg_bar(0.8, desc=i18n("loading_web_app"))
            os.makedirs(cache_path, exist_ok=True)
            torch.save(vectors, os.path.join(cache_path, "vectors.pt"))
            configs = {
                "files": files,
                "tree": tree,
                "embedding_model": embedding_model_path,
                "base_model": model_path,
                "extensions": exts,
                "api_key": deepseek_api_key,
                "project_path": project_path,
                "project_name": project_name,
            }
            with open(os.path.join(cache_path, "configs.json"), "w", encoding='utf-8') as f:
                json.dump(configs, f)

            cmd = f'python project.py --lang {language} --project {project_name}'
            global project_page
            project_page = Popen(cmd, shell=True)
            return gr.Dropdown(label=i18n("select_project_name"), choices=projects), gr.Textbox(value=i18n("project_status"), visible=True), gr.Button(visible=True)
        
        @kill_project_btn.click(
            inputs=[],
            outputs=[status_info, kill_project_btn],
        )
        def kill_project():
            global project_page
            if project_page:
                logger.info(f"Killing project {project_page.pid}")
                project_page.kill()
                project_page = None
            return gr.Textbox(visible=False), gr.Button(visible=False)

        

        @join_project.click(
            inputs=[projects_dropdown],
            outputs=[projects_dropdown, status_info, kill_project_btn],
        )
        def join_project(project_name):
            cmd = f'python project.py --lang {language} --project {project_name}'
            global project_page
            project_page = Popen(cmd, shell=True)
            return gr.Dropdown(label=i18n("select_project_name"), choices=projects_list), gr.Textbox(value=i18n("project_running"), visible=True), gr.Button(visible=True)
    
    demo.launch(inbrowser=True)

if __name__ == "__main__":
    main()
        
        

