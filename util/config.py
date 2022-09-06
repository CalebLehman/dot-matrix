import os
import sys
import logging
from dataclasses import dataclass

from dotenv import dotenv_values


log = logging.getLogger(__name__)
__config = None


@dataclass
class Database:
    database: str
    schema: str


@dataclass
class Config:
    token: str
    prefix: str
    log_level: str
    databases: dict[Database]


def get_config():
    global __config
    if __config is None:
        __config = __init_config()
    return __config


def __init_config():
    environment = {
        **dotenv_values('.env'),
        **dotenv_values('.env.dev'),
        **os.environ,
    }
    optional_variables = {
        'BOT_LOGLEVEL': 'INFO'
    }
    for variable, default in optional_variables.items():
        if variable not in environment:
            log.warn(f'Missing environment variable \'{variable}\', using default \'{default}\'')
            environment[variable] = default
    is_valid = True
    required_variables = [
        'BOT_PREFIX',
        'BOT_TOKEN',
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
        log_level=environment['BOT_LOGLEVEL'],
        databases={
            'address': Database(database='cogs/address/database/database.db', schema='cogs/address/database/schema.sql'),
        }
    )
