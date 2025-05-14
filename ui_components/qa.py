import gradio as gr

from utils.i18n.i18n import I18nAuto, scan_language_list
from agents.rag_agent import RAGAgent
from agents.qwen_agents import QwenCodebaseQAAgent, QwenAgent
from agents.sft_cache_agent import SFTCacheAgent


def qa_UI(i18n, qa_agent, embedding_agent, train_data, ds_qa_agent=None, tree=None):
    chatbot = gr.Chatbot(type="messages")
    msg = gr.Textbox()

    
    with gr.Column():
        use_deepseek = gr.Checkbox(label=i18n("use_deepseek"), value=False, visible=ds_qa_agent is not None)
        submit = gr.Button(i18n("submit"))
        clear = gr.ClearButton([msg, chatbot], value=i18n("clear"))
    wrong_answer = gr.Button(i18n("wrong_answer"))

    with gr.Group():
        wrong_answer_text = gr.Textbox(label=i18n("wrong_answer_text"), value="", visible=False)
        wrong_answer_submit = gr.Button(i18n("wrong_answer_submit"), visible=False)
    

    def respond(message, chat_history, use_deepseek, pg_bar=gr.Progress()):
        pg_bar(0, desc=i18n("Translate to vector space"))
        if not embedding_agent:
            codes = []
        else:
            codes = embedding_agent(message)

        desc = i18n("Found") + f' {len(codes)} ' + i18n("relevant code") + ". " + i18n("Calling LLM")
        pg_bar(0.4, desc=desc)
        if use_deepseek and ds_qa_agent:
            if tree is not None:
                question, answer = ds_qa_agent(message, codes, tree)
            else:
                question, answer = ds_qa_agent(message, codes)
        else:
            if tree is not None:
                question, answer = qa_agent(message, codes, tree)
            else:
                question, answer = qa_agent(message, codes)

        pg_bar(0.8, desc=i18n("Generating answer"))
        chat_history.append({"role": "user", "content": question})
        chat_history.append({"role": "assistant", "content": answer})        
        return "", chat_history

    msg.submit(respond, [msg, chatbot, use_deepseek], [msg, chatbot])
    submit.click(respond, [msg, chatbot, use_deepseek], [msg, chatbot])

    @wrong_answer.click(
        inputs=[chatbot],
        outputs=[wrong_answer_text, wrong_answer_submit],
    )
    def wrong_answer_click(chat_history):
        if chat_history and chat_history[-1]["role"] == "assistant":
            wrong_answer = chat_history[-1]["content"]
            return gr.Textbox(value=wrong_answer, visible=True), gr.Button(visible=True)
        else:
            raise gr.Error(i18n("no_answer"))
        
    @wrong_answer_submit.click(
        inputs=[wrong_answer_text, chatbot, train_data],
        outputs=[wrong_answer_text, wrong_answer_submit, chatbot, train_data],
    )
    def wrong_answer_submit_click(wrong_answer_text, chat_history, train_data):
        question = chat_history[-2]["content"]
        chat_history[-1]["content"] = wrong_answer_text
        text = SFTCacheAgent.from_qwen_to_text(
            qa_agent.qwen_agent.tokenizer,
            wrong_answer_text,
            question,
            qa_agent.SYSTEM_PROMPT
        )
        train_data.append(text)
        return gr.Textbox(value="", visible=False), gr.Button(visible=False), chat_history, train_data


if __name__ == "__main__":

    i18n = I18nAuto("zh_CN")
    with QwenAgent("Qwen/Qwen2.5-Coder-7B-Instruct") as qwen_agent, RAGAgent("Salesforce/codet5p-110m-embedding", "./cache/test") as embedding_agent:
        qa_agent = QwenCodebaseQAAgent(qwen_agent)
        with gr.Blocks() as demo:
            qa_UI(i18n, qa_agent, embedding_agent)

        demo.queue().launch(  # concurrency_count=511, max_size=1022
            server_name="0.0.0.0",
            inbrowser=True,
        )

