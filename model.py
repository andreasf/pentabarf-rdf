"""
Pentabarf model. 

Usage: create instances, then convert to RDF by calling 
Conference.add_to_graph(graph), with graph being a 
rdflib.ConjunctiveGraph.
"""

from rdflib import BNode, Namespace, Literal, URIRef

FPONT = Namespace('http://fahrplan.u0d.de/schedule.owl#')
FP = Namespace('http://fahrplan.u0d.de/')
FOAF = Namespace('http://xmlns.com/foaf/0.1/')
RDF = Namespace('http://www.w3.org/1999/02/22-rdf-syntax-ns#')
RDFS = Namespace('http://www.w3.org/2000/01/rdf-schema#')

class Schedule:
    def __init__(self, version, conference):
        # unused so far -- should be used for the fahrplan version info
        self.version = version
        self.conference = conference

class Conference:
    def __init__(self):
        #self.title = None
        #self.subtitle = None
        #self.venue = None
        #self.city = None
        #self.start = None
        #self.end = None
        self.rooms = dict()
        self.tracks = dict()
        self.events = list()
        self.persons = dict()

    def add_to_graph(self, graph):
        conf_name = self.title.replace(" ", "_") # uri should be properly encoded...
        this = FP[conf_name]
        graph.add((this, RDF['type'], FPONT['Conference']))
        graph.add((this, RDFS.label, Literal(self.title)))
        graph.add((this, FPONT.hasSubtitle, Literal(self.subtitle)))
        graph.add((this, FPONT.hasVenue, Literal(self.venue)))
        graph.add((this, FPONT.hasCity, Literal(self.city)))

        # create track uris from the track names
        for key in self.tracks:
            track = self.tracks[key]
            tn = track.name.replace(" ", "_")
            track.uri = URIRef(this + "/track/" + tn)
            track.add_to_graph(graph)
            graph.add((this, FPONT.hasTrack, track.uri))
        
        # create room uris from the room names
        for key in self.rooms:
            room = self.rooms[key]
            rn = room.name.replace(" ", "_") # should be properly encoded
            room.uri = URIRef(this + "/room/"+ rn)
            room.add_to_graph(graph)
        
        # create person uris using the person ids
        for key in self.persons:
            person = self.persons[key]
            person.uri = URIRef(this + "/person/" + key)
            person.add_to_graph(graph)
        
        for event in self.events:
            event.uri = URIRef(this + "/event/" + event.event_id)
            event.add_to_graph(graph)

class Event:
    def __init__(self, event_id):
        self.event_id = event_id
        #self.title = None
        #self.subtitle = None
        #self.start = None
        #self.end = None
        self.track = None
        #self.room = None 
        #self.language = None
        #self.abstract = None
        #self.description = None
        self.persons = list()
        self.links = list() 
        #self.event_type = None

    def add_to_graph(self, graph):
        this = self.uri
        graph.add((this, FP['hasTitle'], Literal(self.title)))
        if self.subtitle is not None:
            graph.add((this, FP['hasSubtitle'], Literal(self.subtitle)))
        graph.add((this, FP['starts'], Literal(self.start)))
        graph.add((this, FP['ends'], Literal(self.end)))
        if self.track is not None:
            graph.add((self.track.uri, FP['hasEvent'], this))
        if self.language is not None:
            graph.add((this, FP['hasLanguage'], Literal(self.language)))
        graph.add((this, FP['hasRoom'], self.room.uri))
        for person in self.persons:
            graph.add((this, FP['hasSpeaker'], person.uri))
        for link in self.links:
            graph.add((this, RDFS['seeAlso'], link.url))
        if self.abstract is not None:
            graph.add((this, FP['hasAbstract'], Literal(self.abstract)))
        if self.description is not None:
            graph.add((this, FP['hasDescription'], Literal(self.description)))
            

        # set rdf type
        if self.event_type == "lecture":
            graph.add((this, RDF['type'], FPONT['Lecture']))
        if self.event_type == "workshop":
            graph.add((this, RDF['type'], FPONT['Workshop']))
        if self.event_type == "contest":
            graph.add((this, RDF['type'], FPONT['Contest']))
        if self.event_type == "meeting":
            graph.add((this, RDF['type'], FPONT['Meeting']))


class Link:
    def __init__(self, url):
        self.url = url
        self.description = None


class Person:
    def __init__(self, person_id):
        self.person_id = person_id
        self.name = None
        self.uri = None

    def add_to_graph(self, graph):
        graph.add((self.uri, FOAF.name, Literal(self.name)))
        graph.add((self.uri, RDF['type'], FPONT['Person']))


class Room:
    def __init__(self, name):
        self.name = name
        #self.uri = None

    def add_to_graph(self, graph):
        graph.add((self.uri, RDFS['label'], Literal(self.name)))
        graph.add((self.uri, RDF['type'], FPONT['Room']))


class Track:
    def __init__(self, name):
        self.name = name
        self.uri = None
    
    def add_to_graph(self, graph):
        graph.add((self.uri, RDFS['label'], Literal(self.name)))
        graph.add((self.uri, RDF['type'], FPONT['Track']))

