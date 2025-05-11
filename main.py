import sys
import os
import shutil
import subprocess
from subprocess import Popen

import gradio as gr
from transformers import AutoModelForCausalLM, AutoTokenizer, AutoModel

from config import REASONING_MODELS, EMBEDDING_MODELS, LOCAL_MODELS
from utils.i18n.i18n import I18nAuto, scan_language_list
from agents.rag_agent import RAGAgent
from agents.qwen_agents import QwenCodebaseQAAgent



language = sys.argv[-1] if sys.argv[-1] in scan_language_list() else "Auto"
os.environ["language"] = language
i18n = I18nAuto(language=language)


class ProjectState:

    def __init__(self):
        self.chat_history = []
        self.answers_cache = []
        self.embedding_db = None
        self.chat_agent = None
        self.embedding_agent = None

project_page = None

def main():
    with gr.Blocks() as demo:
        gr.Markdown('# ' + i18n("title"))

        projects = gr.State([])

        with gr.Row():
            projects_dropdown = gr.Dropdown(label=i18n("select_project_name"), choices=[])

        project_name = gr.Textbox(label=i18n("project_name"), value="")

        project_path = gr.Textbox(label=i18n("project_path"), value="")

        extensions = gr.Textbox(
            label=i18n("extensions"),
            value=",".join(["py", "java", "cpp", "js"]),
        ),
        
        project_model = gr.Dropdown(label=i18n("select_model"), choices=list(LOCAL_MODELS.keys()))

        project_embedding_model = gr.Dropdown(label=i18n("select_embedding_model"), choices=list(EMBEDDING_MODELS.keys()))

        create_project = gr.Button(i18n("create_project"))


        status_info = gr.Textbox(label=i18n("project_status"), visible=False)

        @create_project.click(
            inputs=[projects, project_name, project_path, extensions, project_model, project_embedding_model],
            outputs=[projects_dropdown, status_info]
        )
        def create_project(projects, project_name, project_path, extensions, project_model, project_embedding_model, pg_bar=gr.Progress()):
            pg_bar(0.1, desc=i18n("creating_project"))

            cache_path = os.path.join("cache", project_name)
            if os.path.exists(cache_path):
                gr.Error(i18n("project_already_exists"))
                return gr.Dropdown(label=i18n("select_project_name"), choices=projects), gr.Textbox(visible=False)
            os.makedirs(cache_path, exist_ok=True)

            projects.append(project_name)

            pg_bar(0.2, desc=i18n("loading_project_model"))
            model_path = LOCAL_MODELS[project_model]
            with QwenCodebaseQAAgent(model_path) as qa_agent:
                pass

            pg_bar(0.4, desc=i18n("loading_embedding_model"))
            embedding_model_path = EMBEDDING_MODELS[project_embedding_model]
            with RAGAgent(embedding_model_path, db_path=cache_path) as embedding_agent:
                pass
            
            embedding_model = AutoModel.from_pretrained(embedding_model_path, trust_remote_code=True).to("cuda")
            embedding_tokenizer = AutoTokenizer.from_pretrained(embedding_model_path)

            pg_bar(0.6, desc=i18n("traversing_project_path"))
            exts = extensions.split(",")
            RAGAgent.indexing(
                embedding_model=embedding_model,
                embedding_tokenizer=embedding_tokenizer,
                codebase=project_path,
                extensions=exts,
                db_path=cache_path
            )

            pg_bar(0.8, desc=i18n("loading_web_app"))
            cmd = f'python project.py --lang {language} --project {project_name}'
            global project_page
            project_page = Popen(cmd, shell=True)
            return gr.Dropdown(label=i18n("select_project_name"), choices=projects), gr.Textbox(value=i18n("project_status"), visible=True)
        
        def kill_project():
            global project_page
            if project_page:
                project_page.kill()
                project_page = None
    
    demo.launch()

if __name__ == "__main__":
    main()
        
        

