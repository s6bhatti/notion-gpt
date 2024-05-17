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

Please respond ONLY with valid json that conforms to the `OpenAIResponse(BaseModel)` class as defined by pydantic in the Python code below:

```
from __future__ import annotations

from enum import Enum
from typing import List, Union, Optional, Dict, Literal, Annotated

from pydantic import BaseModel, Field, RootModel, model_validator


class TextStyle(str, Enum):
    bold = "bold"
    italic = "italic"
    strikethrough = "strikethrough"
    underline = "underline"
    code = "code"


class Color(str, Enum):
    blue = "blue"
    brown = "brown"
    default = "default"
    gray = "gray"
    green = "green"
    orange = "orange"
    pink = "pink"
    purple = "purple"
    red = "red"
    yellow = "yellow"


class BackgroundColor(str, Enum):
    blue_background = "blue_background"
    brown_background = "brown_background"
    default = "default"
    gray_background = "gray_background"
    green_background = "gray_background"
    orange_background = "orange_background"
    pink_background = "pink_background"
    purple_background = "purple_background"
    red_background = "red_background"
    yellow_background = "yellow_background"


class NumberFormat(str, Enum):
    argentinepeso = "argentinepeso"
    baht = "baht"
    australiandollar = "australiandollar"
    canadiandollar = "canadiandollar"
    chileanpeso = "chileanpeso"
    colombianpeso = "colombianpeso"
    danishkrone = "danishkrone"
    dirham = "dirham"
    dollar = "dollar"
    euro = "euro"
    forint = "forint"
    franc = "franc"
    hongkongdollar = "hongkongdollar"
    koruna = "koruna"
    krona = "krona"
    leu = "leu"
    lira = "lira"
    mexicanpeso = "mexicanpeso"
    newtaiwandollar = "newtaiwandollar"
    newzealanddollar = "newzealanddollar"
    norwegiankrone = "norwegiankrone"
    number = "number"
    numberwithcommas = "numberwithcommas"
    percent = "percent"
    philippinepeso = "philippinepeso"
    pound = "pound"
    peruviansol = "peruviansol"
    rand = "rand"
    real = "real"
    ringgit = "ringgit"
    riyal = "riyal"
    ruble = "ruble"
    rupee = "rupee"
    rupiah = "rupiah"
    shekel = "shekel"
    singaporedollar = "singaporedollar"
    uruguayanpeso = "uruguayanpeso"
    yen = "yen"
    yuan = "yuan"
    won = "won"
    zloty = "zloty"


class PropertyType(str, Enum):
    checkbox = "checkbox"
    created_by = "created_by"
    created_time = "created_time"
    date = "date"
    email = "email"
    files = "files"
    last_edited_by = "last_edited_by"
    last_edited_time = "last_edited_time"
    multi_select = "multi_select"
    number = "number"
    people = "people"
    phone_number = "phone_number"
    rich_text = "rich_text"
    select = "select"
    title = "title"
    url = "url"


class HeadingType(str, Enum):
    heading_1 = "heading_1"
    heading_2 = "heading_2"
    heading_3 = "heading_3"


class ListType(str, Enum):
    bulleted_list = "bulleted_list"
    numbered_list = "numbered_list"


class SchemaOption(BaseModel):
    name: str
    color: Color


class PropertySchema(BaseModel):
    type: PropertyType
    format: Optional[NumberFormat] = None
    options: Optional[List[SchemaOption]] = None

    @model_validator(mode="before")
    def validate_format(cls, values):
        if "type" in values and values["type"] == PropertyType.number and not values.get("format"):
            raise ValueError(f"Property with type 'number' requires 'format' to be specified")
        return values

    @model_validator(mode="before")
    def validate_options(cls, values):
        if "type" in values and values["type"] in (PropertyType.select, PropertyType.multi_select) and not values.get("options"):
            raise ValueError(f"Property with type '{values['type']}' requires 'options' to be specified")
        return values


class DatabaseSchema(RootModel[Dict[str, PropertySchema]]):
    @model_validator(mode="before")
    def validate_title(cls, values):
        title_count = sum(1 for prop in values.values() if isinstance(prop, dict) and prop.get("type") == PropertyType.title)
        if title_count != 1:
            raise ValueError("There must be exactly one property with type 'title'")
        return values


class RichTextContent(BaseModel):
    text: str
    style: List[TextStyle] = []


class Divider(BaseModel):
    type: Literal["divider"]


class TableOfContents(BaseModel):
    type: Literal["table_of_contents"]


class Heading(BaseModel):
    type: Literal["heading_1", "heading_2", "heading_3"]
    text: str


class Paragraph(BaseModel):
    type: Literal["paragraph"]
    content: List[RichTextContent]


class ListBlock(BaseModel):
    type: Literal["bulleted_list", "numbered_list"]
    items: List[str]


class ToDoListItem(BaseModel):
    text: str
    checked: bool


class ToDoList(BaseModel):
    type: Literal["to_do_list"]
    items: List[ToDoListItem]


class Toggle(BaseModel):
    type: Literal["toggle"]
    text: str
    children: List[Union[Divider, TableOfContents, Heading, Paragraph, ListBlock, ToDoList, Toggle, ColumnList, Callout, Quote]]


class Column(BaseModel):
    type: Literal["column"]
    children: List[Union[Divider, TableOfContents, Heading, Paragraph, ListBlock, ToDoList, Toggle, Callout, Quote]]


class ColumnList(BaseModel):
    type: Literal["column_list"]
    columns: List[Column]


class Callout(BaseModel):
    type: Literal["callout"]
    icon: str
    color: BackgroundColor
    content: List[RichTextContent]
    children: Optional[List[Union[Divider, TableOfContents, Heading, Paragraph, ListBlock, ToDoList, Toggle, Callout, Quote]]] = None


class Quote(BaseModel):
    type: Literal["quote"]
    content: List[RichTextContent]
    children: Optional[List[Union[Divider, TableOfContents, Heading, Paragraph, ListBlock, ToDoList, Toggle, Callout, Quote]]] = None


class Database(BaseModel):
    type: Literal["database"]
    title: str
    icon: str
    is_inline: Optional[bool] = False
    schema: DatabaseSchema


class Page(BaseModel):
    type: Literal["page"]
    title: str

    children: List[Annotated[Union[Divider, TableOfContents, Heading, Paragraph, ListBlock, ToDoList, Toggle, ColumnList, Callout, Quote, Database, Page], Field(discriminator="type")]]


class OpenAIResponse(BaseModel):
    response: str
    blueprint: Page


Page.update_forward_refs()
Toggle.update_forward_refs()
Column.update_forward_refs()
ColumnList.update_forward_refs()
Callout.update_forward_refs()
Quote.update_forward_refs()
```

Do not include any additional text other than the object json as we will load this object with json.loads() and pydantic. Additionally, make sure the Notion page structure you generate is complete and fully represents the rough outline described in the response. DO NOT JUST GENERATE A SINGULAR CALLOUT BOX IN A PAGE AS YORU BLUEPRINT. THIS IS VERY IMPORTANT."""

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

with open("finetuning_data_cot_v10.jsonl", "w") as f:
    for message in messages:
        print(json.dumps(message, ensure_ascii=False), file=f)
