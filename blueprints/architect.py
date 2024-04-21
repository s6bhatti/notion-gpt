import json
import os
import random

import emoji
from notion_client import Client
from openai import OpenAI

from .blocks import (create_page, create_database, create_divider, create_table_of_contents, create_heading,
                     create_paragraph, create_list, create_todo_list, create_toggle, create_column_list, create_callout,
                     create_quote)

NOTION_KEY = os.environ["NOTION_KEY"]

notion = Client(auth=NOTION_KEY)
client = OpenAI()


def process_blueprint(parent_id, block_json):
    block_type = block_json["type"]

    if block_type == "page":
        title = block_json.get("title", "Untitled Page")
        emojis = [em for em in emoji.EMOJI_DATA if not any(char in em for char in ["🏻", "🏼", "🏽", "🏾", "🏿", "\u200d"]) and not em.startswith(("🇦", "🇧", "🇨", "🇩", "🇪", "🇫", "🇬", "🇭", "🇮", "🇯", "🇰", "🇱", "🇲", "🇳", "🇴", "🇵", "🇶", "🇷", "🇸", "🇹", "🇺", "🇻", "🇼", "🇽", "🇾", "🇿"))]
        icon = block_json.get("icon", random.choice(emojis))
        page_id = create_page(parent_id, title, icon, cover_image=True)["id"]
        for child in block_json.get("children", []):
            process_blueprint(page_id, child)

    elif block_type == "database":
        title = block_json.get("title", "Untitled Database")
        emojis = [em for em in emoji.EMOJI_DATA if not any(char in em for char in ["🏻", "🏼", "🏽", "🏾", "🏿", "\u200d"]) and not em.startswith(("🇦", "🇧", "🇨", "🇩", "🇪", "🇫", "🇬", "🇭", "🇮", "🇯", "🇰", "🇱", "🇲", "🇳", "🇴", "🇵", "🇶", "🇷", "🇸", "🇹", "🇺", "🇻", "🇼", "🇽", "🇾", "🇿"))]
        icon = block_json.get("icon", random.choice(emojis))
        schema = block_json.get("schema", {})
        create_database(parent_id, title, icon, schema, cover_image=True)

    elif block_type == "divider":
        create_divider(parent_id)

    elif block_type == "table_of_contents":
        create_table_of_contents(parent_id)

    elif block_type.startswith("heading_"):
        text = block_json.get("text", "")
        level = int(block_type.split("_")[1])
        create_heading(parent_id, text, level)

    elif block_type == "paragraph":
        text_blocks = block_json.get("content", [])
        create_paragraph(parent_id, text_blocks)

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

    elif block_type == "column_list":
        num_columns = len(block_json.get("columns", []))
        column_ids = create_column_list(parent_id, num_columns)

        for i, column in enumerate(block_json.get("columns", [])):
            for child in column.get("children", []):
                process_blueprint(column_ids[i], child)

    elif block_type == "callout":
        text_blocks = block_json.get("content", [])
        icon = block_json.get("icon", "💡")
        color = block_json.get("color", "default")
        callout_id = create_callout(parent_id, text_blocks, icon, color)["results"][0]["id"]
        for child in block_json.get("children", []):
            process_blueprint(callout_id, child)

    elif block_type == "quote":
        text_blocks = block_json.get("content", [])
        quote_id = create_quote(parent_id, text_blocks)["results"][0]["id"]
        for child in block_json.get("children", []):
            process_blueprint(quote_id, child)

