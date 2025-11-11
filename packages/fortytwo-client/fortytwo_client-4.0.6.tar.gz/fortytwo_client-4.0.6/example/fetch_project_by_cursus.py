import json
import os
import sys

from dotenv import load_dotenv

from fortytwo import Client, logger
from fortytwo.json import default_serializer


def main() -> None:
    logger.enable_debug_logging()
    load_dotenv(".env")

    client = Client(
        client_id=os.environ.get("42_SCHOOL_ID"),
        client_secret=os.environ.get("42_SCHOOL_SECRET"),
    )

    if len(sys.argv) != 2:
        print("Please provide the cursus id as an argument.")
        sys.exit(2)

    cursus_id: int
    try:
        cursus_id = int(sys.argv[1])
    except ValueError:
        print("Invalid cursus id provided.")
        sys.exit(2)

    # Fetch projects using pagination
    projects = []
    for i in range(1, 10):
        print(f"Fetching page {i}...")

        page_projects = client.projects.get_by_cursus_id(
            cursus_id,
            page=i,
            page_size=1,
        )

        if not page_projects:
            break

        projects.extend(page_projects)

    for project in projects:
        print(json.dumps(project, default=default_serializer, indent=4))


if __name__ == "__main__":
    main()
