from datetime import datetime, timedelta
from typing import List

import requests
from icalendar import Calendar, Event
from recurring_ical_events import of


def get_gcal_entries(url: str, type: str, qty: int) -> List[Event]:
    if type == 'airbnb':
        summary_title = 'Reserved'
    elif type == 'home':
        summary_title = 'cleaning'
    else:
        raise Exception("invalid type specified, expecting 'airbnb' or 'home'")

    response = requests.get(url)
    response.raise_for_status()
    cal = Calendar.from_ical(response.text)

    after = datetime.now() + timedelta(days=-2)
    event_generator = of(cal).after(after)

    events = []

    while len(events) < qty:
        try:
            event = next(event_generator)
            if event['SUMMARY'] == summary_title:
                events.append(event)
        except StopIteration:
            break

    return events