import argparse
import os

from blueprints.architect import process_blueprint, generate_blueprint


def main():
    parser = argparse.ArgumentParser(description="Generates Notion content given a brief description")
    parser.add_argument("description", help="Text description of the desired content in Notion.")
    args = parser.parse_args()

    notion_page_id = os.environ["NOTION_PAGE_ID"]

    content = generate_blueprint(args.description)
    # response = content["response"]
    blueprint = content["blueprint"]

    # print(response)

    process_blueprint(notion_page_id, blueprint)


if __name__ == "__main__":
    main()
