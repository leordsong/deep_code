import gradio as gr

from utils.i18n.i18n import I18nAuto, scan_language_list
from agents.rag_agent import RAGAgent
from agents.openai_agents import ChatOpenAIAgent
from agents.qwen_agents import QwenCodebaseSystemDesignAgent


def system_design(i18n, sys_agent, embedding_agent, tree, ds_sys_agent=None, answers_cache_agent=None):
    chatbot = gr.Chatbot(type="messages")
    msg = gr.Textbox()
    
    with gr.Column():
        use_deepseek = gr.Checkbox(label=i18n("use_deepseek"), value=False, visible=ds_sys_agent is not None)
        submit = gr.Button(i18n("submit"))
        clear = gr.ClearButton([msg, chatbot], value=i18n("clear"))
    # wrong_answer = gr.Button(i18n("wrong_answer"))
    

    def respond(message, chat_history, use_deepseek, pg_bar=gr.Progress()):
        pg_bar(0, desc=i18n("Translate to vector space"))
        codes = embedding_agent(message)

        pg_bar(0.4, desc=i18n("Calling LLM"))
        if use_deepseek and ds_sys_agent:
            question, answer = ds_sys_agent(message, codes)
        else:
            question, answer = sys_agent(message, tree, codes)

        pg_bar(0.8, desc=i18n("Generating answer"))
        chat_history.append({"role": "user", "content": question})
        chat_history.append({"role": "assistant", "content": answer})        
        return "", chat_history

    msg.submit(respond, [msg, chatbot], [msg, chatbot, use_deepseek])
    submit.click(respond, [msg, chatbot], [msg, chatbot, use_deepseek])


if __name__ == "__main__":
    # qa_agent = QwenCodebaseQAAgent("Qwen/Qwen2.5-Coder-7B-Instruct")
    # embedding_agent = RAGAgent("Salesforce/codet5p-110m-embedding", "data/db")

    # i18n = I18nAuto("zh_CN")
    # with gr.Blocks() as demo, QwenCodebaseQAAgent("Qwen/Qwen2.5-Coder-7B-Instruct") as qa_agent, RAGAgent("Salesforce/codet5p-110m-embedding", "data/db") as embedding_agent:
    #     system_design(i18n, qa_agent, embedding_agent)

    # demo.queue().launch(  # concurrency_count=511, max_size=1022
    #     server_name="0.0.0.0",
    #     inbrowser=True,
    # )
    # print the tree structure of the current directory
    import os

    def print_tree(path, level=0, extensions=('py', 'java', 'js', 'cpp')):
        
        basename = os.path.basename(path)
        if basename.startswith('.') or basename == '__pycache__':
            return ''
        
        if os.path.isdir(path):
            dirname = "  " * level + basename + "/\n"
            result = ''
            for item in os.listdir(path):
                result += print_tree(os.path.join(path, item), level + 1)
            if result:
                return dirname + result
            return ''
        else:
            if any(basename.endswith(ext) for ext in extensions):
                return "  " * level + basename + "\n"
            else:
                return ''

