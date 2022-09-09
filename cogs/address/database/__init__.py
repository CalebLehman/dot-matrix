from typing import Optional

from util.cog_database import CogDatabase


class AddressDatabase(CogDatabase):
    def __init__(self) -> None:
        super().__init__('address')

    def address_exists(self, name: str) -> bool:
        return self.execute_query('select count(*) from Address where Name = ? collate nocase', [name])[0][0] > 0

    def create_address(self, name: str, location: str) -> None:
        self.execute_non_query('insert into Address (Name, Location) VALUES (?, ?)', [name, location])

    def update_address(self, old_name: str, new_name: Optional[str], new_location: Optional[str]) -> None:
        update_statments = []
        update_parameters = []
        if new_name is not None:
            update_statments.append('Name = ?')
            update_parameters.append(new_name)
        if new_location is not None:
            update_statments.append('Location = ?')
            update_parameters.append(new_location)
        self.execute_non_query(
            f'update Address set {", ".join(update_statments)} where Name = ? collate nocase',
            [*update_parameters, old_name],
        )

    def get_address(self, name: str) -> tuple[str, str]:
        return self.execute_query('select Name, Location from Address where Name = ? collate nocase', [name])[0]

    def get_addresses(self) -> list[tuple[str, str]]:
        return self.execute_query('select Name, Location from Address', [])

    def delete_address(self, name: str) -> None:
        self.execute_non_query('delete from Address where Name = ? collate nocase', [name])


address_database = AddressDatabase()
