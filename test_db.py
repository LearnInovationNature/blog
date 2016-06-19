#! /usr/bin/python
# -*- coding: utf-8 -*-
from flaskr import *
db = connect_db()
db.execute ("insert into entries (title, text) values('good1', 'bad2')")
db.commit()
cur = db.execute("select * from entries")
for row in cur.fetchall():
    print (row)

cur.close()
db.close()
