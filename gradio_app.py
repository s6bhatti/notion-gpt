import json
import os
import time

import gradio as gr
from pydantic import ValidationError

from blueprints.architect import generate_blueprint, process_blueprint
from blueprints.schema import OpenAIResponse

NOTION_PAGE_ID = os.environ["NOTION_PAGE_ID"]
MODEL_NAME = os.environ["NOTION_GPT_MODEL_NAME"]


def gradio_blueprint_interface(description, model_name, force_json, auto_restart, temperature, top_p, error=None, failed_response=None):
    try:
        cumulative_content = ""
        for update in generate_blueprint(description, model_name, force_json, temperature, top_p, error, failed_response):
            if isinstance(update, dict):
                yield "Blueprint generation complete. Processing blueprint..."
                try:
                    OpenAIResponse(**update)
                    process_blueprint(NOTION_PAGE_ID, update.get("blueprint", {}))
                    yield f"Blueprint successfully processed! 🎉"
                except ValidationError as e:
                    error = json.dumps(e.json(), separators=(",", ":"))
                    failed_response = json.dumps(update, separators=(",", ":"))
                    if auto_restart:
                        yield f"Validation failed: f{error}. Restarting..."
                        time.sleep(5)
                        yield from gradio_blueprint_interface(description, model_name, force_json, auto_restart, temperature, top_p, error, failed_response)
                    else:
                        yield f"Validation failed: f{error}."
            else:
                cumulative_content += update
                yield cumulative_content
    except Exception as e:
        if auto_restart:
            yield f"Error encountered: {str(e)}. Restarting..."
            time.sleep(5)
            yield from gradio_blueprint_interface(description, model_name, force_json, auto_restart, temperature, top_p)
        else:
            yield f"Error encountered: {str(e)}."


def main():
    iface = gr.Interface(
        fn=gradio_blueprint_interface,
        inputs=[
            gr.Textbox(label="Describe your Notion page", value="Generate me a detailed and comprehensive Notion page to plan a 2-week vacation to Tokyo and Kyoto."),
            gr.Dropdown(label="OpenAI Model", choices=[MODEL_NAME, "gpt-4-turbo", "gpt-4o", "gpt-3.5-turbo"], value=MODEL_NAME),
        ],
        additional_inputs=[
            gr.Checkbox(label="Force JSON", value=False),
            gr.Checkbox(label="Auto Restart", value=True),
            gr.Slider(label="Temperature", minimum=0.1, maximum=1.0, step=0.1, value=0.4),
            gr.Slider(label="Top P", minimum=0.1, maximum=1.0, step=0.1, value=0.9),
        ],
        outputs=[gr.Text(label="Process Output")],
        title="NotionGPT",
        description="Enter a description to generate and process a custom Notion page layout."
    )
    iface.launch()


if __name__ == "__main__":
    main()
