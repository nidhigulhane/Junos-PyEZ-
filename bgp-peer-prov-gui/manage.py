#!/usr/bin/env python
# -*- coding: utf-8 -*-
#This page is used for managing database entries via the WEBUI.
import cgi
import cgitb
import MySQLdb as mdb
import sys
form=cgi.FieldStorage()
cgitb.enable()


try:
    con = mdb.connect('localhost', 'db_user', 'db_password', 'routers');
    cur = con.cursor()
    cur.execute("SELECT * FROM router_list")
except mdb.Error, e:
    print "Error %d: %s" % (e.args[0],e.args[1])
    sys.exit(1)

finally:
    if con:
 		con.close()



#Begin HTML data form.
print "Content-type: text/html\n\n"
print "<html>"
print "<b> BGP Peering point peer builder - Management page</b><br>" 


#Output all current records
print "<h1>Current Records in Database</h1>"
print "<br>"
print "<table border=\"1\">"
print "<tr>"
print "<th>Router ID</th>"
print "<th>v4 group name</th>"
print "<th>v6 group name</th>"
print "<th>as-path name</th>"
print "<th>Router name</th>"
print "</tr>"
for ROW in cur.fetchall():
    print "<tr>"
    print "<td>%s</td>" % ROW[0]
    print "<td>%s</td>" % ROW[1]
    print "<td>%s</td>" % ROW[2]
    print "<td>%s</td>" % ROW[3]
    print "<td>%s</td>" % ROW[4]
    print "</tr>"
print "</table>"
print "<br>"


#Add  a new record section
#POSTS into add-bgp-peer-record.py
print "<h1>Add new record</h1>"
print "<form action=\"/cgi-bin/add-bgp-peer-record.py\" method=\"POST\">"
print "v4 Group Name: <input type=\"text\" size=\"20\" name=\"v4_group_name\" value=\"\"><br>"
print "v6 Group Name: <input type=\"text\" size=\"20\" name=\"v6_group_name\" value=\"\"><br>"
print "AS Path Name: <input type=\"text\" size=\"20\" name=\"as_path_name\" value=\"\"><br>"
print "Router Name: <input type=\"text\" size=\"20\" name=\"router_name\" value=\"\"><br>"
print "<input type=\"submit\" value=\"Add\">" 
print "</form>"


#delete a record section
#POSTS into delete-bgp-peer-record.py
print "<h1>Delete record. Specify router ID</h1>"
print "<form action=\"/cgi-bin/delete-bgp-peer-record.py\" method=\"POST\">"
print "Router ID to remove: <input type=\"text\" size=\"20\" name=\"router_id\" value=\"\"><br>"
print "<input type=\"submit\" value=\"Delete\">" 
print "</form>"
