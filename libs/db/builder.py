from bs4 import BeautifulSoup
import urllib2
import sys
import re
import os
sys.path.insert(0,'libs')
from google.appengine.ext import ndb, deferred

class VectorDatabase():

    def __init__(self, database):
        self.database = database

    def db_check(self):

        test_vec_yeast = self.database.query(self.database.name=='pXP116').get()
        test_vec_gateway = self.database.query(self.database.name=='pDONR201').get()
        test_vec_unspecified = self.database.query(self.database.name=='pRS303').get()
        return_string = ''
        if test_vec_yeast is None:
            deferred.defer(self.dl_vectors, 'Yeast', _target='builder')
        if test_vec_gateway is None:
            deferred.defer(self.dl_vectors, 'Other', _target='builder')
        if test_vec_unspecified is None:
            deferred.defer(self.dl_vectors, 'Unspecified', _target='builder')

    def dl_vectors(self, dburl):

        dburl = dburl.lower()
        dburl = dburl.title()
        dburl = "http://www.addgene.org/vector-database/query/?q_vdb=*+***%20vector_type:" + dburl
    
        http = urllib2.urlopen(dburl).read()
        soup = BeautifulSoup(http)
    
        tbl = soup.find(id='results')
        tbl = re.sub('<input\sid.*?value="','', str(tbl))
        tbl = tbl.replace('###','')
    
        list = tbl.split('::')
    
        vec_dict = {}
    
        for n in range(0, len(list), 9):
            try:
                if list[n+8] == 'yes':
                    if 'vector' in list[n+7]:
                        r = re.search(r'\d+',str(list[n+7]))
                        vec_dict[list[n+1]] = ("/browse/sequence/%s/giraffe-analyze_vdb/" % r.group())
                    else: vec_dict[list[n+1]] = ("%ssequences/" % str(list[n+7]))
            except IndexError: break

        for vector in vec_dict:
            if 'giraffe' in vec_dict[vector]:
                try:
                    http = urllib2.urlopen('http://www.addgene.org/' + vec_dict[vector]).read()
                    giraffelink = re.search(r'src="(/g.*?)"',http,re.DOTALL).group(1)
                    http = urllib2.urlopen('http://www.addgene.org' + str(giraffelink)).read()
                    srch = re.search(r'[a-zA-Z]{20}[a-zA-Z\n]{20,}',http).group(0)
                    self.database(name=vector,sequence=srch).put()
                except AttributeError: continue
            else:
                try:
                    http = urllib2.urlopen('http://www.addgene.org/' + vec_dict[vector]).read()
                    srch = re.search(r'[a-zA-Z]{20}[a-zA-Z\n]{20,}',http).group(0)
                    self.database(name=vector,sequence=srch).put()
                except AttributeError: continue
    
        return("completed")

class SitesDatabase():
    def __init__(self,database):
        self.database = database

    def db_check(self):
        test_att_site = self.database.query(self.database.name=='attB4').get()
        if test_att_site is None:
            deferred.defer(self.dl_sites, _target='builder')
    
    def dl_sites(self):

        sitelist = []

        dburl = "http://chien.neuro.utah.edu/tol2kitwiki/index.php/Att_site_sequences"  
        http = urllib2.urlopen(dburl).read()

        src = re.findall(r'gt;.*?([\w\d]+).*?([A-Z]{3,}.*?)[&<]', http,flags=re.DOTALL)
        for n in range (0,len(src),1):
            if '_' in src[n][0]: continue
            else: self.database(name=src[n][0],sequence=src[n][1]).put()
    
class EnzymesDatabase():


    def __init__(self, database):
        self.database = database

    def db_check(self):
        test_enz = self.database.query(self.database.name=='EcoRV').get()
        if test_enz is None:
            deferred.defer(self.dl_enzymes, _target='builder')

    def dl_enzymes(self):

        enzlist = []
    
        dburl = "http://www.addgene.org/mol_bio_reference/restriction_enzymes/"
        http = urllib2.urlopen(dburl).read()
        soup = BeautifulSoup(http)
    
        tbl = soup.find('table',attrs={'class':'border-box w400'})
        src = tbl.find_all('td')
        src = re.sub(r'<td>\s</td>,', '', str(src))
        src = src.split(',')
    
        for n in range(0, len(src), 2):
            try:
                name = re.search(r'\s(\w+)', str(src[n]))
                enzyme = re.search(r'.*?([A-Z]+).*?([A-Z]+)', str(src[n+1]),
                                   re.DOTALL)

                if name.group(1) in enzlist: continue
                else:
                    enzlist.append(str(name.group(1)))
                    self.database(name=str(name.group(1)),frontsite=str(enzyme.group(1)),backsite=str(enzyme.group(2))).put()

            except IndexError:
                continue

        return("completed")