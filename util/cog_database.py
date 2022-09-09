import sqlite3
from contextlib import closing
from typing import Any


class CogDatabase():
    def __init__(self, cog_name: str) -> None:
        self.schema_file = f'cogs/{cog_name}/database/schema.sql'
        self.database_file = f'cogs/{cog_name}/database/database.db'
        with closing(self.get_connection()) as connection:
            with open(self.schema_file, 'r') as schema:
                connection.cursor().executescript(schema.read())
            connection.commit()

    def get_connection(self) -> sqlite3.Connection:
        return sqlite3.connect(self.database_file)

    def execute_non_query(self, script: str, parameters: list[str]) -> None:
        with closing(self.get_connection()) as database:
            database.cursor().execute(script, parameters)
            database.commit()

    def execute_query(self, script: str, parameters: list[str]) -> list[Any]:
        with closing(self.get_connection()) as database:
            return database.cursor().execute(script, parameters).fetchall()
