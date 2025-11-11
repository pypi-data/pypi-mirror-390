import json
import os
import sys

from dotenv import load_dotenv

from fortytwo import Client, logger, parameter
from fortytwo.json import default_serializer


def main() -> None:
    logger.enable_debug_logging()
    load_dotenv(".env")

    client = Client(
        client_id=os.environ.get("42_SCHOOL_ID"),
        client_secret=os.environ.get("42_SCHOOL_SECRET"),
    )

    if len(sys.argv) != 2:
        print("Please provide the user login as an argument.")
        sys.exit(2)

    user_login = sys.argv[1]
    users = client.users.get_all(
        # Use the filter by login parameter to fetch user by login
        parameter.UserParameters.Filter.by_login(user_login)
    )

    if not users:
        print("User not found.")
        sys.exit(1)

    cursus_users = client.cursus_users.get_by_user_id(
        users[0].id,
        page_size=1,
    )
    if not cursus_users:
        print("No cursus_users found for this user.")

    print(json.dumps(cursus_users, default=default_serializer, indent=4))


if __name__ == "__main__":
    main()
