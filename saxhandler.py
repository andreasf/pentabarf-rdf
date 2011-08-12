"""
SAX handler, creates model objects from a pentabarf xml file.
"""

from model import Event, Room, Track, Link, Person, Conference
import xml.sax.handler
import xml.sax
import datetime
from rdflib import ConjunctiveGraph

class FahrplanHandler(xml.sax.handler.ContentHandler):
    def __init__(self):
        self.year = None
        self.month = None
        self.day = None
        self.event = None
        self.in_event = False
        self.buf = None
        self.rooms = dict()
        self.tracks = dict()
        self.events = list()
        self.daychange = None
        self.person = None
        self.link = None
        self.in_conference = False
        self.conference = None

    def setDay(self, day_string):
        el = day_string.split("-")
        assert len(el) == 3
        self.year = int(el[0])
        self.month = int(el[1])
        self.day = int(el[2])

    def startElement(self, name, attributes):
        if name == "day":
            self.setDay(attributes["date"])
        elif name == "conference":
            self.conference = Conference()
            self.in_conference = True
        elif name == "event":
            event_id = attributes["id"]
            self.event = Event(event_id)
            self.in_event = True
        elif name == "link":
            if self.in_event:
                self.link = Link(attributes["href"])
        elif name == "person":
            if self.in_event:
                self.person = self.get_person(attributes["id"])

    def endElement(self, name):
        if name == "event":
            self.in_event = False
            self.conference.events.append(self.event)
            self.event = None
        elif name == "start":
            if self.in_event:
                el = self.buf.split(":")
                assert len(el) == 2
                hour = int(el[0])
                minute = int(el[1])
                self.event.start = self.check_daychange(datetime.datetime(self.year, self.month, self.day, hour, minute))
            elif self.in_conference:
                el = self.buf.split("-")
                assert len(el) == 3
                self.conference.start = datetime.datetime(int(el[0]), int(el[1]), int(el[2]))
        elif name == "end":
            if self.in_conference:
                el = self.buf.split("-")
                assert len(el) == 3
                self.conference.end = datetime.datetime(int(el[0]), int(el[1]), int(el[2]))
        elif name == "duration":
            if self.in_event:
                el = self.buf.split(":")
                assert len(el) == 2
                delta = datetime.timedelta(hours=int(el[0]), minutes=int(el[1]))
                self.event.end = self.event.start + delta
        elif name == "room":
            if self.in_event:
                room = self.get_room(self.buf)
                self.event.room = room
        elif name == "title":
            if self.in_event:
                self.event.title = self.buf
            elif self.in_conference:
                self.conference.title = self.buf
        elif name == "subtitle":
            if self.in_event:
                self.event.subtitle = self.buf
            elif self.in_conference:
                self.conference.subtitle = self.buf
        elif name == "type":
            if self.in_event:
                self.event.event_type = self.buf
        elif name == "track":
            if self.in_event:
                if self.buf is not None:
                    track = self.get_track(self.buf)
                    self.event.track = track
        elif name == "language":
            if self.in_event:
                self.event.language = self.buf
        elif name == "abstract":
            if self.in_event:
                self.event.abstract = self.buf
        elif name == "description":
            if self.in_event:
                self.event.description = self.buf
        elif name == "link":
            if self.in_event:
                self.link.description = self.buf
                self.event.links.append(self.link)
                self.link = None
        elif name == "person":
            if self.in_event:
                self.person.name = self.buf
                self.event.persons.append(self.person)
                self.person = None
        elif name == "venue":
            if self.in_conference:
                self.conference.venue = self.buf
        elif name == "city":
            if self.in_conference:
                self.conference.city = self.buf
        elif name == "conference":
            self.in_conference = False
        elif name == "day_change":
            el = self.buf.split(":")
            assert len(el) == 2
            self.daychange = datetime.timedelta(hours=int(el[0]), minutes=int(el[1]))

    def get_track(self, name):
        try:
            track = self.conference.tracks[name]
        except KeyError:
            track = Track(name)
            self.conference.tracks[name] = track
        return track

    def get_room(self, name):
        try:
            room = self.conference.rooms[name]
        except KeyError:
            room = Room(name)
            self.conference.rooms[name] = room
        return room

    def get_person(self, person_id):
        try:
            person = self.conference.persons[person_id]
        except KeyError:
            person = Person(person_id)
            self.conference.persons[person_id] = person
        return person

    def characters(self, data):
        self.buf = data.strip()
        if self.buf == "":
            self.buf = None
    
    def check_daychange(self, timestamp):
        dc = datetime.datetime(timestamp.year, timestamp.month, timestamp.day) + self.daychange
        if timestamp < dc:
            # next day
            timestamp = timestamp + datetime.timedelta(days=1)
        return timestamp


        

def main():
    parser = xml.sax.make_parser()
    handler = FahrplanHandler()
    parser.setContentHandler(handler)
    parser.parse("schedule.en.xml")
    graph = ConjunctiveGraph()
    handler.conference.add_to_graph(graph)
    print(graph.serialize())
    

if __name__ == "__main__":
    main()
