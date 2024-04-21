import os

import requests
from notion_client import Client

NOTION_KEY = os.environ["NOTION_KEY"]
UNSPLASH_ACCESS_KEY = os.environ["UNSPLASH_ACCESS_KEY"]

notion = Client(auth=NOTION_KEY)


def get_unsplash_image_url(query):
    params = {
        "query": query,
        "client_id": UNSPLASH_ACCESS_KEY,
        "orientation": "landscape"
    }
    response = requests.get("https://api.unsplash.com/search/photos", params=params)

    if response.status_code == 200:
        results = response.json()["results"]
        if results:
            return results[0]["urls"]["regular"]
    return None


def process_rich_text_content(text_blocks):
    rich_text_content = []
    for block in text_blocks:
        text_content = {
            "type": "text",
            "text": {
                "content": block["text"],
                "link": None
            },
            "annotations": {
                "bold": "bold" in block.get("style", []),
                "italic": "italic" in block.get("style", []),
                "strikethrough": "strikethrough" in block.get("style", []),
                "underline": "underline" in block.get("style", []),
                "code": "code" in block.get("style", []),
                "color": "default"
            }
        }
        rich_text_content.append(text_content)
    return rich_text_content


def create_page(parent_id, title, icon, cover_image=True):
    image_url = get_unsplash_image_url(title) if cover_image else None
    new_page = notion.pages.create(**{
        "parent": {
            "page_id": parent_id
        },
        "icon": {
            "emoji": icon
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
        "cover": {
            "type": "external",
            "external": {
                "url": image_url
            }
        } if image_url else {}
    })
    return new_page


def create_database(parent_id, title, icon, schema, cover_image=True):
    image_url = get_unsplash_image_url(title) if cover_image else None
    approved_types = ("checkbox", "created_by", "created_time", "date", "email", "files", "last_edited_by",
                      "last_edited_time", "multi_select", "number", "people", "phone_number", "rich_text", "select",
                      "title", "url")

    properties = {}
    for name, info in schema.items():
        prop_type = info["type"]
        if prop_type not in approved_types:
            raise ValueError(f"Property type '{prop_type}' is currently unsupported.")

        if prop_type in ["select", "multi_select"]:
            properties[name] = {prop_type: {"options": info["options"]}}
        elif prop_type == "number":
            properties[name] = {prop_type: {"format": info["format"]}}
        else:
            properties[name] = {prop_type: {}}

    new_database = notion.databases.create(**{
        "parent": {
            "page_id": parent_id
        },
        "icon": {
            "emoji": icon
        },
        "title": [
            {
                "type": "text",
                "text": {
                    "content": title
                }
            }
        ],
        "properties": properties,
        "cover": {
            "type": "external",
            "external": {
                "url": image_url
            }
        } if image_url else {}
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


def create_paragraph(parent_id, text_blocks):
    paragraph_block = notion.blocks.children.append(**{
        "block_id": parent_id,
        "children": [
            {
                "object": "block",
                "type": "paragraph",
                "paragraph": {
                    "rich_text": process_rich_text_content(text_blocks)
                }
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


def create_column_list(parent_id, num_columns=2):
    column_list_block = notion.blocks.children.append(**{
        "block_id": parent_id,
        "children": [
            {
                "object": "block",
                "type": "column_list",
                "column_list": {
                    "children": [
                        {
                            "object": "block",
                            "type": "column",
                            "column": {
                                "children": [
                                    {
                                        "object": "block",
                                        "type": "paragraph",
                                        "paragraph": {
                                            "rich_text": [
                                                {
                                                    "type": "text",
                                                    "text": {
                                                        "content": "placeholder",
                                                    }
                                                }
                                            ]
                                        }
                                    }
                                ]
                            }
                        } for _ in range(num_columns)
                    ]
                }
            }
        ]
    })

    return column_list_block


def create_callout(parent_id, text_blocks, icon, color="default"):
    callout_block = notion.blocks.children.append(**{
        "block_id": parent_id,
        "children": [
            {
                "object": "block",
                "type": "callout",
                "callout": {
                    "rich_text": process_rich_text_content(text_blocks),
                    "icon": {
                        "type": "emoji",
                        "emoji": icon
                    },
                    "color": color
                }
            }
        ]
    })
    return callout_block


def create_quote(parent_id, text_blocks):
    quote_block = notion.blocks.children.append(**{
        "block_id": parent_id,
        "children": [
            {
                "object": "block",
                "type": "quote",
                "quote": {
                    "rich_text": process_rich_text_content(text_blocks)
                }
            }
        ]
    })
    return quote_block
