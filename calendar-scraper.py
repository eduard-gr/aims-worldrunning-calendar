import requests
from bs4 import BeautifulSoup
import datetime
import csv


from icalendar import Calendar, Event

cal = Calendar()
cal.add('prodid', '-//World Running calendar//')
cal.add('version', '2.0')


url = "https://aims-worldrunning.org/calendar.html"
response = requests.get(url)
soup = BeautifulSoup(response.content, "html.parser")

calendar = soup.find("div", class_="twelve columns")

year_month = None

for item in calendar.findChildren():
    if(item.has_attr("class") == False):
        continue

    style = item.get("class")

    is_calendar_month_header = "calendar-month-header" in style
    is_calendar_item = "calendar-item" in style

    if(is_calendar_month_header == False and is_calendar_item == False):
        continue

    if(is_calendar_month_header):
        year_month = item.text.strip()
        continue

    if(is_calendar_item):
        date = item.find("div", class_="calendar-date")
        if(date == None):
            continue

        if("calendar-date-cancelled" in date.get("class")):
            continue

        compressed = date.find("span", class_="calendar-date-compressed")

        if(compressed):
            parts = compressed.text.strip().split("–")
            days = [int(parts[0]), int(parts[1])]
        else:
            days = [date.text.strip()]


        link = item.find("a")

        # Add subcomponents
        event = Event()
        event.add('name', link.text)
        event.add('summary', link.text)
        event.add('LOCATION', link.text)
        event.add('source', link.get("href"))
        event.add('description', link.get("href"))


        start = datetime.datetime.strptime("%s %s" % (days[0], year_month), "%d %B %Y").date()
        event.add('dtstart', start)

        if(len(days) > 1):
            
            if(days[0] > days[1]):
                end = start + datetime.timedelta(days=days[1])
            else:
                end = datetime.datetime.strptime("%s %s" % (days[1], year_month), "%d %B %Y").date()

            event.add('dtend', end)

        else:
            event.add('dtend', start)


        cal.add_component(event)

        # if(len(cal.walk("VEVENT")) > 4):
        #     break

f = open('marathons.ics', 'wb')
f.write(cal.to_ical())
f.close()