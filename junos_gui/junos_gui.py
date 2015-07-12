#!/usr/bin/python
from flask import Flask, session, redirect, request, url_for, render_template
from flask_bootstrap import Bootstrap
import lxml
from config import *
from jnpr.junos import Device
from jnpr.junos.utils.config import Config
from jnpr.junos.exception import *


app = Flask(__name__)

'''get list of devices'''
def get_devices():
	#this comes from the configuration py script. This is here for future use
	return devices

'''device facts'''
def device_facts(device):
	dev = Device(host=device, user=username, password=password)
	dev.open()
	facts = dev.facts
	dev.close()
	return facts

'''run opeartional command'''
def operation_command(device,command):
	dev = Device(host=device, user=username, password=password)
	dev.open()
	output = dev.cli(command)
	dev.close
	return output

'''commit check'''
def commit_check(device, config_text):
		dev = Device(host=device, user=username, password=password)
		dev.open()
		dev.bind(cfg=Config)
		try:
			dev.cfg.load(config_text, format="set", merge=True)
		except Exception as err:
		    if err.rsp.find('.//ok') is None:
		        rpc_msg = err.rsp.findtext('.//error-message')
		        return "Error:", rpc_msg			
		config_diff = dev.cfg.diff()
		dev.cfg.rollback()
		dev.close()
		return config_diff


'''commit config'''
def commit_config(device, config_text):
		dev = Device(host=device, user=username, password=password)
		dev.open()
		dev.bind(cfg=Config)
		try:
			dev.cfg.load(config_text, format="set", merge=True)
		except Exception as err:
		    if err.rsp.find('.//ok') is None:
		        rpc_msg = err.rsp.findtext('.//error-message')
		        return "Error:", rpc_msg			
		dev.cfg.commit()
		dev.close()
		return


'''index page'''
@app.route('/', methods=['GET'])
def index():
	return render_template("index.html", devices=get_devices())

@app.route('/', methods=['POST'])
def select_device():
	device = request.form['device']
	session['device'] = device
	return render_template("index.html", devices=get_devices())

'''hostname change '''
@app.route('/hostname', methods=['GET'])
def hostname_form():
	device = session.get('device', None)
	dev = device_facts(device)
	hostname = dev['hostname']
	return render_template("hostname_form.html", hostname=hostname)

@app.route('/hostname', methods=['POST'])
def hostname_commit():
	if 'commit' in request.form:
		config_text = session.get('config_text', None)
		device = session.get('device', None)
		commit_config(device, config_text)
		return redirect(url_for('hostname_form'))
	elif 'submit' in request.form:
		hostname = request.form['hostname']
		config_text = "set system host-name %s" %(hostname)
		device = session.get('device', None)
		config_diff = commit_check(device, config_text)
		session['config_text'] = config_text
		return render_template("hostname_commit.html", config_diff=config_diff)



'''BGP neighbor add'''
@app.route('/bgp', methods=['GET'])
def bgp_form():
	device = session.get('device', None)
	dev = Device(host=device, user=username, password=password)
	dev.open()
	bgp = dev.rpc.get_bgp_neighbor_information()
	neighbors = bgp.findall('bgp-peer')
	bgp_peers = {}
	for neighbor in neighbors:
		bgp_peers[neighbor.find("peer-address").text] = neighbor.find('peer-state').text
	dev.close()
	return render_template("bgp_form.html", bgp_peers=bgp_peers)

@app.route('/bgp', methods=['POST'])
def bgp_submit():
	if 'commit' in request.form:
		config_text = session.get('config_text', None)
		device = session.get('device', None)
		commit_config(device, config_text)
		return redirect(url_for('bgp_form'))
	elif 'submit' in request.form:
		bgp_peer_ipv4 = request.form['bgp_peer_ipv4']
		bgp_peer_asn = request.form['bgp_peer_asn']
		config_text = "set protocols bgp group external-peers type external neighbor %s peer-as %s" %(bgp_peer_ipv4, bgp_peer_asn)
		device = session.get('device', None)
		config_diff = commit_check(device, config_text)
		session['config_text'] = config_text
		return render_template("bgp_commit.html", config_diff=config_diff)
	elif 'delete' in request.form:
		bgp_peer_ipv4 = request.form['bgp_peer_ipv4']
		config_text = "delete protocols bgp group external-peers neighbor %s" %(bgp_peer_ipv4)
		device = session.get('device', None)
		config_diff = commit_check(device, config_text)
		session['config_text'] = config_text
		return render_template("bgp_commit.html", config_diff=config_diff)

'''raw command sender'''
@app.route('/commander', methods=['GET'])
def commander_form():
	return render_template("commander_form.html")

@app.route('/commander', methods=['POST'])
def commander_diff():
	if 'commit' in request.form:
		config_text = session.get('config_text', None)
		device = session.get('device', None)
		commit_config(device, config_text)
		return redirect(url_for('commander_form'))
	elif 'submit' in request.form:
		config_text = request.form['commands']
		device = session.get('device', None)
		config_diff = commit_check(device, config_text)
		if "Error:" in config_diff:
			return "encountered error. Please return to main page: " + str(config_diff)
		session['config_text'] = config_text
		return render_template("commander_diff.html", config_diff=config_diff)

'''show commands helper'''
@app.route('/show', methods=['GET'])
def show_form():
	return render_template("show_form.html")

@app.route('/show', methods=['POST'])
def show_output():
		config_text = request.form['command']
		device = session.get('device', None)
		output = operation_command(device, config_text)
		return render_template("show_form.html", output=output, config_text=config_text)


'''devices page'''
@app.route('/device', methods=['GET'])
def device_management():
	return render_template("device.html", devices=get_devices())

'''clear'''
@app.route("/clear")
def clear():
    session.clear()
    return redirect(url_for("index"))

if __name__ == '__main__':
	app.secret_key = secret_key
	Bootstrap(app)
	app.run(host='0.0.0.0', debug="True")