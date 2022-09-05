import sqlite3
from typing import Any
from contextlib import closing

SCHEMA_FILE = 'database/schema.sql'
DATABASE_FILE = 'database/database.db'


class Database():
    def __init__(self) -> None:
        with closing(self.__get_connection()) as connection:
            with open(SCHEMA_FILE, 'r') as schema:
                connection.cursor().executescript(schema.read())
            connection.commit()

    def __get_connection(self) -> sqlite3.Connection:
        return sqlite3.connect(DATABASE_FILE)

    def __execute_non_query(self, script: str, params: list[str]) -> None:
        with closing(self.__get_connection()) as database:
            database.cursor().execute(script, params)
            database.commit()

    def __execute_query(self, script: str, params: list[str]) -> list[Any]:
        with closing(self.__get_connection()) as database:
            return database.cursor().execute(script, params).fetchall()

    def address_exists(self, name: str) -> bool:
        return self.__execute_query('select count(*) from Address where Name = ? collate nocase', [name])[0][0] > 0

    def create_address(self, name: str, location: str) -> None:
        self.__execute_non_query('insert into Address (Name, Location) VALUES (?, ?)', [name, location])

    def update_address(self, old_name: str, new_name: str, new_location: str) -> None:
        self.__execute_non_query(
            'update Address set Name = ?, Location = ? where Name = ? collate nocase',
            [new_name, new_location, old_name],
        )

    def get_address(self, name: str) -> tuple[str, str]:
        return self.__execute_query('select Name, Location from Address where Name = ? collate nocase', [name])[0]

    def delete_address(self, name: str) -> None:
        self.__execute_non_query('delete from Address where Name = ? collate nocase', [name])
