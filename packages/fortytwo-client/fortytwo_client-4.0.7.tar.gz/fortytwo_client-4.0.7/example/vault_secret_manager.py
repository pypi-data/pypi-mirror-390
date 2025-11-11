import json
import os
import sys
from collections.abc import Generator
from contextlib import contextmanager

import hvac
from dotenv import load_dotenv
from testcontainers.vault import VaultContainer

from fortytwo import Client, logger, parameter
from fortytwo.json import default_serializer


@contextmanager
def vault_container() -> Generator[hvac.Client, None, None]:
    """
    Context manager for managing a Vault test container.

    Yields:
        Vault client connected to the test container
    """
    print("Starting Vault container...")

    with VaultContainer("hashicorp/vault:1.16.1") as vault_container:
        connection_url = vault_container.get_connection_url()

        vault_client = hvac.Client(
            url=connection_url,
            token=vault_container.root_token,
        )

        print(f"Vault container ready at {connection_url}")
        yield vault_client


def main() -> None:
    logger.enable_debug_logging()

    with vault_container() as vault_client:
        load_dotenv(".env")

        client_id = os.environ.get("42_SCHOOL_ID")
        client_secret = os.environ.get("42_SCHOOL_SECRET")

        vault_client.secrets.kv.v2.create_or_update_secret(
            path="fortytwo",
            secret={
                "client_id": client_id,
                "client_secret": client_secret,
            },
            mount_point="secret",
        )

        client = Client(
            config=Client.Config(
                secret_manager=Client.SecretManager.Vault(
                    vault_client,
                    path="fortytwo",
                    mount_point="secret",
                ),
            ),
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

        project = client.projects.get_by_cursus_id(
            cursus_id,
            parameter.PageSize(1),
        )

        if project is None:
            print("Project not found.")
            sys.exit(1)

        print(json.dumps(project, default=default_serializer, indent=4))


if __name__ == "__main__":
    main()