def generate_blueprint(description):
    response = client.chat.completions.create(
        model="gpt-4-turbo",
        response_format={"type": "json_object"},
        messages=[
            {
                "role": "system",
                "content": "You are a state-of-the-art template designer for Notion, equipped to create custom JSON structures that represent detailed, aesthetic, and highly functional Notion templates. Your templates should be ready for users to use immediately and should meet their specific organizational needs, with template content to get them started. Your designs should include elements like databases, to-do lists, schedules, and note-taking sections, and should follow the bespoke JSON format provided in the examples. Ensure that the templates are not only functional but also visually appealing and well-organized. You are allowed to use the following Notion blocks, and need to follow the documentation exactly for the output JSON to be valid:\n\n\"\"\"\nType: Page\nStructure:\n{\n    \"type\": \"page\",\n    \"title\": \"New Page\", \n    \"children\": []\n}\n\nType: Database\nStructure:\n{\n    \"type\": \"database\", \n    \"title\": \"New Database\",\n    \"schema\": { // Supports \"title\", \"rich_text\", \"number\", \"checkbox\", \"date\", \"people\", \"files\", \"url\", \"email\", \"phone_number\", \"select\", and \"multi_select\"\n        \"Name\": {\"type\": \"title\"},\n        \"Status\": {\n            \"type\": \"select\",\n            \"options\": [\"Option 1\", \"Option 2\", \"Option 3\"]\n        }\n    }\n}\n\nType: Divider\nStructure:\n{\n    \"type\": \"divider\"\n}\n\nType: Headings\nStructure:\n{\n    \"type\": \"heading_1\",  // Supports headings 1-3\n    \"text\": \"Heading Level 1\"\n}\n\nType: Paragraph\nStructure:\n{\n    \"type\": \"paragraph\", \n    \"text\": \"This is a paragraph.\"\n}\n\nType: List\nStructure:\n{\n    \"type\": \"bulleted_list\", // bulleted_list or numbered_list\n    \"items\": [\"Item 1\", \"Item 2\"]\n}\n\nType: Todo List\nStructure:\n{\n  \"type\": \"to_do_list\",\n  \"items\": [\n    {\"text\": \"Task 1\", \"checked\": false},\n    {\"text\": \"Task 2\", \"checked\": true},\n    {\"text\": \"Task 3\", \"checked\": false}\n  ]\n}\n\nType: Toggle\nStructure:\n{\n    \"type\": \"toggle\", \n    \"text\": \"Toggle Title\", \n    \"children\": []\n}\n\nType: Callout\nStructure:\n{\n    \"type\": \"callout\",\n    \"text\": \"This is a callout.\",\n    \"icon\": \"📢\", \n    \"color\": \"yellow_background\"\n}\n\nType: Quote\nStructure:\n{\n    \"type\": \"quote\", \n    \"text\": \"This is a quote.\"\n}\n\"\"\""
            },
            {
                "role": "user",
                "content": "A health and fitness dashboard that lets me plan out my groceries, meals, and track my workouts."
            },
            {
                "role": "assistant",
                "content": "{\n  \"type\": \"page\",\n  \"title\": \"Health and Fitness Dashboard\",\n  \"children\": [\n    {\n      \"type\": \"callout\",\n      \"text\": \"With this Health and Fitness Dashboard template, you can plan out your groceries, meals and workouts in a centralized place.\",\n      \"icon\": \"💡\",\n      \"color\": \"yellow_background\"\n    },\n    {\n      \"type\": \"heading_1\",\n      \"text\": \"Weekly Grocery Planning\"\n    },\n    {\n      \"type\": \"database\",\n      \"title\": \"Weekly Grocery Planning\",\n      \"schema\": {\n        \"Name\": {\n          \"type\": \"title\"\n        },\n        \"Description\": {\n          \"type\": \"rich_text\"\n        },\n        \"In stock\": {\n          \"type\": \"checkbox\"\n        },\n        \"Food group\": {\n          \"type\": \"select\",\n          \"options\": [\n            {\n              \"name\": \"🥦Vegetable\",\n              \"color\": \"green\"\n            },\n            {\n              \"name\": \"🍎Fruit\",\n              \"color\": \"red\"\n            },\n            {\n              \"name\": \"💪Protein\",\n              \"color\": \"yellow\"\n            }\n          ]\n        },\n        \"Price\": {\n          \"type\": \"number\",\n          \"format\": \"dollar\"\n        },\n        \"Last ordered\": {\n          \"type\": \"date\"\n        },\n        \"Store availability\": {\n          \"type\": \"multi_select\",\n          \"options\": [\n            {\n              \"name\": \"Duc Loi Market\",\n              \"color\": \"blue\"\n            },\n            {\n              \"name\": \"Rainbow Grocery\",\n              \"color\": \"gray\"\n            },\n            {\n              \"name\": \"Nijiya Market\",\n              \"color\": \"purple\"\n            },\n            {\n              \"name\": \"Gus's Community Market\",\n              \"color\": \"yellow\"\n            }\n          ]\n        },\n        \"+1\": {\n          \"type\": \"people\"\n        },\n        \"Photo\": {\n          \"type\": \"files\"\n        }\n      }\n    },\n    {\n      \"type\": \"heading_1\",\n      \"text\": \"Meal Planner\"\n    },\n    {\n      \"type\": \"database\",\n      \"title\": \"Meal Planner\",\n      \"schema\": {\n        \"Recipe Name\": {\n          \"type\": \"title\"\n        },\n        \"Ingredients\": {\n          \"type\": \"rich_text\"\n        },\n        \"Preparation Time\": {\n          \"type\": \"number\",\n          \"format\": \"minutes\"\n        },\n        \"Calories\": {\n          \"type\": \"number\",\n          \"format\": \"number\"\n        },\n        \"Dietary Restrictions\": {\n          \"type\": \"multi_select\",\n          \"options\": [\n            {\n              \"name\": \"Vegetarian\",\n              \"color\": \"green\"\n            },\n            {\n              \"name\": \"Vegan\",\n              \"color\": \"red\"\n            },\n            {\n              \"name\": \"Gluten-Free\",\n              \"color\": \"orange\"\n            },\n            {\n              \"name\": \"Keto\",\n              \"color\": \"blue\"\n            }\n          ]\n        },\n        \"Instructions\": {\n          \"type\": \"rich_text\"\n        },\n        \"Nutritional Info\": {\n          \"type\": \"rich_text\"\n        },\n        \"Rating\": {\n          \"type\": \"select\",\n          \"options\": [\n            {\n              \"name\": \"⭐\",\n              \"color\": \"yellow\"\n            },\n            {\n              \"name\": \"⭐⭐\",\n              \"color\": \"yellow\"\n            },\n            {\n              \"name\": \"⭐⭐⭐\",\n              \"color\": \"yellow\"\n            },\n            {\n              \"name\": \"⭐⭐⭐⭐\",\n              \"color\": \"yellow\"\n            },\n            {\n              \"name\": \"⭐⭐⭐⭐⭐\",\n              \"color\": \"yellow\"\n            }\n          ]\n        },\n        \"Photo\": {\n          \"type\": \"files\"\n        }\n      }\n    },\n    {\n      \"type\": \"heading_1\",\n      \"text\": \"Workout Tracker\"\n    },\n    {\n      \"type\": \"page\",\n      \"title\": \"Workouts\",\n      \"children\": [\n        {\n          \"type\": \"toggle\",\n          \"title\": \"Workout History\",\n          \"children\": [\n            {\n              \"type\": \"toggle\",\n              \"title\": \"January 1st - Leg Day\",\n              \"children\": [\n                {\n                  \"type\": \"to_do_list\",\n                  \"items\": [\n                    {\n                      \"text\": \"Warm-up: 10 minutes on the stationary bike\",\n                      \"checked\": false\n                    },\n                    {\n                      \"text\": \"Squats: 4 sets of 10 reps\",\n                      \"checked\": false\n                    },\n                    {\n                      \"text\": \"Leg Press: 3 sets of 12 reps\",\n                      \"checked\": false\n                    },\n                    {\n                      \"text\": \"Lunges with Dumbbells: 3 sets of 15 reps per leg\",\n                      \"checked\": false\n                    },\n                    {\n                      \"text\": \"Leg Curls: 3 sets of 12 reps\",\n                      \"checked\": false\n                    },\n                    {\n                      \"text\": \"Calf Raises: 4 sets of 15 reps\",\n                      \"checked\": false\n                    }\n                  ]\n                }\n              ]\n            }\n          ]\n        }\n      ]\n    }\n  ]\n}"
            },
            {
                "role": "assistant",
                "content": "A school hub where I can manage my class schedule, upcoming assignments, and take notes."
            },
            {
                "role": "assistant",
                "content": "{\n  \"type\": \"page\",\n  \"title\": \"School Hub\",\n  \"children\": [\n    {\n      \"type\": \"heading_1\",\n      \"text\": \"Planning\"\n    },\n    {\n      \"type\": \"heading_2\",\n      \"text\": \"Classes\"\n    },\n    {\n      \"type\": \"page\",\n      \"title\": \"Class Schedule\",\n      \"children\": [\n        {\n          \"type\": \"heading_1\",\n          \"text\": \"Schedule\"\n        },\n        {\n          \"type\": \"bulleted_list\",\n          \"items\": [\n            \"English 101 - Monday & Wednesday, 9:00 AM - 10:30 AM - Building A, Room 204\",\n            \"World History II - Tuesday & Thursday, 10:45 AM - 12:15 PM - Building C, Room 101\",\n            \"Calculus I - Monday & Wednesday, 1:00 PM - 2:30 PM - Building B, Room 310\",\n            \"General Biology - Tuesday & Thursday, 2:45 PM - 4:15 PM - Science Center, Room 450\"\n          ]\n        }\n      ]\n    },\n    {\n      \"type\": \"heading_2\",\n      \"text\": \"Assignments\"\n    },\n    {\n      \"type\": \"database\",\n      \"title\": \"Assignment Tracker\",\n      \"schema\": {\n        \"Title\": {\n          \"type\": \"title\"\n        },\n        \"Due Date\": {\n          \"type\": \"date\"\n        },\n        \"Course\": {\n          \"type\": \"rich_text\"\n        },\n        \"Status\": {\n          \"type\": \"select\",\n          \"options\": [\n            {\n              \"name\": \"Not Started\",\n              \"color\": \"red\"\n            },\n            {\n              \"name\": \"In Progress\",\n              \"color\": \"yellow\"\n            },\n            {\n              \"name\": \"Completed\",\n              \"color\": \"green\"\n            }\n          ]\n        },\n        \"Details\": {\n          \"type\": \"rich_text\"\n        },\n        \"Priority\": {\n          \"type\": \"select\",\n          \"options\": [\n            {\n              \"name\": \"High\",\n              \"color\": \"red\"\n            },\n            {\n              \"name\": \"Medium\",\n              \"color\": \"yellow\"\n            },\n            {\n              \"name\": \"Low\",\n              \"color\": \"green\"\n            }\n          ]\n        }\n      }\n    },\n    {\n      \"type\": \"heading_1\",\n      \"text\": \"Coursework\"\n    },\n    {\n      \"type\": \"heading_2\",\n      \"text\": \"Notes\"\n    },\n    {\n      \"type\": \"page\",\n      \"title\": \"English Notes\",\n      \"children\": [\n        {\n          \"type\": \"callout\",\n          \"text\": \"Your English notes will go here...\",\n          \"icon\": \"✍️\"\n        },\n        {\n          \"type\": \"toggle\",\n          \"title\": \"Lecture Notes\",\n          \"children\": [\n            {\n              \"type\": \"paragraph\",\n              \"text\": \"Add your notes here...\"\n            }\n          ]\n        },\n        {\n          \"type\": \"toggle\",\n          \"title\": \"Readings\",\n          \"children\": [\n            {\n              \"type\": \"bulleted_list\",\n              \"items\": [\n                \"Hamlet, Act 1-3\"\n              ]\n            }\n          ]\n        }\n      ]\n    },\n    {\n      \"type\": \"page\",\n      \"title\": \"History Notes\",\n      \"children\": [\n        {\n          \"type\": \"callout\",\n          \"text\": \"Your History notes will go here...\",\n          \"icon\": \"🌎\"\n        },\n        {\n          \"type\": \"toggle\",\n          \"title\": \"Lecture Notes\",\n          \"children\": [\n            {\n              \"type\": \"paragraph\",\n              \"text\": \"Add your notes here...\"\n            }\n          ]\n        },\n        {\n          \"type\": \"toggle\",\n          \"title\": \"Readings\",\n          \"children\": [\n            {\n              \"type\": \"bulleted_list\",\n              \"items\": [\n                \"The Rise and Fall of the Great Powers\"\n              ]\n            }\n          ]\n        }\n      ]\n    }\n  ]\n}"
            },
            {
                "role": "user",
                "content": "A project management dashboard where I can track my team's project timelines, tasks, current bugs, and write out our engineering documentation."
            },
            {
                "role": "assistant",
                "content": "{\n  \"type\": \"page\",\n  \"title\": \"Project Management Dashboard\",\n  \"children\": [\n    {\n      \"type\": \"heading_1\",\n      \"text\": \"Project Timelines\"\n    },\n    {\n      \"type\": \"database\",\n      \"title\": \"Project Timeline Tracker\",\n      \"schema\": {\n        \"Project Name\": {\n          \"type\": \"title\"\n        },\n        \"Start Date\": {\n          \"type\": \"date\"\n        },\n        \"End Date\": {\n          \"type\": \"date\"\n        },\n        \"Team\":{\n          \"type\": \"select\",\n          \"options\": [\n            {\n              \"name\": \"Engineering\",\n              \"color\": \"blue\"\n            },\n            {\n              \"name\": \"Sales\",\n              \"color\": \"orange\"\n            },\n            {\n              \"name\": \"Marketing\",\n              \"color\": \"green\"\n            }\n          ]\n        },\n        \"Status\": {\n          \"type\": \"select\",\n          \"options\": [\n            {\n              \"name\": \"Planning\",\n              \"color\": \"blue\"\n            },\n            {\n              \"name\": \"In Progress\",\n              \"color\": \"yellow\"\n            },\n            {\n              \"name\": \"Completed\",\n              \"color\": \"green\"\n            }\n          ]\n        },\n        \"Details\": {\n          \"type\": \"rich_text\"\n        },\n        \"Progress\": {\n          \"type\": \"number\",\n          \"format\": \"percent\"\n        }\n      }\n    },\n    {\n      \"type\": \"heading_1\",\n      \"text\": \"Task Management\"\n    },\n    {\n      \"type\": \"database\",\n      \"title\": \"Task Tracker\",\n      \"schema\": {\n        \"Task\": {\n          \"type\": \"title\"\n        },\n        \"Assigned To\": {\n          \"type\": \"people\"\n        },\n        \"Due Date\": {\n          \"type\": \"date\"\n        },\n        \"Status\": {\n          \"type\": \"select\",\n          \"options\": [\n            {\n              \"name\": \"Not Started\",\n              \"color\": \"red\"\n            },\n            {\n              \"name\": \"In Progress\",\n              \"color\": \"yellow\"\n            },\n            {\n              \"name\": \"Completed\",\n              \"color\": \"green\"\n            }\n          ]\n        },\n        \"Priority\": {\n          \"type\": \"select\",\n          \"options\": [\n            {\n              \"name\": \"High\",\n              \"color\": \"red\"\n            },\n            {\n              \"name\": \"Medium\",\n              \"color\": \"yellow\"\n            },\n            {\n              \"name\": \"Low\",\n              \"color\": \"green\"\n            }\n          ]\n        }\n      }\n    },\n    {\n      \"type\": \"heading_1\",\n      \"text\": \"Bug Tracker\"\n    },\n    {\n      \"type\": \"database\",\n      \"title\": \"Bug Tracker\",\n      \"schema\": {\n        \"Bug Name\": {\n          \"type\": \"title\"\n        },\n        \"Bud Description\": {\n          \"type\": \"rich_text\"\n        },\n        \"Severity\": {\n          \"type\": \"select\",\n          \"options\": [\n            {\n              \"name\": \"Critical\",\n              \"color\": \"red\"\n            },\n            {\n              \"name\": \"Major\",\n              \"color\": \"orange\"\n            },\n            {\n              \"name\": \"Minor\",\n              \"color\": \"yellow\"\n            },\n            {\n              \"name\": \"Trivial\",\n              \"color\": \"green\"\n            }\n          ]\n        },\n        \"Status\": {\n          \"type\": \"select\",\n          \"options\": [\n            {\n              \"name\": \"Open\",\n              \"color\": \"red\"\n            },\n            {\n              \"name\": \"In Review\",\n              \"color\": \"yellow\"\n            },\n            {\n              \"name\": \"Resolved\",\n              \"color\": \"green\"\n            }\n          ]\n        },\n        \"Assigned To\": {\n          \"type\": \"people\"\n        }\n      }\n    },\n    {\n      \"type\": \"heading_1\",\n      \"text\": \"Engineering Documentation\"\n    },\n    {\n      \"type\": \"page\",\n      \"title\": \"Docs\",\n      \"children\": [\n        {\n          \"type\": \"heading_1\",\n          \"text\": \"Engineering Documentation Overview\"\n        },\n        {\n          \"type\": \"quote\",\n          \"text\": \"Documentation is a love letter that you write to your future self. — Damian Conway\"\n        },\n        {\n          \"type\": \"divider\"\n        },\n        {\n          \"type\": \"heading_2\",\n          \"text\": \"Frontend Documentation\"\n        },\n        {\n          \"type\": \"page\",\n          \"title\": \"Frontend\",\n          \"children\": [\n            {\n              \"type\": \"paragraph\",\n              \"text\": \"This section contains all relevant documentation for frontend development.\"\n            },\n            {\n              \"type\": \"bulleted_list\",\n              \"items\": [\n                \"React Component Guidelines\",\n                \"State Management Best Practices\",\n                \"Accessibility Checklist\"\n              ]\n            },\n            {\n              \"type\": \"quote\",\n              \"text\": \"The best performance improvement is the transition from the nonworking state to the working state. — J. Osterhout\"\n            }\n          ]\n        },\n        {\n          \"type\": \"divider\"\n        },\n        {\n          \"type\": \"heading_2\",\n          \"text\": \"Backend Documentation\"\n        },\n        {\n          \"type\": \"page\",\n          \"title\": \"Backend\",\n          \"children\": [\n            {\n              \"type\": \"paragraph\",\n              \"text\": \"This section covers the documentation for backend development, including APIs, databases, and server management.\"\n            },\n            {\n              \"type\": \"bulleted_list\",\n              \"items\": [\n                \"REST API Design Guidelines\",\n                \"Database Migration Strategies\",\n                \"Server Security Checklist\"\n              ]\n            },\n            {\n              \"type\": \"quote\",\n              \"text\": \"In theory, there is no difference between theory and practice. But, in practice, there is. — Jan L.A. van de Snepscheut\"\n            }\n          ]\n        }\n      ]\n    }\n  ]\n}"
            },
            {
                "role": "user",
                "content": description
            }
        ],
        temperature=1,
        max_tokens=4095,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0
    )
    return json.loads(response.choices[0].message.content)
