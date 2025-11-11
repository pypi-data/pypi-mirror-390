import json
import os
import sys

from dotenv import load_dotenv

from fortytwo import Client, logger
from fortytwo.exceptions.exceptions import FortyTwoNotFoundException
from fortytwo.json import default_serializer


def main() -> None:
    logger.enable_debug_logging()
    load_dotenv(".env")

    client = Client(
        client_id=os.environ.get("42_SCHOOL_ID"),
        client_secret=os.environ.get("42_SCHOOL_SECRET"),
    )

    if len(sys.argv) != 2:
        print("Please provide the project id as an argument.")
        sys.exit(2)

    project_id: int
    try:
        project_id = int(sys.argv[1])
    except ValueError:
        print("Invalid project id provided.")
        sys.exit(2)

    try:
        project = client.projects.get_by_id(project_id)
        print(json.dumps(project, default=default_serializer, indent=4))
    except FortyTwoNotFoundException:
        print("Project not found.")
        sys.exit(1)


if __name__ == "__main__":
    main()
