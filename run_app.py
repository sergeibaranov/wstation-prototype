import argparse
import asyncio

import uvicorn

from app import init_app, parse_config


async def main():
    # Set up argument parsing
    parser = argparse.ArgumentParser(description="Run the FastAPI application")
    parser.add_argument("--reload", action="store_true", help="Enable auto-reload")
    args = parser.parse_args()

    cfg = parse_config("./config.yml")
    app = init_app(cfg)
    if app is None:
        raise TypeError("app not instantiated")
    server = uvicorn.Server(
        uvicorn.Config(
            app, host=str(cfg.host), port=cfg.port, log_level="info", reload=args.reload
        )
    )
    await server.serve()


if __name__ == "__main__":
    asyncio.run(main())
