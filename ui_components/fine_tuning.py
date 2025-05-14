import gradio as gr
import json

from utils.i18n.i18n import I18nAuto, scan_language_list
from agents.rag_agent import RAGAgent
from agents.openai_agents import ChatOpenAIAgent
from agents.qwen_agents import QwenCodebaseQAAgent, QwenAgent
from agents.rag_agent import RAGAgent
from agents.training_agent import TrainingAgent


def fine_tuning(i18n, qwen_agent:QwenAgent, embedding_agent:RAGAgent, qa_train_data, cache_path):

    train_data = gr.State([])
    validation_data = gr.State([])

    # target = gr.Dropdown(label=i18n("select_target"), choices=[i18n("QA"), i18n("SystemDesign")], value=i18n("QA"))
    epochs = gr.Slider(label=i18n("epochs"), minimum=1, maximum=10, step=1, value=2)
    batch_size = gr.Slider(label=i18n("batch_size"), minimum=1, maximum=64, step=1, value=4)
    learning_rate = gr.Number(label=i18n("learning_rate"), value=1e-5)
    with gr.Accordion(i18n("data_format"), open=False):
        gr.Markdown(i18n("only_json_files"))
        gr.Code("[\n \"...\", \n ...\n]", language='json')  # Example JSON format

    with gr.Row():
        with gr.Column():
            training_data_files = gr.File(label=i18n("training_data"), file_count="multiple", file_types=[".json"])
            clear_train_data = gr.Button(i18n("clear_training_data"))
            @gr.render(
                inputs=[train_data, qa_train_data]
            )
            def render_train_data(train_data, qa_data):
                gr.DataFrame(
                    value=train_data + qa_data,
                    visible=True,
                    label=i18n("training_data"),
                )
        with gr.Column():
            validation_data_files = gr.File(label=i18n("validation_data"), file_count="multiple", file_types=[".json"])
            clear_valid_data = gr.Button(i18n("clear_validation_data"))
            @gr.render(
                inputs=[validation_data]
            )
            def render_validation_data(validation_data):
                gr.DataFrame(
                    value=validation_data,
                    visible=True,
                    label=i18n("validation_data"),
                )
    
    clear_train_data.click(lambda: [], inputs=[], outputs=[train_data])
    clear_valid_data.click(lambda: [], inputs=[], outputs=[validation_data])

    def upload_files(files, data_state):
        for file in files:
            with open(file.name, "r") as f:
                data_state.extend(json.load(f))
        return data_state

    training_data_files.upload(
        upload_files,
        inputs=[training_data_files, train_data],
        outputs=[train_data]
    )

    validation_data_files.upload(
        upload_files,
        inputs=[validation_data_files, validation_data],
        outputs=[validation_data]
    )


    # @gr.render(
    #     inputs=[train_data, validation_data, target]
    # )
    # def training_data_files(train_data, validation_data, target):
    #     data = cache_agent.get_data(target == i18n("qa"))
    #     with gr.Column():
    #         gr.DataFrame(
    #             value=train_data + data,
    #             visible=True,
    #             label=i18n("training_data"),
    #         )
    #         gr.DataFrame(
    #             value=validation_data,
    #             visible=True,
    #             label=i18n("validation_data"),
    #         )

    train_btn = gr.Button(i18n("train"))
    @train_btn.click(
        inputs=[train_data, validation_data, epochs, batch_size, learning_rate],
        outputs=[gr.Textbox(label=i18n("training_result"))]
    )
    def train_model(train_data, validation_data, epochs, batch_size, learning_rate, pg_bar=gr.Progress()):
        qwen_agent.close()
        embedding_agent.close()

        try:
            pg_bar(0, desc=i18n("Loading model"))
            with TrainingAgent(
                'ft_model',
                qwen_agent.model_name,
                cache_path,
                batch_size=batch_size,
                learning_rate=learning_rate,
                num_epochs=epochs,
            ) as training_agent:
                pg_bar(0.2, desc=i18n("Training"))
                result = training_agent(
                    train_data,
                    validation_data
                )
                qwen_agent.model_name = training_agent.output_dir
                pg_bar(0.8, desc=i18n("Finished"))
            return i18n("Finished")
        except Exception as e:
            raise gr.Error(i18n("training_failed") + str(e))
        finally:
            qwen_agent.open()
            embedding_agent.open()
