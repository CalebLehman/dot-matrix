import sys
import logging
import asyncio

from bot import Bot
from util.config import get_config


logging.basicConfig(
    datefmt='%Y-%m-%d %H:%M:%S',
    style='{',
    format='{asctime},{levelname},{name},{message}',
)
log: logging.Logger = logging.getLogger(__name__)


def main() -> None:
    logging.getLogger().setLevel(get_config().log_level)
    bot: Bot = Bot(get_config().prefix)
    try:
        asyncio.run(bot.load_extension('address'))
    except Exception:
        log.exception('Failed to load cog \'address\'')
        sys.exit(1)
    bot.run(get_config().token)


if __name__ == '__main__':
    main()
