#!/usr/bin/env python
# -*- coding: utf-8 -*-
import cgi
import cgitb
import MySQLdb as mdb
import sys

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



#Begin HTML data form. First box uses our BGP query and builds dropdown from current DB entries
print "Content-type: text/html\n\n"
print "<html>"
print "<b> BGP Peering point peer builder</b><br>" 
print "Please select a peering point you would like to provision and populate text fields<br>"
print "<br>"
print "<form action=\"/cgi-bin/web-bgp-peer-provision.py\" method=\"POST\">"
print "Peering point router"
print "<select name=\"router\">"
print "<option value=\"\"></option>"
#loads the DB rows into the dropdown
for ROW in cur.fetchall():   
    print "<option value=%s>%s</option>" % (ROW[4], ROW[4])
print "</select><br>"
print "ipv4 IP address of peer: <input type=\"text\" size=\"20\" name=\"ipv4\" value=\"\"><br>"
print "ipv6 IP address of peer: <input type=\"text\" size=\"20\" name=\"ipv6\" value=\"\"><br>"
print "Peer ASN: <input type=\"text\" size=\"20\" name=\"asn\" value=\"\"><br>"
print "Peer Descriptive name: <input type=\"text\" size=\"20\" name=\"peer_name\" value=\"\"><br>"
print "Prefix Limit for ipv4 prefixes: <input type=\"text\" size=\"20\" name=\"pl4\" value=\"\"><br>"
print "Prefix Limit for ipv6 prefixes: <input type=\"text\" size=\"20\" name=\"pl6\" value=\"\"><br>"
print "NetConf username: <input type=\"text\" size=\"20\" name=\"username\" value=\"\"><br>"
print "NetConf password: <input type=\"password\" size=\"20\" name=\"password\" value=\"\"><br>"
print "<br>Click Submit to see a configuration change diff. From there you can commit configuration<br>"
print "<input type=\"submit\" value=\"Submit\">" 
print "<input type=\"reset\" value=\"Reset\">"
print "</form>"
print "<h1> Management page:</h1>"
print "<a href=\"manage.py\">Management page</a>"
print "</html>"