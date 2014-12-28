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
router_name=form["router_name"].value
v4_group_name=form["v4_group_name"].value
v6_group_name=form["v6_group_name"].value
as_path_name=form["as_path_name"].value

#SQL query from POST data variables
query = """INSERT INTO router_list VALUES (NULL,"%s","%s","%s","%s")""" % (v4_group_name, v6_group_name, as_path_name, router_name)
try:
    con = mdb.connect('localhost', 'database_user', 'database_password', 'routers');
    cur = con.cursor()
    cur.execute(query)
    con.commit()
    print "<b>record added</b>"
except mdb.Error, e:
    print "Error %d: %s" % (e.args[0],e.args[1])
    sys.exit(1)

finally:
    if con:
 		con.close()