#!/usr/bin/env python
# -*- coding: utf-8 -*-
#most of this code is a duplicate of web-bgp-peer-provision.py..only major difference is the commit vs the pdff(printed diff)
import cgi
import cgitb
import MySQLdb as mdb
import sys
from jnpr.junos.utils.config import Config
from jnpr.junos import Device
from jnpr.junos.exception import *
import getpass
from lxml import etree

print "Content-type: text/html\n\n"
form=cgi.FieldStorage()
cgitb.enable()

#Populate form contents to variables
router_name=form["router_name"].value
ipv4=form["ipv4"].value
ipv6=form["ipv6"].value
asn=form["asn"].value
peer_name=form["peer_name"].value
pl4=form["pl4"].value
pl6=form["pl6"].value
username=form["username"].value
password=form["password"].value



try:
    con = mdb.connect('localhost', 'db_user', 'db_password', 'routers');
    cur = con.cursor()
    cur.execute("SELECT * FROM router_list WHERE router_name  = %s", (router_name))
    query = cur.fetchone()

except mdb.Error, e:

    print "Error %d: %s" % (e.args[0],e.args[1])
    sys.exit(1)

finally:
    if con:
 		con.close()

#populate DB variable names(these are dynamic based on form input)
v4_group_name = query[1]
v6_group_name = query[2]
as_path_name = query[3]


#populate myvars from information above
myvars = {}
myvars['ipv4'] = ipv4
myvars['asn'] = asn
myvars['ipv6'] = ipv6
myvars['pl4'] = pl4
myvars['pl6'] = pl6
myvars['v4_group_name'] = v4_group_name
myvars['v6_group_name'] = v6_group_name
myvars['as_path_name'] = as_path_name
myvars['name'] = peer_name


#connection to device.  Default will be 830
dev = Device(router_name, user=username, password=password, port=22)
try:
	dev.open()
except Exception as err:
    if err.rsp.find('.//ok') is None:
        rpc_msg = err.rsp.findtext('.//error-message')
        print "Unable to open device: ", rpc_msg
#Bind config utility instance to device
dev.bind(cfg=Config)

#config lock the device
try:
	dev.cfg.lock()
except Exception as err:
    if err.rsp.find('.//ok') is None:
        rpc_msg = err.rsp.findtext('.//error-message')
        print "Unable to lock configuration: ", rpc_msg

#load configuration to device
try:
	dev.cfg.load(template_path='bgp-peer-template.set', template_vars=myvars)
except Exception as err:
    if err.rsp.find('.//ok') is None:
        rpc_msg = err.rsp.findtext('.//error-message')
        print "Unable to load configuration changes: ", rpc_msg

#commit check the changes and ask user if they want to commit
try:
	commit_check = dev.cfg.commit_check()
except Exception as err:
    if err.rsp.find('.//ok') is None:
        rpc_msg = err.rsp.findtext('.//error-message')
        print "Unable to commit check configuration changes: ", rpc_msg
	sys.exit()

if commit_check is True:
	print "<pre>"
	dev.cfg.commit()
	print '<html>'
	print "configuration commited successfully"
	print "</pre>"
#close connection
#dev.close