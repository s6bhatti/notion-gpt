import os

from notion_client import Client

NOTION_KEY = os.environ["NOTION_KEY"]
notion = Client(auth=NOTION_KEY)


def process_page(page_id):
    page = notion.pages.retrieve(page_id)
    page_title = page["properties"]["title"]["title"][0]["text"]["content"]
    page_children = fetch_and_process_children(page_id)
    page_blueprint = {
        "type": "page",
        "title": page_title,
        "children": page_children
    }
    return page_blueprint


def fetch_and_process_children(parent_id):
    children = []
    block_children = notion.blocks.children.list(block_id=parent_id)["results"]

    list_buffer = None

    for child in block_children:
        if child["type"] in ["bulleted_list_item", "numbered_list_item", "to_do"]:
            list_type = "to_do_list" if child["type"] == "to_do" else "bulleted_list" if child["type"] == "bulleted_list_item" else "numbered_list"

            if list_buffer is None or list_buffer["type"] != list_type:
                if list_buffer:
                    children.append(list_buffer)
                list_buffer = {"type": list_type, "items": []}

            if list_type == "to_do_list":
                todo_item_text = child["to_do"]["rich_text"][0]["text"]["content"]
                todo_item_checked = child["to_do"]["checked"]
                list_buffer["items"].append({"text": todo_item_text, "checked": todo_item_checked})
            else:
                list_item_text = child[child["type"]]["rich_text"][0]["text"]["content"]
                list_buffer["items"].append(list_item_text)

        else:
            if list_buffer:
                children.append(list_buffer)
                list_buffer = None

            formatted_block = format_block(child)

            if child.get("has_children", False):
                formatted_block["columns" if child["type"] == "column_list" else "children"] = fetch_and_process_children(child["id"])

            children.append(formatted_block)

    if list_buffer:
        children.append(list_buffer)

    return children


def format_block(block):
    block_type = block["type"]
    block_json = {"type": block_type}

    if block_type == "child_page":
        block_json["type"] = "page"
        block_json["title"] = block["child_page"]["title"]

    elif block_type == "child_database":
        block_json["type"] = "database"
        database_details = notion.databases.retrieve(database_id=block["id"])
        block_json["title"] = database_details["title"][0]["plain_text"]
        properties = {}
        for prop_name, prop_details in database_details["properties"].items():
            prop_type = prop_details["type"]
            if prop_type in ["select", "multi_select"]:
                options = [{"name": option["name"], "color": option.get("color", "default")} for option in
                           prop_details[prop_type]["options"]]
                properties[prop_name] = {"type": prop_type, "options": options}
            elif prop_type == "number":
                properties[prop_name] = {"type": prop_type, "format": prop_details["number"].get("format", "none")}
            else:
                properties[prop_name] = {"type": prop_type}
        block_json["schema"] = properties

    if block_type == "paragraph":
        if block["paragraph"]["rich_text"]:
            block_json["text"] = block["paragraph"]["rich_text"][0]["text"]["content"]
        else:
            block_json["text"] = ""

    elif block_type.startswith("heading_"):
        block_json["text"] = block[block_type]["rich_text"][0]["text"]["content"]

    elif block_type == "bulleted_list_item":
        block_json["items"] = [text["plain_text"] for text in block["bulleted_list_item"]["rich_text"]]

    elif block_type == "numbered_list_item":
        block_json["items"] = [text["plain_text"] for text in block["numbered_list_item"]["rich_text"]]

    elif block_type == "to_do":
        block_json["text"] = block["to_do"]["rich_text"][0]["text"]["content"]
        block_json["checked"] = block["to_do"]["checked"]

    elif block_type == "toggle":
        block_json["title"] = block["toggle"]["rich_text"][0]["text"]["content"]

    elif block_type == "callout":
        block_json["text"] = block["callout"]["rich_text"][0]["text"]["content"]
        block_json["icon"] = block["callout"]["icon"]["emoji"]
        block_json["color"] = block["callout"]["color"]

    elif block_type == "quote":
        block_json["text"] = block["quote"]["rich_text"][0]["text"]["content"]

    return block_json