#!/usr/bin/env python
# coding: utf-8
import sqlite3
import random
import sys

conn = sqlite3.connect('results.db')

SELECTION_COUNT = 5

conn.execute("""
CREATE TABLE IF NOT EXISTS verbs (
    verb VARCHAR(20) PRIMARY KEY,
    right INTEGER DEFAULT 0,
    wrong INTEGER DEFAULT 0
)""")
conn.execute("ATTACH DATABASE 'spanish.db' AS spanish")
conn.commit()

query = """
  SELECT spanish, english
    FROM spanish.verbs
ORDER BY RANDOM()
   LIMIT ?
"""

# well known: total > MINIMUM_CORRECT and proportion correct > PROPORTION_KNOWN

MINIMUM_CORRECT = 3
PROPORTION_KNOWN = 0.9

query_revise = """
   SELECT v.spanish, v.english
     FROM spanish.verbs v
LEFT JOIN verbs r
       ON v.spanish = r.verb
    WHERE r.right IS NOT NULL
      AND r.right+r.wrong > %(minimum_correct)d
      AND r.right/(r.right+r.wrong) > %(proportion_known)f
 ORDER BY RANDOM()
    LIMIT ?
""" % dict(minimum_correct=MINIMUM_CORRECT,
           proportion_known=PROPORTION_KNOWN)

query_learn = """
   SELECT v.spanish, v.english
     FROM spanish.verbs v
LEFT JOIN verbs r
       ON v.spanish = r.verb
    WHERE r.right IS NULL
       OR r.right+r.wrong <= %(minimum_correct)d
       OR r.right/(r.right+r.wrong) <= %(proportion_known)f
 ORDER BY RANDOM()
    LIMIT ?
""" % dict(minimum_correct=MINIMUM_CORRECT,
           proportion_known=PROPORTION_KNOWN)

if len(sys.argv) > 1 and sys.argv[1] == 'revise':
    print " [Revision mode]"
    query = query_revise
else:
    print " [Learning mode]"
    query = query_learn


def pick():
    pick = random.randint(0, SELECTION_COUNT-1)
    opts = []
    verb = None
    for i, (es, en) in enumerate(conn.execute(query_learn, (SELECTION_COUNT,))):
        if i == pick:
            verb = es
            print " === %s ===" % verb

        opts.append(en)

    print "Options:"
    for i, en in enumerate(opts):
        print "%d: %s" % (i+1, en)

    return pick, verb

def get_bool(prompt="?", default=None):
    if default is not None:
        prompt += " [%s]" % default
    while True:
        choice = raw_input(prompt+' ')
        if choice in ('y', 'Y') or default in ('y', 'Y'):
            return True
        elif choice in ('n', 'N') or default in ('n', 'N'):
            return False

        print "Input y/n"

def get_int(prompt="?", minimum=None, maximum=None):
    while True:
        try:
            choice = int(raw_input(prompt+' '))
        except ValueError:
            choice = None

        if minimum is not None and choice < minimum:
            print "Please choose a number >= %d" % minimum

        elif minimum is not None and choice > maximum:
            print "Please choose a number <= %d" % maximum

        else:
            break

    return choice

def guess():
    choice = get_int("Choice:", minimum=1, maximum=SELECTION_COUNT)
    return choice - 1

pick, verb = pick()

def increment_count(verb, column):
    try:
        conn.execute("""INSERT INTO verbs (verb,
                                           %(column)s)
                             VALUES (?, 1)""" % dict(column=column),
                     (verb,))
    except sqlite3.IntegrityError:
        conn.execute("""UPDATE verbs
                           SET %(column)s = %(column)s + 1
                         WHERE verb = ?""" % dict(column=column),
                     (verb,))
    finally:
        conn.commit()

result = False
wrong = 0
while not result:
    choice = guess()
    if choice == pick:
        result = True
        print "You're right!"
        if not get_bool("Did you just guess?", default='n'):
            print "Recording result..."
            increment_count(verb, 'right')
    else:
        increment_count(verb, 'wrong')
        print "You're wrong :("

conn.close()
