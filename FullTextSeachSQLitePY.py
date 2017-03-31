# -*- encoding: utf-8 -*-
# Made by http://www.elmalabarista.com
# This will teach about how use the sqlite full text search
# abilities from python

# About

# You have a app used by users? Wanna a good search functionality?
# Then implement full text search (FTS). Is easy with sqlite, perform well
# and give good results. PostgreSQL is another database with good
# FTS functionality

# Official docs
# http://www.sqlite.org/fts3.html

# Usefull links
# https://en.wikipedia.org/wiki/Full_text_search
# http://docs.python.org/2/library/sqlite3.html

# Other FTS libraries, independent of the database engine
# http://pythonhosted.org/Whoosh/
# http://lucene.apache.org/core/
# http://sphinxsearch.com/

import collections
import datetime
import sqlite3


from utils import printTitle, printSubTitle, printExplain, printTab, printError

printTitle("You need to provide search functionality")
print """
Your app/web site need a way to give search results, fast & easy
"""

printSubTitle("First, we need a database")
# This will run in the memory
conn = sqlite3.connect(':memory:')
conn.row_factory = sqlite3.Row


def exeSql(sql):
    c = conn.cursor()
    c.execute(sql)
    conn.commit()


def selectSql(sql, params=None):
    c = conn.cursor()
    if params:
        c.execute(sql, params)
    else:
        c.execute(sql)

    return c.fetchall()


SQL_SCHEMA = """
CREATE TABLE Persons(
    Id INTEGER PRIMARY KEY AUTOINCREMENT,
    FullName VARCHAR,
    City VARCHAR,
    Country VARCHAR,
    Phone VARCHAR,
    Street VARCHAR,
    Email VARCHAR,
    CreatedAt datetime
);
"""

SQL_INSERT = """
INSERT INTO Persons
    (City,Country,Phone,FullName,Id,Street,Email,CreatedAt)
VALUES
    (:City,:Country,:Phone,:FullName,:Id,:Street,:Email,:CreatedAt)
"""

print SQL_SCHEMA
exeSql(SQL_SCHEMA)

from sampledata import PERSONS
# Some data for testing
# Generated from http://www.databasetestdata.com/


def readCsv(csv_data):
    # A simple utily to read a CSV-like data as namedtuples
    # Note the use of generator, to avoid build all in memory
    Row = None
    for line in csv_data.splitlines():
        if Row:
            yield Row._make(line.split(u','))
        else:
            header = line.split(u',')
            Row = collections.namedtuple("Row", [x.replace(u' ', u'') for x in header])


printExplain("Importing 1000 records..")
cur = conn.cursor()
cur.executemany(SQL_INSERT, readCsv(PERSONS))
print "Done!"

printExplain("Using LIKE is not enough")
print """
Is possible to perform queries with the LIKE keyword. However, the user interface
regulary is complicated with several boxes that restrict the fields/tables to search,
and is probably necesary to concatenate the fields to search and the query probably will
perform worse with LIKE than with direct comparision keywords like =, <, >.

For example, to search name & city that could start with 'Ad', like in a auto-complete box
"""

printExplain("Regular LIKE search")

SEARCH_LIKE = """
SELECT FullName, City FROM Persons WHERE FullName LIKE :FullName OR City LIKE :City
ORDER BY FullName
"""

print SEARCH_LIKE

for row in selectSql(SEARCH_LIKE, dict(FullName='Ad%', City='Ad%')):
    print row

printTitle("Installing the FTS support")

printExplain("Sqlite have 2 extensions for FTS: FTS3 & FTS4")
# See http://www.sqlite.org/fts3.html#section_1_1 for the differences
print "We will use FTS4"

printExplain("You need to create a VIRTUAL TABLE and set the kind of FTS implementation")

SQL_FTS = """
CREATE VIRTUAL TABLE Persons_index USING fts4(personId INT, content);
"""

print SQL_FTS

printExplain("You need at least 1 field to store the data, and put any other field you need for JOINS")

exeSql(SQL_FTS)

printExplain("You need to populate the virtual table with INSERTS from the table(s) that are part of the index")

print "Inserting the data..."

SQL_POPULATEINDEX = """
INSERT INTO Persons_index (personId, content)
SELECT Id, FullName || ' ' || City || ' ' || Country || ' ' || Street
    FROM Persons
"""

printExplain("Note how I concatenate the fields with a space")

print SQL_POPULATEINDEX
exeSql(SQL_POPULATEINDEX)
print "Done.."

printExplain("To have the index up-to-date, use triggers")

printTitle("Searching with FTS")
printExplain("Search is very easy, instead of LIKE, use MATCH!")

SEARCH_FTS = """
SELECT FullName, City FROM Persons WHERE Id IN (
  SELECT personId FROM Persons_index WHERE content MATCH :Content
)
ORDER BY FullName
"""

print SEARCH_FTS
printSubTitle("Search results:")
# Because I add more fields to this, the results are different
for row in selectSql(SEARCH_FTS, dict(Content='Ad*')):
    print row


printExplain("Using FTS, is possible to do faster queries for things that are slow with LIKE")
print "For example, looking for a string in any position '*arden*'"

printSubTitle("Search results:")
# Note: Is case-insensitive!
for row in selectSql(SEARCH_FTS, dict(Content='arden')):
    print row

print "And for a phrase like 'Dillan King' in ANY part of the content"


printSubTitle("Search results:")
# Note: Is enclosed in ""
for row in selectSql(SEARCH_FTS, dict(Content='"Dillan King"')):
    print row

printSubTitle("SET operations")
printExplain("You can use OR, NOT like in a web search engine!")


printSubTitle("Search results AND:")
# Just separate the words with a space
for row in selectSql(SEARCH_FTS, dict(Content='King Neva')):
    print row

printSubTitle("Search results OR:")
for row in selectSql(SEARCH_FTS, dict(Content='Neva OR King')):
    print row

printSubTitle("Search results NOT:")
# Use the unary marked '-'
for row in selectSql(SEARCH_FTS, dict(Content='King -Neva')):
    print row

printTitle("Conclusion")
print """
Sqlite + FTS is a easy way to add rich search capabilities to
any app (web, mobile, desktop).

Beacuse is already integrate in the database itself, you not need a separate
server/library and different API, also, is more easy to mantain the index
up to date because the data is already in the database, and you can
mix & match regular SQL queries and FTS queries.

FTS is particulary usefull for end-users, because the experience is similar to
use a search engine like google.

Plus, FTS perform well for cases where the regular queries will need a full scan
to find the data.

Take in account the index is inside the database, and it increase the size of it.
"""
