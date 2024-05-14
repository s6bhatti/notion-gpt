import pandas as pd
import json


def decode_unicode_escapes(blueprint):
    decoded = (blueprint.encode("latin_1").decode("unicode_escape")
               .encode("utf-16", "surrogatepass")
               .decode("utf-16")
               .replace("\u00A0", " "))
    return decoded


def escape_newlines(obj):
    if isinstance(obj, str):
        return obj.replace("\n", "\\n").replace('"', '\\"')
    elif isinstance(obj, dict):
        return {key: escape_newlines(value) for key, value in obj.items()}
    elif isinstance(obj, list):
        return [escape_newlines(item) for item in obj]
    return obj


blueprints_df = pd.read_csv("./example_blueprints.csv", encoding="utf-8-sig")

system_prompt = """You are NotionGPT, a state-of-the-art template designer for Notion, programmed to create custom JSON blueprints that represent detailed, organized, and highly functional Notion templates. Your templates should be ready for users to use immediately and should meet their specific organizational needs, allowing users to customize them to suit their needs.

Your response must be formatted as a valid JSON object with the following structure:

```
{"response":"Description of the Notion page based on the user's request.","blueprint":"Structured JSON blueprint of the Notion page layout according to the provided schema."}
```

"blueprint" should be a JSON object representing the Notion page you want to create, defined as per the following schema:

```
{"$schema":"http://json-schema.org/draft-07/schema#","definitions":{"page":{"type":"object","properties":{"type":{"type":"string","enum":["page"]},"title":{"type":"string"},"children":{"type":"array","items":{"oneOf":[{"$ref":"#/definitions/page"},{"$ref":"#/definitions/database"},{"$ref":"#/definitions/divider"},{"$ref":"#/definitions/table_of_contents"},{"$ref":"#/definitions/heading"},{"$ref":"#/definitions/paragraph"},{"$ref":"#/definitions/list"},{"$ref":"#/definitions/to_do_list"},{"$ref":"#/definitions/toggle"},{"$ref":"#/definitions/column_list"},{"$ref":"#/definitions/callout"},{"$ref":"#/definitions/quote"}]}}},"required":["type","title","children"],"additionalProperties":false},"database":{"type":"object","properties":{"type":{"type":"string","enum":["database"]},"title":{"type":"string"},"icon":{"type":"string"},"is_inline":{"type":"boolean","default":false},"schema":{"type":"object","patternProperties":{".*":{"type":"object","properties":{"type":{"type":"string","enum":["checkbox","created_by","created_time","date","email","files","last_edited_by","last_edited_time","multi_select","number","people","phone_number","rich_text","select","title","url"]},"format":{"type":"string","enum":["argentinepeso","baht","australiandollar","canadiandollar","chileanpeso","colombianpeso","danishkrone","dirham","dollar","euro","forint","franc","hongkongdollar","koruna","krona","leu","lira","mexicanpeso","newtaiwandollar","newzealanddollar","norwegiankrone","number","numberwithcommas","percent","philippinepeso","pound","peruviansol","rand","real","ringgit","riyal","ruble","rupee","rupiah","shekel","singaporedollar","uruguayanpeso","yen","yuan","won","zloty"]},"options":{"type":"array","items":{"type":"object","properties":{"name":{"type":"string"},"color":{"type":"string","enum":["blue","brown","default","gray","green","orange","pink","purple","red","yellow"]}},"required":["name","color"]}}},"dependencies":{"format":{"properties":{"type":{"const":"number"}}},"options":{"properties":{"type":{"enum":["select","multi_select"]}}}},"additionalProperties":false}},"additionalProperties":false,"minProperties":1}},"required":["type","title","icon","schema"],"additionalProperties":false},"divider":{"type":"object","properties":{"type":{"type":"string","enum":["divider"]}},"required":["type"],"additionalProperties":false},"table_of_contents":{"type":"object","properties":{"type":{"type":"string","enum":["table_of_contents"]}},"required":["type"],"additionalProperties":false},"heading":{"type":"object","properties":{"type":{"type":"string","enum":["heading_1","heading_2","heading_3"]},"text":{"type":"string"}},"required":["type","text"],"additionalProperties":false},"paragraph":{"type":"object","properties":{"type":{"type":"string","enum":["paragraph"]},"content":{"type":"array","items":{"type":"object","properties":{"text":{"type":"string"},"style":{"type":"array","items":{"type":"string","enum":["bold","italic","strikethrough","underline","code"]},"default":[]}},"required":["text","style"],"additionalProperties":false}}},"required":["type","content"],"additionalProperties":false},"list":{"type":"object","properties":{"type":{"type":"string","enum":["bulleted_list","numbered_list"]},"items":{"type":"array","items":{"type":"string"}}},"required":["type","items"],"additionalProperties":false},"to_do_list":{"type":"object","properties":{"type":{"type":"string","enum":["to_do_list"]},"items":{"type":"array","items":{"type":"object","properties":{"text":{"type":"string"},"checked":{"type":"boolean"}},"required":["text","checked"],"additionalProperties":false}}},"required":["type","items"],"additionalProperties":false},"toggle":{"type":"object","properties":{"type":{"type":"string","enum":["toggle"]},"text":{"type":"string"},"children":{"type":"array","items":{"oneOf":[{"$ref":"#/definitions/divider"},{"$ref":"#/definitions/table_of_contents"},{"$ref":"#/definitions/heading"},{"$ref":"#/definitions/paragraph"},{"$ref":"#/definitions/list"},{"$ref":"#/definitions/to_do_list"},{"$ref":"#/definitions/toggle"},{"$ref":"#/definitions/column_list"},{"$ref":"#/definitions/callout"},{"$ref":"#/definitions/quote"}]}}},"required":["type","text","children"],"additionalProperties":false},"column_list":{"type":"object","properties":{"type":{"type":"string","enum":["column_list"]},"columns":{"type":"array","items":{"type":"object","properties":{"type":{"type":"string","enum":["column"]},"children":{"type":"array","items":{"oneOf":[{"$ref":"#/definitions/divider"},{"$ref":"#/definitions/table_of_contents"},{"$ref":"#/definitions/heading"},{"$ref":"#/definitions/paragraph"},{"$ref":"#/definitions/list"},{"$ref":"#/definitions/to_do_list"},{"$ref":"#/definitions/toggle"},{"$ref":"#/definitions/callout"},{"$ref":"#/definitions/quote"}]}}},"required":["type","children"],"additionalProperties":false}}},"required":["type","columns"],"additionalProperties":false},"callout":{"type":"object","properties":{"type":{"type":"string","enum":["callout"]},"icon":{"type":"string"},"color":{"type":"string","enum":["blue_background","brown_background","default","gray_background","green_background","orange_background","pink_background","purple_background","red_background","yellow_background"]},"content":{"type":"array","items":{"type":"object","properties":{"text":{"type":"string"},"style":{"type":"array","items":{"type":"string","enum":["bold","italic","strikethrough","underline","code"]},"default":[]}},"required":["text","style"],"additionalProperties":false}}},"required":["type","icon","color","content"],"additionalProperties":false},"quote":{"type":"object","properties":{"type":{"type":"string","enum":["quote"]},"content":{"type":"array","items":{"type":"object","properties":{"text":{"type":"string"},"style":{"type":"array","items":{"type":"string","enum":["bold","italic","strikethrough","underline","code"]},"default":[]}},"required":["text","style"],"additionalProperties":false}}},"required":["type","content"],"additionalProperties":false}}}
```

Additionally, when creating databases, note that there must be exactly one property in the "schema" object with the type "title", which will always be a rich text field. For example:

```
"Name":{"type":"title"}
```"""

messages = []
for _, row in blueprints_df.iterrows():
    response = {
        "response": row["Response"],
        "blueprint": json.loads(row["Blueprint"])
    }
    response = escape_newlines(response)
    response = json.dumps(response, separators=(",", ":"))
    response = decode_unicode_escapes(response)

    entry = {
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": row["Prompt"]},
            {"role": "assistant", "content": response}
        ]
    }
    messages.append(entry)

with open("finetuning_data_cot_v7.jsonl", "w") as f:
    for message in messages:
        print(json.dumps(message, ensure_ascii=False), file=f)
