import sys
import os

import gradio as gr

from utils.i18n.i18n import I18nAuto, scan_language_list


language = sys.argv[-1] if sys.argv[-1] in scan_language_list() else "Auto"
os.environ["language"] = language
i18n = I18nAuto(language=language)

def main():
    with gr.Blocks() as demo:
        gr.Markdown('# ' + i18n("title"))

        with gr.Tabs():

            with gr.TabItem(i18n("Settings")):
                pass

            with gr.TabItem(i18n("Inference")):
                pass

            with gr.TabItem(i18n("Fine-tuning")):
                pass
    
    demo.launch(share=True)

if __name__ == "__main__":
    main()
        
        

