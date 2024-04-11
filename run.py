import argparse
import json
import os

from blueprints.architect import process_blueprint


def load_blueprint(filename):
    with open(filename, "r") as file:
        return json.load(file)


def main():
    parser = argparse.ArgumentParser(description="Process a JSON blueprint to create content in Notion.")
    parser.add_argument("json_file", help="Location of the JSON blueprint file")
    args = parser.parse_args()

    notion_page_id = os.environ["NOTION_PAGE_ID"]

    blueprint = load_blueprint(args.json_file)
    process_blueprint(notion_page_id, blueprint)


if __name__ == "__main__":
    main()
