"""
Released under the MIT License
Copyright (c) 2013 Hashem Al-Dujaili
"""
import sys
import re
sys.path.insert(0, 'libs')
import os
import webapp2
import jinja2
from google.appengine.ext import ndb

JINJA_ENVIRONMENT = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),
    extensions=['jinja2.ext.autoescape'])


class Sequences(ndb.Model):
    # Models unique DNA sites with the properties of name: and sequence:
    name = ndb.StringProperty()
    sequence = ndb.StringProperty(indexed=False)


class CreateSequence(webapp2.RequestHandler):

    def post(self):

        seqname = self.request.POST['name']
        newseq = self.request.POST['sequence']
        if (seqname == '') or (newseq == ''):
            self.response.write('One or more fields were left blank, go back'
                                'and try again.')
            return
        if (seqname == "Enter sequence name..") or (newseq ==
                                                    "Enter sequence.."):
            self.response.write('One or more fields were left blank,'
                                'go back and try again.')
            return
        qry = Sequences.query(Sequences.name == seqname).get()
        if qry is not None:
            self.response.write('%s already exists, go back and use a'
                                'different name' % seqname)
            return
        newseq = re.sub(r'[0-9\W\n\r]*', '', newseq)
        newseq = newseq.lower()
        Sequences(name=seqname, sequence=newseq).put()

        self.redirect('/')
        return


class EditSequence(webapp2.RequestHandler):

    def post(self):

        origname = self.request.POST['origname']
        try:
            delseq = self.request.POST['delseq']
            if delseq is not None:
                seq = Sequences.query(Sequences.name == origname).get()
                seq.key.delete()
                self.redirect('/')
                return

        except KeyError:

            try:
                seqname = self.request.POST['name']
                newseq = self.request.POST['sequence']

                if (newseq == '') or (seqname == ''):
                    self.response.write('One or more fields were left blank,\
                     go back and try again.')
                    return

                newseq = re.sub(r'[0-9\W\n\r]*', '', newseq)
                newseq = newseq.lower()
                qry = Sequences.query(Sequences.name == origname).get()
                self.response.write(qry)
                qry.name = seqname
                qry.sequence = newseq
                qry.put()

                self.redirect('/')

            except KeyError:

                if (newseq == '') or (seqname == ''):
                    self.response.write('One or more fields were left blank,\
                     go back and try again.')
                    return

    def get(self):
        try:
            seqname = self.request.GET['seqname']
        except KeyError:
            self.redirect('/sequences')
            return

        qry = Sequences.query(Sequences.name == seqname).get()
        results = qry.sequence
        template = JINJA_ENVIRONMENT.get_template('sequences.html')
        self.response.write(template.render(
                            seqname=seqname,
                            results=results,
                            editseq=True))


class MainPage(webapp2.RequestHandler):

    def post(self):
        self.response.write(self.request.POST)

    def get(self):
        qry = Sequences.query()
        results = qry.fetch()
        template = JINJA_ENVIRONMENT.get_template('sequences.html')
        self.response.write(template.render(results=results))

application = webapp2.WSGIApplication([
    ('/sequences/editseq', EditSequence),
    ('/sequences', MainPage),
    ('/sequences/createseq', CreateSequence),
], debug=True)

