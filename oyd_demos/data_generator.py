import os

# load dotenv
from dotenv import load_dotenv
from openai import AzureOpenAI

load_dotenv()

client = AzureOpenAI(
    azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
    api_key=os.getenv("AZURE_OPENAI_API_KEY"),
    api_version="2024-02-15-preview"
)

DEPLOYMENT_LIST = ["gpt-4o", "gpt4-turbo", "gpt-4v"]
# read prompt from prompt.txt
with open("data_generator_prompt.txt") as f:
    prompt = f.read()


def get_openai_response(messages, model="gpt4-turbo", temperature=0.5, stream=False):
    response = client.chat.completions.create(
        model=model,

        temperature=temperature,
        max_tokens=4096,
        stream=True,
        # response_format={ "type": "json_object" },
        messages=messages
    )
    if stream:
        for chunk in response:
            if len(chunk.choices) > 0 and chunk.choices[0].delta.content is not None:
                yield chunk.choices[0].delta.content
    else:
        return response.choices[0].message.content


def user(history):
    # history = []
    return history + [["", ""]]


def get_cr_bot(model, is_stream, temperature, history):
    spec_response = get_openai_response(messages=[
        {"role": "system", "content": prompt},
        {"role": "user", "content": "please generate a new clinical record"}
    ], model=model, temperature=temperature, stream=is_stream)

    if is_stream:
        history[-1][1] = ""
        for chunk in spec_response:
            history[-1][1] += chunk
            yield history
    else:
        return spec_response





def save_file(history, file_path):
    with open(file_path, "w") as f:
        f.write(f"{history[-1][1]}")


def get_file_paths():
    # maximum id of the spec file
    ids = [int(f.split("_")[0]) for f in os.listdir("../data") if f.endswith("_clinical_record.md")]
    max_cr_id = 0
    if len(ids) > 0 : max_cr_id = max(ids)

    cr_path = f"../data/{max_cr_id + 1}_clinical_record.md"
    return cr_path


if __name__ == "__main__":
    import gradio as gr

    with gr.Blocks() as demo:
        with gr.Row():
            model_name_ddn = gr.Dropdown(choices=DEPLOYMENT_LIST, value="gpt-4o")
            is_stream_cb = gr.Checkbox(label="Stream", value=True)
            temperature_sldr = gr.Slider(minimum=0.0, maximum=1.0, value=0.5, step=0.1)
        with gr.Row():
            cr_bot = gr.Chatbot(height=700)
        with gr.Row():
            cr_btn = gr.Button("Generate CR")
        with gr.Row():
            save_cr_btn = gr.Button("Save CR")
        with gr.Row():
            with gr.Accordion():
                fpaths = get_file_paths()
                cr_file = gr.Textbox(label="CR file", value=fpaths)
                upd_btn = gr.Button("Update")
        with gr.Row():
            clear_btn = gr.Button("Clear")

        # (model, is_stream, temperature, history)
        cr_btn.click(user, cr_bot, cr_bot, queue=False).then(get_cr_bot,
                                                                   [model_name_ddn, is_stream_cb, temperature_sldr,
                                                                    cr_bot],
                                                                   cr_bot)

        upd_btn.click(get_file_paths, None, [cr_file], queue=False)
        save_cr_btn.click(save_file, [cr_bot, cr_file], outputs=None, queue=False)
        clear_btn.click(lambda: [None, None], None, [cr_bot], queue=False)

    demo.launch()
