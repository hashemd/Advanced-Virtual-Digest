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

JINJA_ENVIRONMENT = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),
    extensions=['jinja2.ext.autoescape'])

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

def CreateJSON(database):

#Creates JSON files for all database name entries to use with typeahead.js
    strenz = []
    qry = database.query()
    listenz = qry.fetch(projection=[database.name])
    for n in range(0, len(listenz), 1):
        strenz.append(listenz[n].name)
    response_json = simplejson.dumps(strenz)
    return response_json


class Results(webapp2.RequestHandler):
    """Displays digest results using jinja2 and POST data"""
    def cleanData(self, option):
        data = self.request.POST[option]
        data = data.split(',')
        clean = []

        for cln in data:
            cln = re.sub(r'["/\]\[]]*','',cln)
            clean.append(cln)
        if len(clean) == 1:
            clean = clean[0]
        return clean

    def get(self):

        self.redirect('/')

    def post(self):
        template = JINJA_ENVIRONMENT.get_template('result.html')

        try: instruction = self.cleanData('options')
        except KeyError:
            self.response.write("I can't read minds, make sure you select \
             an option. Go back and try again.")
            return
        try: shape = self.cleanData('shape')
        except KeyError:
            self.response.write('Shape was left blank, go back and try again.')
            return

        try:
            vec_name = self.cleanData('vec_names')
            try: 
                sequence = self.cleanData('sequence')
                if (sequence == 'sequence') or (sequence == ''):
                    sequence = None
                    sites = ''
                else:
                    try: sites = self.cleanData('rest_sites')
                    except KeyError:
                        self.response.write('Sites surrounding insert not\
                        specified despite a vector and insert being provided.')
                        return                     
            except KeyError: 
                sequence = None
                sites = ''
                pass
        except KeyError:
            try:
                sequence = self.cleanData('sequence')
                vec_name = ''
            except KeyError:
                self.response.write('Sequence and vector name were left blank, go back and try again.')
                return

        qry = Sequences.query(Sequences.name == sequence).get()

        if qry is not None:
            sequence = qry.sequence

        if len(vec_name) > 0:
                if len(sites) == 0:
                    sequence = Vectors.query(Vectors.name==vec_name).get().sequence

                else:
                    sites_database = Sites3
                    first_site = sites[0]
                    second_site = sites[1]
                    sequence = Digest(Enzymes, sequence, shape).insert(
                                                            first_site,
                                                            second_site,
                                                            vec_name,
                                                            Vectors,
                                                            sites_database)
        try:
            name = self.cleanData("digest_name")
        except KeyError:
            if (len(sequence) < 51) and (len(sequence) > 0):
                name = sequence
            else:
                name = 'Unnamed Digest'

        if name == '':
            if (len(sequence) < 51) and (len(sequence) > 0):
                name = sequence
            else:
                name = 'Unnamed Digest'

        # POST Data from HTML:
        # ins_seq, vec_name, rest_sites, options, enz_list

        if instruction == 'Linearize Sequence':

            if shape == 'Linear':
                self.response.write('You have stated the sequence is already\
                    linear, there is nothing for me to do.')

            results = Digest(Enzymes, sequence, shape).linearize()

            title = 'The following enzymes will linearize the sequence: %s' \
                % name
            headings = ['Enzyme', "Cuts at base:"]
            self.response.write(template.render(title=title,
                                headings=headings, results=results))

        elif instruction == 'Remove Insert':
            
            template = JINJA_ENVIRONMENT.get_template('result_rem.html')

            sequence = self.cleanData('sequence')
            qry = Sequences.query(Sequences.name == sequence).get()

            if qry is not None:
                sequence = qry.sequence

            first_site = sites[0]
            second_site = sites[1]

            title = 'The following enzymes will cut in %s and not %s' \
                    % (vec_name, name)

            headings = ['Enzyme', 'Side Product Lengths:']

            if ('att' in first_site) or ('att' in second_site):
                sites_database = Sites3
            else: 
                sites_database = None

            results = Digest(Enzymes, sequence, shape).rem_insert(
                                                            first_site,
                                                            second_site,
                                                            vec_name,
                                                            Vectors,
                                                            sites_database)

            self.response.write(
                template.render(
                title=title,
                headings=headings,
                results=results,
                instruction='digest_rem'
                ))

        elif instruction == 'Map Sequence':

            results = Digest(Enzymes, sequence, shape).enzyme_map()

            title = 'The following enzymes will cut the sequence: %s' % name
            headings = ['Enzyme', "Fragment Lengths:"]
            self.response.write(template.render(
                title=title, headings=headings, results=results))

        elif instruction == 'Custom Digest':

            enz_list = self.cleanData('enzymes')
            if isinstance(enz_list, basestring):
                enz_list = [enz_list]
            
            title = 'Results for digesting %s with: ' % name
            for enzyme in enz_list:
                title += enzyme + ', '
            title = title[:len(title)-2]
            
            headings = ['Fragment', 'Fragment Lengths:']
            results = Digest(Enzymes, sequence, shape).multi_digest(enz_list)
            if results == -1:
                self.response.write(title + '<br><br> No cuts detected')
                return
            results = sorted(results, key=lambda x:int(x[1]), reverse=True)

            self.response.write(template.render(
                                title=title,
                                headings=headings,
                                results=results))


class MainPage(webapp2.RequestHandler):

    def get(self):
        #The reason I'm rendering this is because I'm planning on making the index dynamic at some point soon.
        template = JINJA_ENVIRONMENT.get_template('index.html')
        self.response.write(template.render())
        
application = webapp2.WSGIApplication([
    ('/', MainPage),
    ('/results', Results),
], debug=True)
