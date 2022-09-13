from util.cog_database import CogDatabase


class JackboxDatabase(CogDatabase):
    def __init__(self) -> None:
        super().__init__('jackbox')

    def game_exists(self, id: str) -> bool:
        return self.execute_query('select count(*) from Game where Id = ?', [id])[0][0] > 0

    def create_game(self, id: str, name: str) -> None:
        self.execute_non_query('insert into Game (Id, Name) VALUES (?, ?)', [id, name])


jackbox_database = JackboxDatabase()
