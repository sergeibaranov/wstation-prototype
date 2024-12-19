import asyncio

import datastore
from app import parse_config


async def main() -> None:
    cfg = parse_config("config.yml")
    ds = await datastore.Client.create(cfg.datastore)
    await ds.initialize_tables()
    await ds.close()

    print("database init done.")


if __name__ == "__main__":
    asyncio.run(main())