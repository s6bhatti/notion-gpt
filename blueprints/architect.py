from .blocks import (create_page, create_database, create_divider, create_heading,
                     create_paragraph, create_list, create_todo_list, create_toggle)


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
    elif block_type in ["bulleted_list", "numbered_list"]:
        items = block_json.get("items", [])
        create_list(parent_id, items, bulleted=True if block_type == "bulleted_list" else False)
    elif block_type == "to_do_list":
        items = block_json.get("items", [])
        create_todo_list(parent_id, items)
    elif block_type == "toggle":
        title = block_json.get("title", "Untitled Toggle")
        toggle_id = create_toggle(parent_id, title)["results"][0]["id"]
        for child in block_json.get("children", []):
            process_blueprint(toggle_id, child)
