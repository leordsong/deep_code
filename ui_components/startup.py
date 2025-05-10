import gradio as gr
from transformers import AutoModelForCausalLM, AutoTokenizer, AutoModel

from config import REASONING_MODELS, EMBEDDING_MODELS, LOCAL_MODELS
from utils.i18n.i18n import I18nAuto, scan_language_list



def startup(i18n, project_state=None):

    projects = gr.State([])

    with gr.Row():
        projects_dropdown = gr.Dropdown(label=i18n("select_project_name"), choices=[])

    project_name = gr.Textbox(label=i18n("project_name"), value="")

    project_path = gr.Textbox(label=i18n("project_path"), value="")
    
    project_model = gr.Dropdown(label=i18n("select_model"), choices=list(LOCAL_MODELS.keys()))

    project_embedding_model = gr.Dropdown(label=i18n("select_embedding_model"), choices=list(EMBEDDING_MODELS.keys()))

    create_project = gr.Button(i18n("create_project"))

    @create_project.click(
        inputs=[projects, project_name, project_path, project_model, project_embedding_model],
        outputs=[projects_dropdown]
    )
    def create_project(projects, project_name, project_path, project_model, project_embedding_model, pg_bar=gr.Progress()):
        pg_bar(0.1, desc=i18n("creating_project"))
        projects.append(project_name)
        pg_bar(0.2, desc=i18n("loading_project_model"))
        model_path = LOCAL_MODELS[project_model]
        AutoModelForCausalLM.from_pretrained(model_path)
        AutoTokenizer.from_pretrained(model_path)
        pg_bar(0.4, desc=i18n("loading_embedding_model"))
        embedding_model_path = EMBEDDING_MODELS[project_embedding_model]
        AutoModel.from_pretrained(embedding_model_path, trust_remote_code=True)
        AutoTokenizer.from_pretrained(embedding_model_path)
        pg_bar(0.6, desc=i18n("traversing_project_path"))
        pg_bar(0.8, desc=i18n("loading_web_app"))
        return gr.Dropdown(label=i18n("select_project_name"), choices=projects)

