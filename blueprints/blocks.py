import os

from notion_client import Client

notion = Client(auth=os.environ["NOTION_KEY"])


def create_page(parent_id, title):
    new_page = notion.pages.create(**{
        "parent": {
            "page_id": parent_id
        },
        "properties": {
            "title": {
                "title": [
                    {
                        "type": "text",
                        "text": {
                            "content": title,
                        },
                    }
                ]
            },
        },
    })
    return new_page


def create_database(parent_id, title, schema):
    approved_types = (
        "title", "rich_text", "number", "checkbox", "date", "people",
        "files", "url", "email", "phone_number", "select", "multi_select"
    )

    properties = {}
    for name, info in schema.items():
        prop_type = info["type"]
        if prop_type not in approved_types:
            raise ValueError(f"Property type '{prop_type}' is currently unsupported.")

        if prop_type in ["select", "multi_select"]:
            properties[name] = {prop_type: {"options": info["options"]}}
        else:
            properties[name] = {prop_type: {}}

    new_database = notion.databases.create(**{
        "parent": {"page_id": parent_id},
        "title": [
            {
                "type": "text",
                "text": {
                    "content": title
                }
            }
        ],
        "properties": properties
    })
    return new_database


def create_divider(parent_id):
    divider_block = notion.blocks.children.append(**{
        "block_id": parent_id,
        "children": [
            {
                "object": "block",
                "type": "divider",
                "divider": {},
            }
        ]
    })
    return divider_block


def create_heading(parent_id, text, level):
    heading_block = notion.blocks.children.append(**{
        "block_id": parent_id,
        "children": [
            {
                "object": "block",
                "type": f"heading_{level}",
                f"heading_{level}": {
                    "rich_text": [
                        {
                            "type": "text",
                            "text": {
                                "content": text
                            }
                        }
                    ],
                },
            }
        ]
    })
    return heading_block


def create_paragraph(parent_id, text):
    paragraph_block = notion.blocks.children.append(**{
        "block_id": parent_id,
        "children": [
            {
                "object": "block",
                "type": "paragraph",
                "paragraph": {
                    "rich_text": [
                        {
                            "type": "text",
                            "text": {
                                "content": text
                            }
                        }
                    ],
                },
            }
        ]
    })
    return paragraph_block


def create_list(parent_id, items, bulleted=True):
    list_type = "bulleted_list_item" if bulleted else "numbered_list_item"
    children = [{
        "object": "block",
        "type": list_type,
        list_type: {
            "rich_text": [
                {
                    "type": "text",
                    "text": {
                        "content": item
                    }
                }
            ]
        }
    } for item in items]

    list_block = notion.blocks.children.append(**{
        "block_id": parent_id,
        "children": children
    })
    return list_block


def create_todo_list(parent_id, items):
    children = [{
        "object": "block",
        "type": "to_do",
        "to_do": {
            "rich_text": [
                {
                    "type": "text",
                    "text": {
                        "content": item["text"]
                    }
                }
            ],
            "checked": item.get("checked", False),
        },
    } for item in items]

    todo_block = notion.blocks.children.append(**{
        "block_id": parent_id,
        "children": children
    })
    return todo_block


def create_toggle(parent_id, title):
    toggle_block = notion.blocks.children.append(**{
        "block_id": parent_id,
        "children": [
            {
                "object": "block",
                "type": "toggle",
                "toggle": {
                    "rich_text": [
                        {
                            "type": "text",
                            "text": {
                                "content": title
                            }
                        }
                    ],
                }
            }
        ]
    })
    return toggle_block
