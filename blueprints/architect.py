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
MODEL_NAME = os.environ["NOTION_GPT_MODEL_NAME"]

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
        is_inline = block_json.get("is_inline", False)
        create_database(parent_id, title, icon, schema, is_inline=is_inline, cover_image=True)

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
        model=MODEL_NAME,
        response_format={"type": "json_object"},
        messages=[
            {
                "role": "system",
                "content": "You are NotionGPT, a state-of-the-art template designer for Notion, programmed to create custom JSON blueprints that represent detailed, organized, and highly functional Notion templates. Your templates should be ready for users to use immediately and should meet their specific organizational needs, allowing users to customize them to suit their needs.\n\nYour response must be formatted as a valid JSON object with the following structure:\n{\n    \"response\": \"Description of the Notion page based on the user's request.\"\n    \"blueprint\": \"Structured JSON blueprint of the Notion page layout according to the provided schema.\"\n}\n\n\"blueprint\" should be a JSON object representing the Notion page you want to create, defined as per the following schema:\n\n```\n{\"$schema\":\"http://json-schema.org/draft-07/schema#\",\"definitions\":{\"page\":{\"type\":\"object\",\"properties\":{\"type\":{\"type\":\"string\",\"enum\":[\"page\"]},\"title\":{\"type\":\"string\"},\"children\":{\"type\":\"array\",\"items\":{\"oneOf\":[{\"$ref\":\"#/definitions/page\"},{\"$ref\":\"#/definitions/database\"},{\"$ref\":\"#/definitions/divider\"},{\"$ref\":\"#/definitions/table_of_contents\"},{\"$ref\":\"#/definitions/heading\"},{\"$ref\":\"#/definitions/paragraph\"},{\"$ref\":\"#/definitions/list\"},{\"$ref\":\"#/definitions/to_do_list\"},{\"$ref\":\"#/definitions/toggle\"},{\"$ref\":\"#/definitions/column_list\"},{\"$ref\":\"#/definitions/callout\"},{\"$ref\":\"#/definitions/quote\"}]}}},\"required\":[\"type\",\"title\",\"children\"],\"additionalProperties\":false},\"database\":{\"type\":\"object\",\"properties\":{\"type\":{\"type\":\"string\",\"enum\":[\"database\"]},\"title\":{\"type\":\"string\"},\"icon\":{\"type\":\"string\"},\"is_inline\":{\"type\":\"boolean\",\"default\":false},\"schema\":{\"type\":\"object\",\"patternProperties\":{\".*\":{\"type\":\"object\",\"properties\":{\"type\":{\"type\":\"string\",\"enum\":[\"checkbox\",\"created_by\",\"created_time\",\"date\",\"email\",\"files\",\"last_edited_by\",\"last_edited_time\",\"multi_select\",\"number\",\"people\",\"phone_number\",\"rich_text\",\"select\",\"title\",\"url\"]},\"format\":{\"type\":\"string\",\"enum\":[\"argentinepeso\",\"baht\",\"australiandollar\",\"canadiandollar\",\"chileanpeso\",\"colombianpeso\",\"danishkrone\",\"dirham\",\"dollar\",\"euro\",\"forint\",\"franc\",\"hongkongdollar\",\"koruna\",\"krona\",\"leu\",\"lira\",\"mexicanpeso\",\"newtaiwandollar\",\"newzealanddollar\",\"norwegiankrone\",\"number\",\"numberwithcommas\",\"percent\",\"philippinepeso\",\"pound\",\"peruviansol\",\"rand\",\"real\",\"ringgit\",\"riyal\",\"ruble\",\"rupee\",\"rupiah\",\"shekel\",\"singaporedollar\",\"uruguayanpeso\",\"yen\",\"yuan\",\"won\",\"zloty\"]},\"options\":{\"type\":\"array\",\"items\":{\"type\":\"object\",\"properties\":{\"name\":{\"type\":\"string\"},\"color\":{\"type\":\"string\",\"enum\":[\"blue\",\"brown\",\"default\",\"gray\",\"green\",\"orange\",\"pink\",\"purple\",\"red\",\"yellow\"]}},\"required\":[\"name\",\"color\"]}}},\"dependencies\":{\"format\":{\"properties\":{\"type\":{\"const\":\"number\"}}},\"options\":{\"properties\":{\"type\":{\"enum\":[\"select\",\"multi_select\"]}}}},\"additionalProperties\":false}},\"additionalProperties\":false,\"minProperties\":1}},\"required\":[\"type\",\"title\",\"icon\",\"schema\"],\"additionalProperties\":false},\"divider\":{\"type\":\"object\",\"properties\":{\"type\":{\"type\":\"string\",\"enum\":[\"divider\"]}},\"required\":[\"type\"],\"additionalProperties\":false},\"table_of_contents\":{\"type\":\"object\",\"properties\":{\"type\":{\"type\":\"string\",\"enum\":[\"table_of_contents\"]}},\"required\":[\"type\"],\"additionalProperties\":false},\"heading\":{\"type\":\"object\",\"properties\":{\"type\":{\"type\":\"string\",\"enum\":[\"heading_1\",\"heading_2\",\"heading_3\"]},\"text\":{\"type\":\"string\"}},\"required\":[\"type\",\"text\"],\"additionalProperties\":false},\"paragraph\":{\"type\":\"object\",\"properties\":{\"type\":{\"type\":\"string\",\"enum\":[\"paragraph\"]},\"content\":{\"type\":\"array\",\"items\":{\"type\":\"object\",\"properties\":{\"text\":{\"type\":\"string\"},\"style\":{\"type\":\"array\",\"items\":{\"type\":\"string\",\"enum\":[\"bold\",\"italic\",\"strikethrough\",\"underline\",\"code\"]},\"default\":[]}},\"required\":[\"text\",\"style\"],\"additionalProperties\":false}}},\"required\":[\"type\",\"content\"],\"additionalProperties\":false},\"list\":{\"type\":\"object\",\"properties\":{\"type\":{\"type\":\"string\",\"enum\":[\"bulleted_list\",\"numbered_list\"]},\"items\":{\"type\":\"array\",\"items\":{\"type\":\"string\"}}},\"required\":[\"type\",\"items\"],\"additionalProperties\":false},\"to_do_list\":{\"type\":\"object\",\"properties\":{\"type\":{\"type\":\"string\",\"enum\":[\"to_do_list\"]},\"items\":{\"type\":\"array\",\"items\":{\"type\":\"object\",\"properties\":{\"text\":{\"type\":\"string\"},\"checked\":{\"type\":\"boolean\"}},\"required\":[\"text\",\"checked\"],\"additionalProperties\":false}}},\"required\":[\"type\",\"items\"],\"additionalProperties\":false},\"toggle\":{\"type\":\"object\",\"properties\":{\"type\":{\"type\":\"string\",\"enum\":[\"toggle\"]},\"text\":{\"type\":\"string\"},\"children\":{\"type\":\"array\",\"items\":{\"oneOf\":[{\"$ref\":\"#/definitions/divider\"},{\"$ref\":\"#/definitions/table_of_contents\"},{\"$ref\":\"#/definitions/heading\"},{\"$ref\":\"#/definitions/paragraph\"},{\"$ref\":\"#/definitions/list\"},{\"$ref\":\"#/definitions/to_do_list\"},{\"$ref\":\"#/definitions/toggle\"},{\"$ref\":\"#/definitions/column_list\"},{\"$ref\":\"#/definitions/callout\"},{\"$ref\":\"#/definitions/quote\"}]}}},\"required\":[\"type\",\"text\",\"children\"],\"additionalProperties\":false},\"column_list\":{\"type\":\"object\",\"properties\":{\"type\":{\"type\":\"string\",\"enum\":[\"column_list\"]},\"columns\":{\"type\":\"array\",\"items\":{\"type\":\"object\",\"properties\":{\"type\":{\"type\":\"string\",\"enum\":[\"column\"]},\"children\":{\"type\":\"array\",\"items\":{\"oneOf\":[{\"$ref\":\"#/definitions/divider\"},{\"$ref\":\"#/definitions/table_of_contents\"},{\"$ref\":\"#/definitions/heading\"},{\"$ref\":\"#/definitions/paragraph\"},{\"$ref\":\"#/definitions/list\"},{\"$ref\":\"#/definitions/to_do_list\"},{\"$ref\":\"#/definitions/toggle\"},{\"$ref\":\"#/definitions/callout\"},{\"$ref\":\"#/definitions/quote\"}]}}},\"required\":[\"type\",\"children\"],\"additionalProperties\":false}}},\"required\":[\"type\",\"columns\"],\"additionalProperties\":false},\"callout\":{\"type\":\"object\",\"properties\":{\"type\":{\"type\":\"string\",\"enum\":[\"callout\"]},\"icon\":{\"type\":\"string\"},\"color\":{\"type\":\"string\",\"enum\":[\"blue_background\",\"brown_background\",\"default\",\"gray_background\",\"green_background\",\"orange_background\",\"pink_background\",\"purple_background\",\"red_background\",\"yellow_background\"]},\"content\":{\"type\":\"array\",\"items\":{\"type\":\"object\",\"properties\":{\"text\":{\"type\":\"string\"},\"style\":{\"type\":\"array\",\"items\":{\"type\":\"string\",\"enum\":[\"bold\",\"italic\",\"strikethrough\",\"underline\",\"code\"]},\"default\":[]}},\"required\":[\"text\",\"style\"],\"additionalProperties\":false}}},\"required\":[\"type\",\"icon\",\"color\",\"content\"],\"additionalProperties\":false},\"quote\":{\"type\":\"object\",\"properties\":{\"type\":{\"type\":\"string\",\"enum\":[\"quote\"]},\"content\":{\"type\":\"array\",\"items\":{\"type\":\"object\",\"properties\":{\"text\":{\"type\":\"string\"},\"style\":{\"type\":\"array\",\"items\":{\"type\":\"string\",\"enum\":[\"bold\",\"italic\",\"strikethrough\",\"underline\",\"code\"]},\"default\":[]}},\"required\":[\"text\",\"style\"],\"additionalProperties\":false}}},\"required\":[\"type\",\"content\"],\"additionalProperties\":false}}}\n```\n\nAdditionally, when creating databases, note that there must be exactly one property in the \"schema\" object with the type \"title\", which will always be a rich text field. For example:\n\n\"Name\": {\n    \"type\": \"title\"\n}"
            },
            {
                "role": "user",
                "content": "I'm the CEO of Acme Inc., a company dedicated to helping people plan and organize, and I want a system to manage my marketing campaign. I want to store key documents, plan our strategy, handle deliverables and track performance."
            },
            {
                "role": "assistant",
                "content": "{\"response\":\"Alright, I will set up a comprehensive Notion page titled \\\"Campaign Brief\\\" for Acme Inc. to manage your upcoming marketing campaign. Here's a sneak peek of what you can expect:\\n\\n1. Overview: A brief summary of the campaign's objectives to get others up to speed, with an example to get you started.\\n2. Documents: A hub with linked essential documents like the product roadmap, weekly updates, performance reports, budget plans, and more.\\n3. Strategy: Details on campaign goals, target audience, and channel strategy to aid in strategic planning.\\n4. Execution: A section to track deliverables and monitor key campaign performance metrics effectively.\\n\\nThis organized structure will help you manage key documents, strategize effectively, track progress, and analyze campaign performance for a successful marketing push. Now, I’ll create this exact structure in Notion.\",\"blueprint\":{\"type\":\"page\",\"title\":\"Campaign Brief\",\"icon\":\"📋\",\"children\":[{\"type\":\"heading_1\",\"text\":\"Overview\"},{\"type\":\"callout\",\"icon\":\"➡️\",\"color\":\"purple_background\",\"content\":[{\"text\":\"Provide a summary of the campaign. At a glance, others should be able to quickly get up to speed on the project’s “what” and “why”, as well as the “why now”.\",\"style\":[]}],\"children\":[{\"type\":\"paragraph\",\"content\":[{\"text\":\"Example:\",\"style\":[\"bold\"]},{\"text\":\" In Q4, Acme Inc. will launch an awareness campaign for personal users across key global markets to drive new site visits and account creation. The campaign will focus on highlighting the customizability of Acme and how it can be used for planning, organizing, and managing one's life. The primary objectives of the campaign are to increase brand awareness and drive traffic to the site. The campaign will showcase Acme's organization and goal-setting features, including databases, to-do lists, and calendars, as well as its sharing and collaboration capabilities.\",\"style\":[]}]}]},{\"type\":\"paragraph\",\"content\":[]},{\"type\":\"toggle\",\"title\":\"Table of Contents\",\"children\":[{\"type\":\"table_of_contents\"}]},{\"type\":\"heading_1\",\"text\":\"📘 Documents\"},{\"type\":\"divider\"},{\"type\":\"paragraph\",\"content\":[{\"text\":\"Link to all key documents that are relevant for this campaign.\",\"style\":[]}]},{\"type\":\"page\",\"title\":\"Documents Hub\",\"icon\":\"📘\",\"children\":[{\"type\":\"database\",\"title\":\"Product roadmap\",\"icon\":\"🎯\",\"schema\":{\"Project\":{\"type\":\"title\"},\"Assign\":{\"type\":\"people\"},\"Date\":{\"type\":\"date\"},\"Status\":{\"type\":\"select\",\"options\":[{\"name\":\"Not started\",\"color\":\"red\"},{\"name\":\"In progress\",\"color\":\"yellow\"},{\"name\":\"Completed\",\"color\":\"green\"}]}}},{\"type\":\"database\",\"title\":\"Weekly product update\",\"icon\":\"📄\",\"schema\":{\"Name\":{\"type\":\"title\"},\"Author\":{\"type\":\"people\"}}},{\"type\":\"page\",\"title\":\"Performance report\",\"icon\":\"📈\",\"children\":[{\"type\":\"callout\",\"icon\":\"💡\",\"color\":\"gray_background\",\"content\":[{\"text\":\"Tip:\",\"style\":[\"bold\"]},{\"text\":\" Add more details right in this page, including toggles, images, and more. Break up the page by using different header options so that it’s easier to read.\",\"style\":[]}]}]},{\"type\":\"page\",\"title\":\"Budget plan\",\"icon\":\"💸\",\"children\":[{\"type\":\"callout\",\"icon\":\"💡\",\"color\":\"gray_background\",\"content\":[{\"text\":\"Tip:\",\"style\":[\"bold\"]},{\"text\":\" Add more details right in this page, including toggles, images, and more. Break up the page by using different header options so that it’s easier to read.\",\"style\":[]}]}]},{\"type\":\"page\",\"title\":\"Editorial calendar\",\"icon\":\"📅\",\"children\":[{\"type\":\"callout\",\"icon\":\"💡\",\"color\":\"gray_background\",\"content\":[{\"text\":\"Overview:\",\"style\":[\"bold\"]},{\"text\":\" Add more details right in this page, including toggles, images, and more. Break up the page by using different header options so that it’s easier to read.\",\"style\":[]}]}]},{\"type\":\"page\",\"title\":\"Content strategy\",\"icon\":\"📝\",\"children\":[{\"type\":\"callout\",\"icon\":\"💡\",\"color\":\"gray_background\",\"content\":[{\"text\":\"Tip:\",\"style\":[\"bold\"]},{\"text\":\" Add more details right in this page, including toggles, images, and more. Break up the page by using different header options so that it’s easier to read.\",\"style\":[]}]}]}]},{\"type\":\"heading_1\",\"text\":\"🧭 Strategy\"},{\"type\":\"divider\"},{\"type\":\"heading_2\",\"text\":\"Goals & objectives\"},{\"type\":\"paragraph\",\"content\":[{\"text\":\"Use this section to list all campaign goals and objectives. \",\"style\":[]}]},{\"type\":\"paragraph\",\"content\":[{\"text\":\"Campaign objectives:\",\"style\":[\"bold\"]}]},{\"type\":\"numbered_list\",\"items\":[\"Increasing awareness of brand\",\"Driving traffic to site\"]},{\"type\":\"paragraph\",\"content\":[{\"text\":\"Product goals:\",\"style\":[\"bold\"]}]},{\"type\":\"numbered_list\",\"items\":[\"Showcase organization and goal-setting in Acme with databases, to-do lists, calendars, and other productivity features\",\"Highlight sharing and collaborating with friends and family\"]},{\"type\":\"paragraph\",\"content\":[{\"text\":\"Company goals:\",\"style\":[\"bold\"]}]},{\"type\":\"numbered_list\",\"items\":[\"Show Acme’s product flexibility\",\"Increase overall signups \"]},{\"type\":\"heading_2\",\"text\":\"Target audience(s)\"},{\"type\":\"paragraph\",\"content\":[{\"text\":\"Provide a summary of your target audience(s) in as much detail as possible. The more defined your audience is, the more targeted your campaign will be. The toggle below includes a few additional questions to ask when narrowing in on your target audience.\",\"style\":[]}]},{\"type\":\"toggle\",\"title\":\"Additional audience insights:\",\"children\":[{\"type\":\"bulleted_list\",\"items\":[\"What do they think and how do they behave?\",\"What problem or challenge are we trying to solve for them?\",\"What makes their experience with Acme unique?\",\"Why are they not doing what we want them to?\",\"What challenges of theirs can Acme help solve?\",\"What channels does this audience or community interact with most?\",\"What unique behaviors do we want to focus on as part of our marketing effort?\"]}]},{\"type\":\"paragraph\",\"content\":[{\"text\":\"The target audience will include personal users across various demographics and regions, with a focus on those who are seeking a more efficient and customizable productivity tool. \",\"style\":[]}]},{\"type\":\"bulleted_list\",\"items\":[\"Prospects that don’t use Acme for Personal or Teams → Try Acme!\",\"Personal users that don’t use Acme at work → Plan personal and work goals with Acme!\"]},{\"type\":\"heading_1\",\"text\":\"📨 Channel strategy\"},{\"type\":\"divider\"},{\"type\":\"heading_2\",\"text\":\"Overview\"},{\"type\":\"paragraph\",\"content\":[{\"text\":\"Use this section to summarize at a glance the major campaign moments and deliverables.\",\"style\":[]},{\"text\":\" \",\"style\":[]}]},{\"type\":\"bulleted_list\",\"items\":[\"Identify potential partners for cross-promotion, such as productivity and lifestyle influencers\",\"Create social media content that highlights Acme's customization and collaboration features, targeting personal users who are seeking a more efficient productivity tool\",\"Utilize email marketing to drive traffic to the site and showcase Acme's organization and goal-setting features, including databases, to-do lists, and calendars\",\"Host webinars and workshops to educate new users on how to use Acme for personal productivity and organization\",\"Use targeted ads on social media platforms and search engines to reach potential users who are searching for productivity tools\",\"Develop partnerships with relevant organizations or companies to offer Acme as a productivity tool for their employees or members\"]},{\"type\":\"heading_1\",\"text\":\"🚀 Execution\"},{\"type\":\"divider\"},{\"type\":\"heading_2\",\"text\":\"Deliverables tracker\"},{\"type\":\"paragraph\",\"content\":[{\"text\":\"Use this section to track any actions or deliverables needed to launch the campaign. Use the “Channel” column to link deliverables to the relevant channel.\",\"style\":[]}]},{\"type\":\"database\",\"title\":\"Deliverables tracker\",\"icon\":\"🕒\",\"is_inline\":true,\"schema\":{\"Deliverable\":{\"type\":\"title\"},\"Status\":{\"type\":\"select\",\"options\":[{\"name\":\"Not started\",\"color\":\"red\"},{\"name\":\"In progress\",\"color\":\"yellow\"},{\"name\":\"Design in progress\",\"color\":\"yellow\"},{\"name\":\"Design finished\",\"color\":\"orange\"},{\"name\":\"Sent to vendor\",\"color\":\"blue\"},{\"name\":\"Ordered\",\"color\":\"blue\"},{\"name\":\"Shipped\",\"color\":\"blue\"},{\"name\":\"Received\",\"color\":\"green\"},{\"name\":\"Complete\",\"color\":\"green\"}]},\"Assignee\":{\"type\":\"people\"},\"Contributors\":{\"type\":\"people\"},\"Due\":{\"type\":\"date\"},\"Channel\":{\"type\":\"select\",\"options\":[{\"name\":\"Community\",\"color\":\"purple\"},{\"name\":\"Social Media\",\"color\":\"green\"},{\"name\":\"Content\",\"color\":\"pink\"},{\"name\":\"Events\",\"color\":\"brown\"},{\"name\":\"Communications\",\"color\":\"gray\"},{\"name\":\"Performance\",\"color\":\"yellow\"},{\"name\":\"Product Marketing\",\"color\":\"default\"},{\"name\":\"Demand Gen\",\"color\":\"orange\"}]}}},{\"type\":\"heading_1\",\"text\":\"📈 Campaign performance\"},{\"type\":\"divider\"},{\"type\":\"paragraph\",\"content\":[{\"text\":\"Add post-campaign performance reports and metrics here.\",\"style\":[]}]},{\"type\":\"callout\",\"icon\":\"✨\",\"color\":\"default\",\"content\":[{\"text\":\"Overall goal:\",\"style\":[\"bold\"]}]},{\"type\":\"callout\",\"icon\":\"✍️\",\"color\":\"gray_background\",\"content\":[{\"text\":\"Executive Summary\",\"style\":[\"bold\"]}]},{\"type\":\"heading_2\",\"text\":\"Conversions\"},{\"type\":\"divider\"},{\"type\":\"heading_2\",\"text\":\"Impressions\"},{\"type\":\"divider\"},{\"type\":\"heading_2\",\"text\":\"Web traffic\"},{\"type\":\"divider\"},{\"type\":\"heading_2\",\"text\":\"Email\"},{\"type\":\"divider\"},{\"type\":\"heading_2\",\"text\":\"Social & Influencers\"},{\"type\":\"divider\"},{\"type\":\"heading_2\",\"text\":\"Internal Team Retro\"},{\"type\":\"divider\"}]}}"
            },
            {
                "role": "user",
                "content": "I run a CS club and want a centralized dashboard where I can list events, store a repository of resources, and have a news section. Oh, and a place for club photos would also be nice, just so it looks more aesthetic."
            },
            {
                "role": "assistant",
                "content": "{\"response\":\"Certainly! I'll make a centralized Notion dashboard for your club titled \\\"Computer Science Club Home.\\\" This page will serve as a central hub where you can manage and showcase various aspects of your club. It will also include sections for upcoming events, a repository of resources, the latest news, and a gallery for club photos to enhance the aesthetic appeal.\\n\\nWe’ll start with the welcome message in a callout box at the top, that will invite new and prospective members with an application link and a brief introduction to the club’s purpose. Then, we’ll follow up with your news section, which will be set up to feature updates and announcements that can be chronologically organized for ease of use. Additionally, events will be detailed on their individual pages linked from a main events section, ensuring that members know what, when, and where activities are happening.\\n\\nFor resources, there will be individual pages under one umbrella, each containing valuable materials ranging from internship opportunities to tech talks and software deals. This will be an invaluable asset for both new and existing members. Lastly, the photo gallery will serve as a vibrant collage of recent activities and memorable moments from the club, encouraging a sense of community and belonging! Now, I’ll go ahead and create your computer science club dashboard in Notion.\",\"blueprint\":{\"type\":\"page\",\"title\":\"Computer science club home\",\"icon\":\"🤖\",\"children\":[{\"type\":\"callout\",\"icon\":\"💡\",\"color\":\"gray_background\",\"content\":[{\"text\":\"Template Overview: \",\"style\":[\"bold\"]},{\"text\":\"Use this template if you’re running a club at school and need a homepage to showcase your events, news, resources, and more! This template is specifically designed for Computer Science or Engineering-themed clubs, but you can adapt it for any group that runs programming and events.\",\"style\":[]}]},{\"type\":\"column_list\",\"columns\":[{\"type\":\"column\",\"children\":[{\"type\":\"callout\",\"icon\":\"💾\",\"color\":\"blue_background\",\"content\":[{\"text\":\"Hello world!\",\"style\":[\"code\"]},{\"text\":\" Welcome to our computer science club homepage. Want to join? Fill this form out:\",\"style\":[]},{\"text\":\"…attach link here\",\"style\":[\"italic\"]},{\"text\":\"Scroll down to learn more about our club and check out some useful resources. Check out recent news, upcoming events, club photos, and more! \",\"style\":[]}]}]},{\"type\":\"column\",\"children\":[{\"type\":\"quote\",\"content\":[{\"text\":\"Table of contents\",\"style\":[\"bold\"]}],\"children\":[{\"type\":\"table_of_contents\"}]}]}]},{\"type\":\"heading_1\",\"text\":\"News\"},{\"type\":\"database\",\"title\":\"News\",\"icon\":\"📰\",\"is_inline\":true,\"schema\":{\"Name\":{\"type\":\"title\"},\"Date\":{\"type\":\"date\"}}},{\"type\":\"heading_1\",\"text\":\"Events\"},{\"type\":\"page\",\"title\":\"Code party  —  September 2, 2022 7:00 PM (EDT)\",\"icon\":\"🎉\",\"children\":[{\"type\":\"heading_2\",\"text\":\"What?\"},{\"type\":\"paragraph\",\"content\":[{\"text\":\"We’re hosting a code party for anyone and everyone! Use the time to work on your CS homework, a side project, or just hang out with the crew 😎\",\"style\":[]}]},{\"type\":\"paragraph\",\"content\":[{\"text\":\"We’ll also have some snacks available free of charge! Come one, come all!\",\"style\":[]}]},{\"type\":\"heading_2\",\"text\":\"When?\"},{\"type\":\"paragraph\",\"content\":[{\"text\":\"September 2, 2022 7:00 PM (EDT)\",\"style\":[]}]},{\"type\":\"heading_2\",\"text\":\"Where?\"},{\"type\":\"paragraph\",\"content\":[{\"text\":\"MN Building — Room 112\",\"style\":[]}]},{\"type\":\"heading_2\",\"text\":\"Who?\"},{\"type\":\"paragraph\",\"content\":[{\"text\":\"Anyone and everyone!\",\"style\":[]}]},{\"type\":\"paragraph\",\"content\":[]}]},{\"type\":\"page\",\"title\":\"Capture the flag  —  September 7, 2022 7:00 PM (EDT)\",\"icon\":\"🏴‍☠️\",\"children\":[{\"type\":\"callout\",\"icon\":\"💡\",\"color\":\"gray_background\",\"content\":[{\"text\":\"Template Tip: \",\"style\":[\"bold\"]},{\"text\":\"Use this space below to provide more details about this event. You can also add the event schedule, embed a form, or even videos of past events.\",\"style\":[]}]}]},{\"type\":\"page\",\"title\":\"Python 101  —  September 9, 2022 7:00 PM (EDT)\",\"icon\":\"🐍\",\"children\":[{\"type\":\"callout\",\"icon\":\"💡\",\"color\":\"gray_background\",\"content\":[{\"text\":\"Template Tip: \",\"style\":[\"bold\"]},{\"text\":\"Use this space below to provide more details about this event. You can also add the event schedule, embed a form, or even videos of past events.\",\"style\":[]}]}]},{\"type\":\"heading_1\",\"text\":\"Resources\"},{\"type\":\"page\",\"title\":\"Internships 2022\",\"icon\":\"🏢\",\"children\":[{\"type\":\"callout\",\"icon\":\"💡\",\"color\":\"gray_background\",\"content\":[{\"text\":\"Template Tip:\",\"style\":[\"bold\"]},{\"text\":\" Add more details right in this page, including toggles, images, and more. Break up the page by using our different header options so that it’s easier to read.\",\"style\":[]}]}]},{\"type\":\"page\",\"title\":\"Our services\",\"icon\":\"⚙️\",\"children\":[{\"type\":\"callout\",\"icon\":\"💡\",\"color\":\"gray_background\",\"content\":[{\"text\":\"Template Tip:\",\"style\":[\"bold\"]},{\"text\":\" Add more details right in this page, including toggles, images, and more. Break up the page by using our different header options so that it’s easier to read.\",\"style\":[]}]}]},{\"type\":\"page\",\"title\":\"Tech talks\",\"icon\":\"🎤\",\"children\":[{\"type\":\"callout\",\"icon\":\"💡\",\"color\":\"gray_background\",\"content\":[{\"text\":\"Template Tip:\",\"style\":[\"bold\"]},{\"text\":\" Add more details right in this page, including toggles, images, and more. Break up the page by using our different header options so that it’s easier to read.\",\"style\":[]}]}]},{\"type\":\"page\",\"title\":\"Meet the team\",\"icon\":\"👥\",\"children\":[{\"type\":\"callout\",\"icon\":\"💡\",\"color\":\"gray_background\",\"content\":[{\"text\":\"Template Tip:\",\"style\":[\"bold\"]},{\"text\":\" Add more details right in this page, including toggles, images, and more. Break up the page by using our different header options so that it’s easier to read.\",\"style\":[]}]}]},{\"type\":\"page\",\"title\":\"Software deals\",\"icon\":\"💿\",\"children\":[{\"type\":\"callout\",\"icon\":\"💡\",\"color\":\"gray_background\",\"content\":[{\"text\":\"Template Tip:\",\"style\":[\"bold\"]},{\"text\":\" Add more details right in this page, including toggles, images, and more. Break up the page by using our different header options so that it’s easier to read.\",\"style\":[]}]}]},{\"type\":\"page\",\"title\":\"First year guide\",\"icon\":\"🎒\",\"children\":[{\"type\":\"callout\",\"icon\":\"💡\",\"color\":\"gray_background\",\"content\":[{\"text\":\"Template Tip:\",\"style\":[\"bold\"]},{\"text\":\" Add more details right in this page, including toggles, images, and more. Break up the page by using our different header options so that it’s easier to read.\",\"style\":[]}]}]},{\"type\":\"heading_1\",\"text\":\"Photos\"},{\"type\":\"quote\",\"content\":[{\"text\":\"This is where you add photos of recent club meetups or events, be bold!\",\"style\":[]}]}]}}"
            },
            {
                "role": "user",
                "content": description
            }
        ],
        temperature=0.7,
        max_tokens=4096,
        top_p=0.1,
        frequency_penalty=0,
        presence_penalty=0,
        stream=True
    )

    in_response = False
    accumulated_json = ""
    response_buffer = ""
    partial_newline = False

    for chunk in response:
        text = chunk.choices[0].delta.content

        if text is None:
            text = ""

        accumulated_json += text

        if partial_newline:
            if text.startswith("n"):
                response_buffer += "\n"
                text = text[1:]
            partial_newline = False

        if text.endswith("\\"):
            partial_newline = True
            text = text[:-1]

        text = text.replace("\\n", "\n")

        if not in_response:
            response_start_index = accumulated_json[-20 - len(text):].find('"response":"')
            if response_start_index != -1:
                in_response = True
                start_index = len(accumulated_json) - (20 + len(text)) + response_start_index + len('"response":"')
            else:
                start_index = 0
        else:
            start_index = 0

        if in_response:
            response_buffer += text[start_index:]

            end_index = response_buffer.find('",')
            if end_index != -1:
                yield response_buffer[:end_index]
                in_response = False
                response_buffer = ""
            else:
                yield response_buffer[start_index:]
                response_buffer = ""

    content = json.loads(accumulated_json)
    yield content
