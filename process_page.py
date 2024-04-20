import argparse
import json

from blueprints.utils import process_page


def pretty_print_blueprint(page_id):
    blueprint_json = process_page(page_id)
    print(json.dumps(blueprint_json, indent=4))


def main():
    parser = argparse.ArgumentParser(description="Process and print a Notion page as a JSON blueprint.")
    parser.add_argument("page_id", help="The Notion page ID to process")
    args = parser.parse_args()

    pretty_print_blueprint(args.page_id)


if __name__ == "__main__":
    main()
