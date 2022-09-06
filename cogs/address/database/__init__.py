import sqlite3
from typing import Any, Optional
from contextlib import closing


class Database():
    def __init__(self, schema_file: str, database_file: str) -> None:
        self.database_file = database_file
        with closing(self.__get_connection()) as connection:
            with open(schema_file, 'r') as schema:
                connection.cursor().executescript(schema.read())
            connection.commit()

    def __get_connection(self) -> sqlite3.Connection:
        return sqlite3.connect(self.database_file)

    def __execute_non_query(self, script: str, parameters: list[str]) -> None:
        with closing(self.__get_connection()) as database:
            database.cursor().execute(script, parameters)
            database.commit()

    def __execute_query(self, script: str, parameters: list[str]) -> list[Any]:
        with closing(self.__get_connection()) as database:
            return database.cursor().execute(script, parameters).fetchall()

    def address_exists(self, name: str) -> bool:
        return self.__execute_query('select count(*) from Address where Name = ? collate nocase', [name])[0][0] > 0

    def create_address(self, name: str, location: str) -> None:
        self.__execute_non_query('insert into Address (Name, Location) VALUES (?, ?)', [name, location])

    def update_address(self, old_name: str, new_name: Optional[str], new_location: Optional[str]) -> None:
        update_statments = []
        update_parameters = []
        if new_name is not None:
            update_statments.append('Name = ?')
            update_parameters.append(new_name)
        if new_location is not None:
            update_statments.append('Location = ?')
            update_parameters.append(new_location)
        self.__execute_non_query(
            f'update Address set {", ".join(update_statments)} where Name = ? collate nocase',
            [*update_parameters, old_name],
        )

    def get_address(self, name: str) -> tuple[str, str]:
        return self.__execute_query('select Name, Location from Address where Name = ? collate nocase', [name])[0]

    def get_addresses(self) -> list[tuple[str, str]]:
        return self.__execute_query('select Name, Location from Address', [])

    def delete_address(self, name: str) -> None:
        self.__execute_non_query('delete from Address where Name = ? collate nocase', [name])
