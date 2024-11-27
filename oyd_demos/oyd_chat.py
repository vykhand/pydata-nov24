import os

# load dotenv
from dotenv import load_dotenv
from openai import AzureOpenAI
from oyd_demos import zakon_index as ZI

load_dotenv()

client = AzureOpenAI(
    azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
    api_key=os.getenv("AZURE_OPENAI_API_KEY"),
    api_version="2024-02-15-preview"
)

DEPLOYMENT_LIST = ["gpt-4o", "gpt4-turbo", "gpt-4v"]
# read prompt from prompt.txt
with open("chat_system_prompt.txt") as f:
    prompt = f.read()


def get_openai_response(messages, model="gpt4-turbo", temperature=0.5, stream=False):
    response = client.chat.completions.create(
        model=model,

        temperature=temperature,
        max_tokens=4096,
        stream=stream,
        # response_format={ "type": "json_object" },
        messages=messages,
        extra_body=ZI.extra_body
    )
    if stream:
        for chunk in response:
            if len(chunk.choices) > 0 and chunk.choices[0].delta.content is not None:
                yield chunk.choices[0].delta.content
    else:
        return response.choices[0]


def user(user_message, history: list):
    return "", history + [{"role": "user", "content": user_message}]



def get_stream(history, model, temperature):
    msg = history[-1]["content"]
    history.append({"role": "assistant", "content": ""})
    bot_response = get_openai_response(messages=[
        {"role": "system", "content": prompt},
        {"role": "user", "content": msg }
    ], model=model, temperature=temperature, stream=True)

    for chunk in bot_response:
        history[-1]['content'] += chunk
        yield history


def respond(msg, chat_history, model, temperature):
    bot_response = get_openai_response(messages=[
        {"role": "system", "content": prompt},
        {"role": "user", "content": msg }
    ], model=model, temperature=temperature, stream=False)
    chat_history.append({"role": "user", "content": msg})
    next_resp = next(bot_response)
    chat_history.append({"role": "assistant", "content": next_resp.message.content})
    return "", chat_history, bot_response


if __name__ == "__main__":
    import gradio as gr

    with gr.Blocks() as demo:
        with gr.Row():
            with gr.Accordion("Settings", open=False):
                model_name_ddn = gr.Dropdown(choices=DEPLOYMENT_LIST, value="gpt-4o")
                temperature_sldr = gr.Slider(minimum=0.0, maximum=1.0, value=0.5, step=0.1)
        with gr.Tab("Streaming"):
            with gr.Row():
                stream_bot_input_tb = gr.Textbox(label="Input", value="what is the punishment  for kicking hedgehog?")
                stream_bot_btn = gr.Button("Submit", scale=0)
            with gr.Row():
                stream_bot = gr.Chatbot(type="messages", height=700)
            with gr.Row():
                stream_bot_clear_btn = gr.Button("Clear")
        with gr.Tab("QA"):
            with gr.Row():
                bot_input_tb = gr.Textbox(label="Input", value="what is the punishment  for kicking hedgehog?")
                bot_btn = gr.Button("Submit", scale=0)
            with gr.Row():
                bot = gr.Chatbot(type="messages", height=700)
            with gr.Row():
                bot_clear_btn = gr.Button("Clear")

        # (model, is_stream, temperature, history)
        stream_bot_btn.click(user, [stream_bot_input_tb, stream_bot],
                             [stream_bot_input_tb, stream_bot], queue=False).then(get_stream,
                                                             [stream_bot, model_name_ddn, temperature_sldr],
                                                             stream_bot)

        stream_bot_input_tb.submit(user, [stream_bot_input_tb, stream_bot],
                             [stream_bot_input_tb, stream_bot], queue=False).then(get_stream,
                                                             [stream_bot, model_name_ddn, temperature_sldr],
                                                             stream_bot)

        stream_bot_clear_btn.click(lambda: None, None, stream_bot, queue=False)
        bot_btn.click(respond, [bot_input_tb, bot, model_name_ddn, temperature_sldr], [bot_input_tb, bot], queue=False)

    demo.launch(share=True)
