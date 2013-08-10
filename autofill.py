"""
Released under the MIT License
Copyright (c) 2013 Hashem Al-Dujaili
"""

import sys, re
sys.path.insert(0, 'libs')
import os
import webapp2
import jinja2
import urllib2
from google.appengine.ext import ndb
from db.builder import EnzymesDatabase, SitesDatabase, VectorDatabase
from dg.digest import Digest
import json as simplejson

"""This is to create JSON files in Google Cloud Store for magicsuggest autofill, not yet complete"""

class Sites3(ndb.Model):
    # Models unique DNA sites with the properties of name: and sequence:
    name = ndb.StringProperty()
    sequence = ndb.StringProperty(indexed=False)


class Vectors(ndb.Model):  # Vector database as ('pDONR201, 'ATG...')
    # Models plasmid vectors with the properties of name: and sequence:
    name = ndb.StringProperty()
    sequence = ndb.StringProperty(indexed=False)

class Enzymes(ndb.Model):
    """Models restriction enzymes with the properties of
    name:, frontsite:, and backsite:
    Enzyme database as ('EcoRV','ATG','GAC')"""
    name = ndb.StringProperty()
    frontsite = ndb.StringProperty(indexed=False)
    backsite = ndb.StringProperty(indexed=False)

class MainPage(webapp2.RequestHandler):

	def get(self):
	strenz = []
    qry = database.query()
    listenz = qry.fetch(projection=[database.name])
    for n in range(0, len(listenz), 1):
        strenz.append(listenz[n].name)
    response_json = simplejson.dumps(strenz)
    return response_json"""

    
application = webapp2.WSGIApplication([
    ('/autofill', MainPage)
], debug=True)
