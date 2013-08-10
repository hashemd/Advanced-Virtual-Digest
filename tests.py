"""
Released under the MIT License
Copyright (c) 2013 Hashem Al-Dujaili
"""
import sys, re
sys.path.insert(0, 'libs')
import os
import webapp2
from google.appengine.ext import ndb
from db.builder import EnzymesDatabase, SitesDatabase, VectorDatabase
from dg.digest import Digest
import json as simplejson

#Define the databases


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

class Check_db(webapp2.RequestHandler):
    def get(self):
        EnzymesDatabase.check_db()
        VectorDatabase.check_db()
        SitesDatabase.check_db()
        self.redirect('/')

class Digesttests(webapp2.RequestHandler):

    def get(self):
        shape = 'Circular'

        try: testcustom_one = Digest(Enzymes, 'ddddgatatccccc', shape).multi_digest('EcoRV')
        except Exception, e: self.response.write('Error in %s Report<br > %s <br > <br >' % ('testcustom_one', e))

        try:
            enzymes = ['EcoRI', 'EcoRV']
            testcustom_multi = Digest(Enzymes, 'ddddgatatcccccgaattceeee', shape).multi_digest(enzymes)
        except Exception, e: self.response.write('Error in %s Report<br > %s <br > <br >' % ('testcustom_multi <br >', e))

        try: sequence = Digest(Enzymes, 'ddddgatatccccc', shape).insert('attP1', 'attP2', 'pDONR201', Vectors, Sites3)
        except Exception, e: self.response.write('Error in %s Report<br > %s <br > <br >' % ('sequence <br >', e))

        try: testcustom_vector = Digest(Enzymes, sequence, shape).multi_digest(enzymes)
        except Exception, e: self.response.write('Error in %s Report<br > %s <br > <br >' % ('testcustom_vector <br >', e))

        try: testmap = Digest(Enzymes, 'ddddgatatcccccgaattceeee', shape).enzyme_map()
        except Exception, e: self.response.write('Error in %s Report<br > %s <br > <br >' % ('testmap', e))

        try:
            testremove = Digest(Enzymes, 'ddddgatatccccc', shape).rem_insert('EcoRI','EcoRV','pRS303',Vectors,Sites3)
        except Exception, e: self.response.write('Error in %s Report<br > %s <br > <br >' % ('testremove <br >', e))

        try: testlinearize = Digest(Enzymes, 'ddddgatatccccc', shape).linearize()
        except Exception, e: self.response.write('Error in %s Report<br > %s <br > <br >' % ('testlinearize <br >', e))

        try: self.response.out.write([testcustom_one, '<br >', testcustom_vector, '<br >', testcustom_multi, '<br >',
               'Hello:', testmap, '<br >',  testremove , '<br >', testlinearize, '<br >']  )
        except Exception, e: self.response.write(e)

application = webapp2.WSGIApplication([
    ('/tests', Digesttests),
    ('/dbcheck', Check_db)
], debug=True)
