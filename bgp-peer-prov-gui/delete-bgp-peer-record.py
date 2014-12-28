#!/usr/bin/env python
# -*- coding: utf-8 -*-
import cgi
import cgitb
import MySQLdb as mdb
import sys
form=cgi.FieldStorage()
cgitb.enable()

print "Content-type: text/html\n\n"
#Obtain information needed from POST to insert into database
#Populate Variables from web form. These help build SQL query
router_id=form["router_id"].value
#SQL query from POST data variables
query = """DELETE FROM router_list WHERE router_id  = %s""" % router_id
try:
    con = mdb.connect('localhost', 'database_user', 'database_password', 'routers');
    cur = con.cursor()
    cur.execute(query)
    con.commit()
    print "<b>record deleted</b>"
except mdb.Error, e:
    print "Error %d: %s" % (e.args[0],e.args[1])
    sys.exit(1)

finally:
    if con:
 		con.close()