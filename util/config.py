import os
import sys
import logging
import dataclasses

from dotenv import dotenv_values


log = logging.getLogger(__name__)


@dataclasses.dataclass
class Database:
    database: str
    schema: str


@dataclasses.dataclass
class Config:
    token: str
    prefix: str
    log_level: str
    event_channel: str


# TODO this should probably just be a constructor
def init_config():
    environment = {
        **dotenv_values('.env'),
        **dotenv_values('.env.dev'),
        **os.environ,
    }
    optional_variables = {
        'BOT_LOG_LEVEL': 'INFO'
    }
    for variable, default in optional_variables.items():
        if variable not in environment:
            log.warn(f'Missing environment variable \'{variable}\', using default \'{default}\'')
            environment[variable] = default
    is_valid = True
    required_variables = [
        'BOT_PREFIX',
        'BOT_TOKEN',
        'BOT_EVENTS_CHANNEL',
    ]
    for variable in required_variables:
        if variable not in environment:
            log.error(f'Missing required environment variable \'{variable}\'')
            is_valid = False
    if not is_valid:
        sys.exit(1)
    return Config(
        token=environment['BOT_TOKEN'],
        prefix=environment['BOT_PREFIX'],
        log_level=environment['BOT_LOG_LEVEL'],
        event_channel=environment['BOT_EVENTS_CHANNEL'],
    )


config = init_config()
