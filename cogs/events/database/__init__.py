from util.cog_database import CogDatabase


class EventsDatabase(CogDatabase):
    def __init__(self) -> None:
        super().__init__('events')

    def event_exists(self, id: int) -> None:
        return self.execute_query('select count(*) from Event where Id = ?', [id])[0][0] > 0

    def create_event(self, id: int, message_id: int) -> None:
        self.execute_non_query('insert into Event (Id, MessageId) VALUES (?, ?)', [id, message_id])

    def get_event_message(self, id: int) -> int:
        return self.execute_query('select MessageId from Event where Id = ?', [id])[0][0]

    def delete_event(self, id: int) -> None:
        self.execute_non_query('delete from Event where Id = ?', [id])

    def create_guest(self, name: str, event_id: int) -> None:
        self.execute_non_query('insert into Guest (Name, EventId) VALUES (?, ?)', [name, event_id])

    def get_guests(self, event_id: int) -> list[str]:
        return [row[0] for row in self.execute_query('select Name from Guest where EventId = ?', [event_id])]

    def delete_guest(self, name: str, event_id: int) -> None:
        self.execute_non_query('delete from Guest where Name = ? collate nocase and EventId = ?', [name, event_id])

    def delete_guests(self, event_id: int) -> None:
        self.execute_non_query('delete from Guest where EventId = ?', [event_id])


events_database = EventsDatabase()
