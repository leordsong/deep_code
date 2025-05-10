import gradio as gr




def qa(i18n, llm_agent, embedding_agent, retriever_agent, answers_cache_agent):
    chatbot = gr.Chatbot(type="messages")
    msg = gr.Textbox()
    
    with gr.Column():
        submit = gr.Button(i18n("submit"))
        clear = gr.ClearButton([msg, chatbot])
    wrong_answer = gr.Button(i18n("wrong_answer"))
    

    def respond(message, chat_history, pg_bar=gr.Progress()):
        pg_bar(0, desc=i18n("Translate to vector space"))
        # TODO

        pg_bar(0.3, desc=i18n("Reteriving relevant code"))
        # TODO

        pg_bar(0.6, desc=i18n("Calling LLM"))
        # TODO

        pg_bar(0.8, desc=i18n("Generating answer"))
        bot_message = llm_agent(message)
        chat_history.append({"role": "user", "content": message})
        chat_history.append({"role": "assistant", "content": bot_message})        
        return "", chat_history

    msg.submit(respond, [msg, chatbot], [msg, chatbot])
    submit.click(respond, [msg, chatbot], [msg, chatbot])
