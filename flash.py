#!/usr/bin/env python
# coding: utf-8
import sqlite3
import random

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

def pick():
    pick = random.randint(0, SELECTION_COUNT-1)
    opts = []
    verb = None
    for i, (es, en) in enumerate(conn.execute(query, (SELECTION_COUNT,))):
        if i == pick:
            verb = es
            print " === %s ===" % verb

        opts.append(en)

    print "Options:"
    for i, en in enumerate(opts):
        print "%d: %s" % (i+1, en)

    return pick, verb

def get_int(prompt="? ", minimum=None, maximum=None):
    choice = None
    while choice == None:
        try:
            choice = int(raw_input("Choice: "))
        except ValueError:
            pass

        if minimum is not None and choice < minimum:
            choice = None
            print "Please choose a number >= %d" % minimum

        if minimum is not None and choice > maximum:
            choice = None
            print "Please choose a number <= %d" % maximum

    return choice

def guess():
    choice = get_int("Choice: ", minimum=1, maximum=SELECTION_COUNT)
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
        increment_count(verb, 'right')
        print "You're right!"
    else:
        increment_count(verb, 'wrong')
        print "You're wrong :("

conn.close()
