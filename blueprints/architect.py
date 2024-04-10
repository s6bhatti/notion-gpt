from .blocks import create_page, create_database, create_divider, create_heading, create_paragraph


def process_blueprint(parent_id, block_json):
    block_type = block_json["type"]

    if block_type == "page":
        title = block_json.get("title", "Untitled Page")
        page_id = create_page(parent_id, title)["id"]
        for child in block_json.get("children", []):
            process_blueprint(page_id, child)
    elif block_type == "database":
        title = block_json.get("title", "Untitled Database")
        schema = block_json.get("schema", {})
        create_database(parent_id, title, schema)
    elif block_type == "divider":
        create_divider(parent_id)
    elif block_type.startswith("heading_"):
        text = block_json.get("text", "")
        level = int(block_type.split("_")[1])
        create_heading(parent_id, text, level)
    elif block_type == "paragraph":
        text = block_json.get("text", "")
        create_paragraph(parent_id, text)
