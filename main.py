import sys
import logging
import asyncio

from bot import Bot
from util.config import get_config


logging.basicConfig(
    datefmt='%Y-%m-%d %H:%M:%S',
    style='{',
    format='[{asctime}] [{levelname:8}] {name}: {message}',
)
log: logging.Logger = logging.getLogger(__name__)

cogs = [
    'cogs.address',
]


def main() -> None:
    logging.getLogger().setLevel(get_config().log_level)
    bot: Bot = Bot(get_config().prefix)
    for cog in cogs:
        try:
            asyncio.run(bot.load_extension(cog))
        except Exception:
            log.exception(f'Failed to load cog \'{cog}\'')
            sys.exit(1)
    bot.run(get_config().token)


if __name__ == '__main__':
    main()
