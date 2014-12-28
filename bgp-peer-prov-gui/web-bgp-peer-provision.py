#!/usr/bin/env python
# -*- coding: utf-8 -*-
import cgi
import cgitb
import MySQLdb as mdb
import sys
from jnpr.junos.utils.config import Config
from jnpr.junos import Device
from jnpr.junos.exception import *
import getpass
from lxml import etree

#IP address validation
#Provided by http://bytes.com/topic/python/answers/569207-how-validate-ip-address-python
def ipFormatChk(ip_str):
    if len(ip_str.split()) == 1:
        ipList = ip_str.split('.')
        if len(ipList) == 4:
            for i, item in enumerate(ipList):
                try:
                    ipList[i] = int(item)
                except:
                    return False
                if not isinstance(ipList[i], int):
                    return False
            if max(ipList) < 256:
                return True
            else:
                return False
        else:
            return False
    else:
        return False


print "Content-type: text/html\n\n"
form=cgi.FieldStorage()
cgitb.enable()

#Populate Variables from web form. These help build SQL query
router_name=form["router"].value
ipv4=form["ipv4"].value
ipv6=form["ipv6"].value
asn=form["asn"].value
peer_name=form["peer_name"].value
pl4=form["pl4"].value
pl6=form["pl6"].value
username=form["username"].value
password=form["password"].value


#check user input is valid
print "Cehcking syntax on input..<br>"
#ipv4 address check
if ipFormatChk(ipv4):
    print "ipv4 address is valid<br>"
else:
    print "<b>Invalid IP address. Please go back and enter a valid IP address</b>"
    sys.exit()

#check that ASN is number:
try:
    isnumber = int(asn)
    print "ASN is valid<br>"
except ValueError:
    print "<b>ASN is not an integer. Pleaase go back and enter valid ASN.</b>"
    sys.exit()

#check that pl4 and pl6 are numbers:
try:
    isnumber = int(pl4)
    print "Prefix Limit for ipv4 is valid.<br>"
except ValueError:
    print "<b>prefix limit for ipv4 is not an integer. Pleaase go back and enter valid number.</b>"
    sys.exit()

try:
    isnumber = int(pl6)
    print "Prefix Limit for ipv6 is valid.<br>"
except ValueError:
    print "<b>prefix limit for ipv6 is not an integer. Pleaase go back and enter valid number.</b>"
    sys.exit()

#If all basic syntax checking passed with True we can continue.
#database connect to popululate dynamic naming conventions of peer
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

#These are pulled from the DB query and are completely dynamic based on peer. This is where the bulk of the dynamic DB data comes from.
v4_group_name = query[1]
v6_group_name = query[2]
as_path_name = query[3]


#Build Jinja2 dictionary that is processed.  This is taken from POST data from web form(above) or DB data(above)
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


'''
#connection to device.  Default will be 830
#much of this comes from the following sources:
#https://techwiki.juniper.net/Automation_Scripting/010_Getting_Started_and_Reference/Junos_PyEZ
#https://github.com/dhoutz/jnprPushCfg  This is a great source for a basic example
'''
dev = Device(router_name, user=username, password=password, port=22)
try:
	dev.open()
except Exception as err:
    if err.rsp.find('.//ok') is None:
        rpc_msg = err.rsp.findtext('.//error-message')
        print "Unable to open device: ", rpc_msg

#Bind config utility instance to device instance
dev.bind(cfg=Config)

#config lock the device
try:
	dev.cfg.lock()
except Exception as err:
    if err.rsp.find('.//ok') is None:
        rpc_msg = err.rsp.findtext('.//error-message')
        print "Unable to lock configuration: ", rpc_msg
        print "Please wait for other user to finish making changes"
        sys.exit()
#load configuration to device
try:
	dev.cfg.load(template_path='bgp-peer-template.set', template_vars=myvars)
except Exception as err:
    if err.rsp.find('.//ok') is None:
        rpc_msg = err.rsp.findtext('.//error-message')
        print "Unable to load configuration changes: ", rpc_msg

#commit check the changes and ask user if they want to commit.
#If prompted to commit we run commit.py against this from the submit button "commit"
try:
	commit_check = dev.cfg.commit_check()
except Exception as err:
    if err.rsp.find('.//ok') is None:
        rpc_msg = err.rsp.findtext('.//error-message')
        print "Unable to commit check configuration changes: ", rpc_msg
	sys.exit()

if commit_check is True:
	print "<pre>"
	print "Commit check completed. Diff of the changes is here"
	print "There should be no (-) in the config, only additions(+)"
	dev.cfg.pdiff()
    	print '<html>'
    	print 'Would you like to commit configuration?<br>'
    	print '<form action="/cgi-bin/commit.py" method="POST">'
        ###pass variables to commit.py...not sure if there is a better way to process these to another page without going dynamic with DB table of some kind.
        print '<input type="submit" value="Commit" />'
    	print '<input type="hidden" name="router_name" value="%s">' % router_name
        print '<input type="hidden" name="username" value="%s">' % username
        print '<input type="hidden" name="password" value="%s">' % password
        print '<input type="hidden" name="ipv4" value="%s">' % ipv4
        print '<input type="hidden" name="ipv6" value="%s">' % ipv6
        print '<input type="hidden" name="asn" value="%s">' % asn
        print '<input type="hidden" name="peer_name" value="%s">' % peer_name
        print '<input type="hidden" name="pl4" value="%s">' % pl4
        print '<input type="hidden" name="pl6" value="%s">' % pl6
    	print '</form>'
    	print '</html>'
    	print "</pre>"
#close connection
dev.close