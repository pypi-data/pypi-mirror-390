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
        print("Please provide the cursus id as an argument.")
        sys.exit(2)

    cursus_id: int
    try:
        cursus_id = int(sys.argv[1])
    except ValueError:
        print("Invalid cursus id provided.")
        sys.exit(2)

    try:
        cursus = client.cursuses.get_by_id(cursus_id)
        print(json.dumps(cursus, default=default_serializer, indent=4))
    except FortyTwoNotFoundException:
        print("Cursus not found.")
        sys.exit(1)


if __name__ == "__main__":
    main()
