import asyncio
from loguru import logger

from src.bot.main import main


def setup_logger() -> None:
    logger.add(
        "logs/debug.log",
        rotation="10 MB",
        compression="zip",
        level="DEBUG",
        enqueue=True,
    )


if __name__ == "__main__":
    setup_logger()

    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass
