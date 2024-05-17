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

    @model_validator(mode='after')
    def validate_children(cls, values):
        if len(values.blueprint.children) <= 1:
            raise ValueError("The root Page (blueprint) must have more than one child.")
        return values


Page.update_forward_refs()
Toggle.update_forward_refs()
Column.update_forward_refs()
ColumnList.update_forward_refs()
Callout.update_forward_refs()
Quote.update_forward_refs()
