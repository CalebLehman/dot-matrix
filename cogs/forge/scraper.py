import aiohttp
import dataclasses

import bs4

FORGE_URL = 'https://theforgetavern.com/events/list/'


@dataclasses.dataclass
class Event:
    name: str
    date: str
    start: str
    link: str


async def get_events() -> list[Event]:
    async with aiohttp.ClientSession() as session:
        async with session.get(FORGE_URL) as response:
            html = await response.read()
    soup = bs4.BeautifulSoup(html.decode('utf-8'), 'html.parser')
    events = []
    for row in soup.find_all('div', class_='tribe-events-calendar-list__event-details'):
        events.append(Event(
            name=row.find('a', class_='tribe-events-calendar-list__event-title-link').text.strip(),
            date=row.find('time', class_='tribe-events-calendar-list__event-datetime')['datetime'],
            start=row.find('time', class_='tribe-events-calendar-list__event-datetime').text.strip(),
            link=row.find('a', class_='tribe-events-calendar-list__event-title-link')['href'],
        ))
    return events
