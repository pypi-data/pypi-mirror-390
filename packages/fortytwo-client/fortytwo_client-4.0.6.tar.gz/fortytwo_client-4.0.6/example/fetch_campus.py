import json
import os
import sys

from dotenv import load_dotenv

from fortytwo import Client, logger
from fortytwo.exceptions.exceptions import FortyTwoNotFoundException
from fortytwo.json import default_serializer


def main() -> None:
    # Enable debug logging using the new convenience function
    logger.enable_debug_logging()
    load_dotenv(".env")

    client = Client(
        client_id=os.environ.get("42_SCHOOL_ID"),
        client_secret=os.environ.get("42_SCHOOL_SECRET"),
    )

    if len(sys.argv) != 2:
        print("Please provide the campus id as an argument.")
        sys.exit(2)

    campus_id: int
    try:
        campus_id = int(sys.argv[1])
    except ValueError:
        print("Invalid campus id provided.")
        sys.exit(2)

    try:
        campus = client.campuses.get_by_id(campus_id)
        print(json.dumps(campus, default=default_serializer, indent=4))
    except FortyTwoNotFoundException:
        print("Campus not found.")
        sys.exit(1)


if __name__ == "__main__":
    main()
