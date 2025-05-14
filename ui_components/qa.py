import gradio as gr

from utils.i18n.i18n import I18nAuto, scan_language_list
from agents.rag_agent import RAGAgent
from agents.openai_agents import ChatOpenAIAgent
from agents.qwen_agents import QwenCodebaseQAAgent, QwenAgent


def qa(i18n, qa_agent, embedding_agent, ds_qa_agent=None, answers_cache_agent=None):
    chatbot = gr.Chatbot(type="messages")
    msg = gr.Textbox()
    
    with gr.Column():
        use_deepseek = gr.Checkbox(label=i18n("use_deepseek"), value=False, visible=ds_qa_agent is not None)
        submit = gr.Button(i18n("submit"))
        clear = gr.ClearButton([msg, chatbot], value=i18n("clear"))
    wrong_answer = gr.Button(i18n("wrong_answer"), visible=False)
    

    def respond(message, chat_history, use_deepseek, pg_bar=gr.Progress()):
        pg_bar(0, desc=i18n("Translate to vector space"))
        if not embedding_agent:
            codes = []
        else:
            codes = embedding_agent(message)

        desc = i18n("Found") + f' {len(codes)} ' + i18n("relevant code") + ". " + i18n("Calling LLM")
        pg_bar(0.4, desc=desc)
        if use_deepseek and ds_qa_agent:
            question, answer = ds_qa_agent(message, codes)
        else:
            question, answer = qa_agent(message, codes)

        pg_bar(0.8, desc=i18n("Generating answer"))
        chat_history.append({"role": "user", "content": question})
        chat_history.append({"role": "assistant", "content": answer})        
        return "", chat_history

    msg.submit(respond, [msg, chatbot], [msg, chatbot, use_deepseek])
    submit.click(respond, [msg, chatbot], [msg, chatbot, use_deepseek])


if __name__ == "__main__":

    i18n = I18nAuto("zh_CN")
    with QwenAgent("Qwen/Qwen2.5-Coder-7B-Instruct") as qwen_agent, RAGAgent("Salesforce/codet5p-110m-embedding", "./cache/test") as embedding_agent:
        qa_agent = QwenCodebaseQAAgent(qwen_agent)
        with gr.Blocks() as demo:
            qa(i18n, qa_agent, embedding_agent)

        demo.queue().launch(  # concurrency_count=511, max_size=1022
            server_name="0.0.0.0",
            inbrowser=True,
        )

