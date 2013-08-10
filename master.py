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

"""
This file is used to run one time scripts / hacks, can only be accessed by someone with admin level access.
"""

class Sites3(ndb.Model):
    # Models unique DNA sites with the properties of name: and sequence:
    name = ndb.StringProperty()
    sequence = ndb.StringProperty(indexed=False)


class Vectors(ndb.Model):  # Vector database as ('pDONR201, 'ATG...')
    # Models plasmid vectors with the properties of name: and sequence:
    name = ndb.StringProperty()
    sequence = ndb.StringProperty(indexed=False)

class Sequences(ndb.Model):
    # Models unique DNA sites with the properties of name: and sequence:
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
    	Sequences(name='Test1',sequence='Test1').put()
    	Sequences(name='Test2',sequence='Test2').put()
    	self.response.write('Success')

application = webapp2.WSGIApplication([
    ('/master', MainPage)
], debug=True)

