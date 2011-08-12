#!/usr/bin/python
"""
convert.py -- converts a pentabarf xml file to RDF

Usage: convert.py <filename>
"""

from saxhandler import FahrplanHandler

from model import Event, Room, Track, Link, Person, Conference
import xml.sax.handler
import sys
from rdflib import ConjunctiveGraph

def main():
    if len(sys.argv) < 2:
        print "usage: convert.py <schedule.xml file location>"
    else:
        parse(" ".join(sys.argv[1:]))

def parse(filename):
    parser = xml.sax.make_parser()
    handler = FahrplanHandler()
    parser.setContentHandler(handler)
    parser.parse(filename)
    graph = ConjunctiveGraph()
    handler.conference.add_to_graph(graph)
    print(graph.serialize())
    

if __name__ == "__main__":
    main()
