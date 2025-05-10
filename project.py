import sys
import os

import gradio as gr

from utils.i18n.i18n import I18nAuto, scan_language_list
from ui_components.qa import qa



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


with gr.Blocks() as demo:
    gr.Markdown('# ' + i18n("title"))

    with gr.Tabs():

        with gr.TabItem(i18n("QA")):
            qa(i18n, None, None, None, None)

        with gr.TabItem(i18n("Inference")):
            pass

        with gr.TabItem(i18n("Fine-tuning")):
            pass
    

if __name__ == "__main__":
    demo.queue().launch(  # concurrency_count=511, max_size=1022
        server_name="0.0.0.0",
        inbrowser=True,
        # quiet=True,
    )