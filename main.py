import sys
import logging
import asyncio
import pathlib

from bot import Bot
from util.config import config


logging.basicConfig(
    datefmt='%Y-%m-%d %H:%M:%S',
    style='{',
    format='[{asctime}] [{levelname:8}] {name}: {message}',
)
log = logging.getLogger(__name__)


async def main() -> None:
    logging.getLogger().setLevel(config.log_level)
    bot = Bot(config.prefix)
    for cog_path in pathlib.Path('cogs').iterdir():
        cog = str(cog_path).replace('/', '.').replace('.py', '')
        filter_prefix = '_'
        if cog_path.name.startswith(filter_prefix):
            log.info(f'Skipping loading cog \'{cog}\' which starts with \'{filter_prefix}\'')
        else:
            try:
                await bot.load_extension(cog)
                log.info(f'Successfully loaded cog \'{cog}\'')
            except Exception:
                log.exception(f'Failed to load cog \'{cog}\'')
                sys.exit(1)
    await bot.start(config.token)


if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        log.info('Shutting down')
        pass
