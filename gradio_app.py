import gradio as gr
import os
import json
import time
from blueprints.architect import generate_blueprint, process_blueprint
from pydantic import ValidationError
from blueprints.schema import OpenAIResponse

NOTION_PAGE_ID = os.environ["NOTION_PAGE_ID"]


def gradio_blueprint_interface(description, force_json, temperature, top_p, error=None, failed_response=None):
    try:
        cumulative_content = ""
        for update in generate_blueprint(description, force_json, temperature, top_p, error, failed_response):
            if isinstance(update, dict):
                yield "Blueprint generation complete. Processing blueprint..."
                try:
                    OpenAIResponse(**update)
                    process_blueprint(NOTION_PAGE_ID, update.get("blueprint", {}))
                    yield f"Blueprint successfully processed! 🎉"
                except ValidationError as e:
                    error = json.dumps(e.json(), separators=(",", ":"))
                    failed_response = json.dumps(update, separators=(",", ":"))
                    yield f"Validation failed: f{error}. Restarting..."
                    time.sleep(5)
                    yield from gradio_blueprint_interface(description, force_json, temperature, top_p, error, failed_response)
            else:
                cumulative_content += update
                yield cumulative_content
    except Exception as e:
        yield f"Error encountered: {str(e)}. Restarting..."
        time.sleep(5)
        yield from gradio_blueprint_interface(description, force_json, temperature, top_p)


def main():
    iface = gr.Interface(
        fn=gradio_blueprint_interface,
        inputs=[
            gr.Textbox(label="Describe your Notion page", value="Generate me a detailed and comprehensive Notion page to plan a 2-week vacation to Tokyo and Kyoto."),
            gr.Checkbox(label="Force JSON", value=False),
            gr.Slider(label="Temperature", minimum=0.1, maximum=1.0, step=0.1, value=1.0),
            gr.Slider(label="Top P", minimum=0.1, maximum=1.0, step=0.1, value=0.4),
        ],
        outputs=[gr.Text(label="Process Output")],
        title="NotionGPT",
        description="Enter a description to generate and process a custom Notion page layout."
    )
    iface.launch()


if __name__ == "__main__":
    main()
