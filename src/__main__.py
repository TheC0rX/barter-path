import asyncio

from loguru import logger
from rich.logging import RichHandler

from src.bot.main import main


def setup_logger() -> None:
    logger.remove()

    logger.add(
        RichHandler(markup=True, rich_tracebacks=True, tracebacks_show_locals=True),
        format="| {time:YYYY-MM-DD HH:mm:ss} | {message}",
        level="DEBUG",
    )

    logger.add(
        "logs/debug.log",
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {message}",
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
