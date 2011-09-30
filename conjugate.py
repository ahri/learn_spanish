#!/usr/bin/env python
# coding: utf-8
import sqlite3
import re
conn = sqlite3.connect('spanish.db')

query = """
  SELECT spanish, english
    FROM regular_verbs
ORDER BY RANDOM()
   LIMIT 1
"""

regverb_matcher = re.compile(r'^(.+)([aei]r)$')

conv = dict(ar=dict(fps=u"o",    # first person singular (i)
                    tps=u"as",   # third person singular (you)
                    sps=u"a",    # second person singular (he/she)
                    fpp=u"amos", # first person plural (we)
                    tpp=u"áis",  # third person plural (they)
                    spp=u"an",), # second person plural (you)
            er=dict(fps=u"es",
                    tps=u"e",
                    sps=u"o",
                    fpp=u"emos",
                    tpp=u"eís",
                    spp=u"en",),
            ir=dict(fps=u"o",
                    tps=u"es",
                    sps=u"e",
                    fpp=u"imos",
                    tpp=u"íes",
                    spp=u"en",))

for es, en in conn.execute(query):
    res = regverb_matcher.match(es)
    base = res.group(1)
    ending = conv[res.group(2)]
    print " === %s - %s ===" % (es, en)
    print "Yo %s%s" % (base, ending['fps'])
    print "Tu %s%s" % (base, ending['tps'])
    print "El/Ella/Usted %s%s" % (base, ending['sps'])
    print "Nosotros/as %s%s" % (base, ending['fpp'])
    print "Vosotros/as %s%s" % (base, ending['tpp'])
    print "Ellos/Ellas/Ustedes %s%s" % (base, ending['spp'])
