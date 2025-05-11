import gradio as gr

from utils.i18n.i18n import I18nAuto, scan_language_list
from agents.rag_agent import RAGAgent
from agents.openai_agents import ChatOpenAIAgent
from agents.qwen_agents import QwenCodebaseQAAgent


def qa(i18n, qa_agent, embedding_agent, answers_cache_agent=None):
    chatbot = gr.Chatbot(type="messages")
    msg = gr.Textbox()
    
    with gr.Column():
        submit = gr.Button(i18n("submit"))
        clear = gr.ClearButton([msg, chatbot])
    wrong_answer = gr.Button(i18n("wrong_answer"))
    

    def respond(message, chat_history, pg_bar=gr.Progress()):
        pg_bar(0, desc=i18n("Translate to vector space"))
        if not embedding_agent:
            codes = []
        else:
            codes = embedding_agent(message)

        pg_bar(0.4, desc=i18n("Calling LLM"))
        question, answer = qa_agent(message, codes)

        pg_bar(0.8, desc=i18n("Generating answer"))
        chat_history.append({"role": "user", "content": question})
        chat_history.append({"role": "assistant", "content": answer})        
        return "", chat_history

    msg.submit(respond, [msg, chatbot], [msg, chatbot])
    submit.click(respond, [msg, chatbot], [msg, chatbot])


if __name__ == "__main__":

    i18n = I18nAuto("zh_CN")
    # , RAGAgent("Salesforce/codet5p-110m-embedding", "data/db") as embedding_agent
    with QwenCodebaseQAAgent("Qwen/Qwen2.5-Coder-7B-Instruct") as qa_agent:
        with gr.Blocks() as demo:
            qa(i18n, qa_agent, None)

        demo.queue().launch(  # concurrency_count=511, max_size=1022
            server_name="0.0.0.0",
            inbrowser=True,
        )

