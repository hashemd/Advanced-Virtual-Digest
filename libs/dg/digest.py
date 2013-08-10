"""
Released under the MIT License
Copyright (c) 2013 Hashem Al-Dujaili
"""

import re
# from google.appengine.ext import ndb


class Digest():
    """
    Takes input as ndb.database (elements of name, frontsite and backsite),
    sequence (FASTA ok).
    """

    def __init__(self, database, sequence, shape):

        self.database = database
        self.shape = shape
        self.sequence = sequence
        self.sequence = str(self.sequence).lower()
        self.sequence = re.sub(r'[\W\d\s\n]+', '', self.sequence)

    def multi_digest(self, enzymes):

        bases = []
        frags = []
        tmp = self.sequence
        if isinstance(enzymes, basestring):
            enzymes = [enzymes]

        for enzyme in enzymes:

            enz = self.database.query(self.database.name == enzyme).get()
            frontsite = enz.frontsite.lower()
            frontsite = re.sub(r'[\W\d\s\n]+', '', frontsite)
            backsite = enz.backsite.lower()
            backsite = re.sub(r'[\W\d\s\n]+', '', backsite)

            res_site = frontsite + backsite
            res_site = re.sub('r', '[ag]', res_site)
            res_site = re.sub('y', '[ct]', res_site)
            res_site = re.sub('k', '[gt]', res_site)
            res_site = re.sub('m', '[ac]', res_site)
            res_site = re.sub('n', '[gtac]', res_site)

            for match in re.finditer(res_site, tmp):

                bases.append([match.start(), len(frontsite)])

            if len(bases) == 0:
                return -1  # Does not cut

        bases = sorted(bases, key=lambda x: x[0])

        n = 0
        for base in bases:
            frags.append([tmp[n:base[0] + base[1]],
                         str(len(tmp[n:base[0] + base[1]]))])
            n = base[0] + base[1]
        frags.append([tmp[n:], str(len(tmp[n:]))])

        if frags[0][0] == '':
            frags.pop(0)
        if self.shape == 'Circular':
                frags[0][1] = str(int(frags[0][1]) + int(frags[-1][1]))
                frags[0][0] = (frags[-1][0] + frags[0][0])
                frags.pop()

        return frags  # return [(fragment,length)]

    def linearize(self):

        linenz = []
        qry = self.database.query()
        listenz = qry.fetch()
        for n in range(0, len(listenz), 1):
            subseq = listenz[n].frontsite.lower() + listenz[n].backsite.lower()

            if len(re.findall(subseq, self.sequence)) == 1:
                linenz.append((listenz[n].name, str(self.sequence.find(subseq)
                              + len(listenz[n].frontsite))))
            else:
                continue

        return linenz
        # Returns a list of tuples in the format (Enzyme name, Site of cut)

    def insert(self, first_site, second_site, vector,
               vector_database, sites_database=None):

        query = vector_database.query(vector_database.name == vector).get()
        vec_seq = query.sequence
        vec_seq = vec_seq.lower()
        vec_seq = re.sub('\n', '', vec_seq)
        ins_seq = self.sequence

        query = self.database.query(self.database.name == first_site).get()
        if query is None:
            if sites_database is None:
                return -2
            query = sites_database.query(sites_database.name
                                         == first_site).get()
            if query is None:
                return -2
            else:
                fs = query.sequence.lower()

        else:
            fs = query.frontsite.lower() + query.backsite.lower()

        query = self.database.query(self.database.name == second_site).get()
        if query is None:
            if sites_database is None:
                return -2
            query = sites_database.query(self.database.name
                                         == second_site).get()
            if query is None:
                return -2
            else:
                ss = query.sequence.lower()

        else:
            ss = query.frontsite.lower() + query.backsite.lower()

        x = vec_seq.find(fs)
        y = vec_seq.find(ss)

        inserted = vec_seq[:x] + ins_seq + vec_seq[y + len(ss):]
        return inserted

    def rem_insert(self, first_site, second_site, vector, vector_database,
                   sites_database=None, min_distance=300):
     #Sites database is optional, use only if non enzyme sites are included.

        self.shape = 'linear'
        query = vector_database.query(vector_database.name == vector).get()
        vec_seq = query.sequence
        vec_seq = vec_seq.lower()
        vec_seq = re.sub('\n', '', vec_seq)
        ins_seq = self.sequence
        first_enz = []
        second_enz = []
        both_enz = []

        query = self.database.query(self.database.name == first_site).get()
        if query is None:
            if sites_database is None:
                return -2

            query = sites_database.query(sites_database.name
                                         == first_site).get()
            if query is None:
                return -2

            else:
                fs = query.sequence.lower()

        else:
            fs = query.frontsite.lower() + query.backsite.lower()

        query = self.database.query(self.database.name == second_site).get()
        if query is None:

            if sites_database is None:
                return -2
            query = sites_database.query(self.database.name ==
                                         second_site).get()

            if query is None:
                return -2

            else:
                ss = query.sequence.lower()

        else:
            ss = query.frontsite.lower() + query.backsite.lower()

        x = vec_seq.find(fs)
        y = vec_seq.find(ss)
        if (x == -1 or y == -1):
            return -1

        five_seq = vec_seq[:x]
        three_seq = vec_seq[y + len(ss):]
        qry = self.database.query()
        listenz = qry.fetch(projection=[self.database.name])

        for n in range(0, len(listenz), 1):
            self.sequence = ins_seq

            if self.multi_digest(listenz[n].name) == -1:

                self.sequence = five_seq
                x = self.multi_digest(listenz[n].name)

                if not x == -1:

                    self.sequence = three_seq
                    y = self.multi_digest(listenz[n].name)

                    if not y == -1:
                        too_short = False
                        if isinstance(x[0][1], basestring):
                            x[0][1] = [x[0][1]]
                        if isinstance(y[0][1], basestring):
                            y[0][1] = [y[0][1]]
                        adj_frag = [x[0][1].pop() + y[0][1].pop(0)]
                        frags = x[0][1] + y[0][1]
                        if len(frags) < 1:
                            continue
                        frags[0] = frags[-1] + frags[0]

                        frags.pop()
                        side_product = []
                        for frag in frags:
                            if (-min_distance < (frag - len(ins_seq))
                                    < min_distance):
                                too_short = True
                                break
                            side_product.append(frag)

                        if too_short is False:
                            both_enz.append((listenz[n].name, side_product,
                                             adj_frag))
                        continue

                    first_enz.append(listenz[n].name)
                else:
                    self.sequence = three_seq
                    x = self.multi_digest(listenz[n].name)
                    if x == -1 is False:
                        second_enz.append(listenz[n].name)

        #Ordered by shortest (insert + adjacent fragments) length

        both_enz = sorted(both_enz, key=lambda x: (x[2][0]))
        first_enz = sorted(first_enz, key=lambda x: (x[1][0]))
        second_enz = sorted(second_enz, key=lambda x: (x[1][0]))

        return (both_enz, first_enz, second_enz)

    def enzyme_map(self):

        qry = self.database.query()
        strenz = []
        listenz = qry.fetch(projection=[self.database.name])
        for n in range(0, len(listenz), 1):
            x = self.multi_digest([listenz[n].name])

            if not (x == -1):
                tmp = []
                for lengths in x:

                    tmp.append(int(lengths[1]))

                order = sorted(tmp, reverse=True)

                strenz.append([listenz[n].name, order])
                continue

        strenz = sorted(strenz, key=lambda x: len(x[1]), reverse=True)
        return strenz  # Returns a list of list[enzyme and frag lengths]
        # sorted by reverse number of frags.


def main():
    print "This module cannot be executed directly."


if __name__ == '__main__':
    main()
