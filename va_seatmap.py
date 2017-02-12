# coding: utf-8
import requests
import logging
from lxml import html, etree
import datetime
i = datetime.datetime.now()
now = i.isoformat()

logging.basicConfig(level=logging.DEBUG)

last_name = ''
reservation_code = ''


class Seat:
    def __init__(self, c):
        self.avail = 'unavailable' not in c
        self.chosen = 'reserved' in c
        self.paid = 'prepay' in c

    def __repr__(self):
        return '{};{};{}'.format(self.chosen, self.avail, self.paid)

    def __str__(self):
        return '{};{};{}'.format(self.chosen, self.avail, self.paid)


class SeatMap:
    def __init__(self, s, start, finish):
        self.seats = {}
        self.start = str(start)
        self.finish = str(finish)
        for seat in s:
            row = seat.get('data-row_index')
            col = seat.get('data-column_index')
            if row not in self.seats:
                self.seats[row] = {}

            if col in self.seats[row]:
                print('fuck')
            else:
                self.seats[row][col] = Seat(seat.get('class'))

    def get_row(self, id: str) -> int:
        return int(id.split('-')[2][:-1])

    def get_col(self, id: str) -> str:
        return id.split('-')[2][-1:]

    def __repr__(self) -> str:
        formatted = '{},{}\n'.format(self.start, self.finish)
        for row, cols in self.seats.items():
            for col, seat in cols.items():
                formatted += '{};{};{},'.format(row, col, str(seat))
            formatted = formatted.rstrip(',') + '\n'
        return formatted

logging.info('Checking for LAST NAME: {} and RESERVATION NUMBER: {}'.format(last_name, reservation_code))

s = requests.Session()
s.get('https://fly.virginaustralia.com/SSW2010/VAVA/myb.html?lastName={}&reservationCode={}'.format(
    last_name,
    reservation_code
))

r = s.get(
    'https://fly.virginaustralia.com/SSW2010/VAVA/seats.html?viewReloc={}&sourcePage=/SSW2010/VAVA/viewitinerary.html?d=abc&reloc={}'.format(
        reservation_code,
        reservation_code
    ))
tree = html.fromstring(r.content)
segments = tree.xpath("//div[contains(@id, 'seat-map-segment')]")
seat_maps = []

logging.info('{} flights found'.format(len(segments)))
for segment in segments:
    seats = segment.xpath(".//td[contains(@class, 'seat-map-seat')]")
    start = segment.xpath(".//span[contains(@class, 'seat-map-flights-segment-from')]")[0].text.strip()
    finish = segment.xpath(".//span[contains(@class, 'seat-map-flights-segment-to')]")[0].text.strip()
    seat_maps.append(SeatMap(seats, start, finish))

logging.info('Printing {} seat maps'.format(len(seat_maps)))
for m in seat_maps:
    filename = '{}_{}_{}-{}_{}.csv'.format(last_name, reservation_code, m.start, m.finish, now)
    with open(filename, 'w') as o:
        o.write(str(m))