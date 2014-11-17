#!/usr/bin/env python


__author__ = 'xsited'
import logging
import httplib
import json
import base64
import string
from urlparse import urlparse

toggle = 1
toggle_pcmm = 1
circuit_id = 1
# consider refectoring with request http://docs.python-requests.org/en/latest/index.html

class Error:
    # indicates an HTTP error
    def __init__(self, url, errcode, errmsg, headers):
        self.url = url
        self.errcode = errcode
        self.errmsg = errmsg
        self.headers = headers
    def __repr__(self):
        return (
            "<Error for %s: %s %s>" %
            (self.url, self.errcode, self.errmsg)
            )


class RestfulAPI(object):
    def __init__(self, server):
        self.server = server
        self.path = '/wm/staticflowentrypusher/json'
        self.auth = ''
        self.port = 8080

    def get_server(self):
        return self.server

    def set_server(self, server):
        self.server = server


    def set_path(self, path):
	#print path
        self.path = path

#    def set_path(self, path, port):
#        self.path = path
#        self.port = port

    def set_port(self, port):
	#print port
        self.port = port

    def use_creds(self):
    	u = self.auth is not None and len(self.auth) > 0
#    	p = self.password is not None and len(self.password) > 0
        return u

    def credentials(self, username, password):
        self.auth = base64.encodestring('%s:%s' % (username, password)).replace('\n', '')

    def get(self, data=''):
        ret = self.rest_call({}, 'GET')
        #return json.loads(ret[2])
        return ret

    def set(self, data):
        #ret = self.rest_call(data, 'PUT')
        ret = self.rest_call2(data, 'PUT')
	print ret[0], ret[1]
        # return ret[0] == 200
        return ret

    def post(self, data):
        ret = self.rest_call(data, 'POST')
        #ret = self.rest_call2(data, 'POST')
	print ret[0], ret[1]
	return ret

    def put(self, data):
        ret = self.rest_call(data, 'PUT')
        return ret
        #return ret[0] == 200


    def remove(self, objtype, data):
        ret = self.rest_call(data, 'DELETE')
        #return ret[0] == 200
        return ret

    def delete(self):
        ret = self.rest_call({}, 'DELETE')
        #return ret[0] == 200
        return ret

    def show(self, data):
	print ""
	print json.dumps(data, indent=4, sort_keys=True)
#       print 'DATA:', repr(data)
#
#	print ""
#       data_string = json.dumps(data)
#       print 'JSON:', data_string
#
#	print ""
#       data_string = json.dumps(data)
#       print 'ENCODED:', data_string
#
#	print ""
#       decoded = json.loads(data_string)
#       print 'DECODED:', decoded


    def rest_call2(self, data, action):

        #conn = httplib.HTTPConnection(self.server, self.port)
        conn = httplib.HTTP(self.server, self.port)
        conn.putrequest(action, self.path)
	conn.putheader("Host", self.server+':%s'%self.port)
 	conn.putheader("User-Agent", "Python HTTP Auth")
        conn.putheader('Content-type', 'application/json')
        body = json.dumps(data)
	#conn.putheader("Content-length", "%d" % len(data))
	conn.putheader("Content-length", "%d" % len(body))
        if self.use_creds():
        #    print "using creds"
            conn.putheader("Authorization", "Basic %s" % self.auth)
        conn.endheaders()
	
        conn.send(body)
	errcode, errmsg, headers = conn.getreply()
	ret = (errcode, errmsg, headers)

        #if errcode != 201:
        #   raise Error(self.path, errcode, errmsg, headers)

        # get response
        #response = conn.getresponse()
	#headers = response.read()
        #ret = (response.status, response.reason, headers)
        #if response.status != 200:
        #    raise Error(self.path, response.status, response.reason, headers)
	return ret


    def rest_call(self, data, action):
        body = json.dumps(data)
	if self.use_creds():
	#    print "using creds"
            headers = {
                'Content-type': 'application/json',
                'Accept': 'application/json',
		'Content-length': "%d" % len(body),
	        'Authorization': "Basic %s" % self.auth,
                }
        else:
            headers = {
                'Content-type': 'application/json',
                'Accept': 'application/json',
		'Content-length': "%d" % len(body),
                }
		
	print self.server+':',self.port, self.path
        conn = httplib.HTTPConnection(self.server, self.port)
        conn.request(action, self.path, body, headers)
        response = conn.getresponse()
	data = response.read()
        ret = (response.status, response.reason, data)
        #print "status %d %s" % (response.status,response.reason)
        conn.close()
        return ret





class ODL(object):
    def __init__(self, ws):
        self.ws = ws
        self.ws.set_port(8080)

    def response_code_get(self, code):
	reponse_codes = {
	200:"Processed successfully",
	201:"Created successfully",
	204:"No content",
	400:"Bad request",
	401:"User not authorized to perform this operation",
	406:"Invalid operation. Failure details included in HTTP Error response",
	500:"Failure Reason included in HTTP Error response",
	503:"One or more of Controller service is unavailable",
	}
	return reponse_codes.get(code)


    def topology(self):
        self.ws.set_path('/controller/nb/v2/topology/default')
	self.ws.set_port(8080)	
        content = self.ws.get()
        j=json.loads(content[2])
        self.ws.show(j)


    def node_connections_get_all(self):
        self.ws.set_path('/controller/nb/v2/connectionmanager/nodes')
	self.ws.set_port(8080)	
        content = self.ws.get()
        j=json.loads(content[2])
        self.ws.show(j)

    def statistics_ports(self):
        self.ws.set_path('/controller/nb/v2/statistics/default/port')
	self.ws.set_port(8080)	
        content = self.ws.get()
        allPortStats = json.loads(content[2])
	# ws.show(allPortStats)
        portStats = allPortStats['portStatistics']
	# XXX - Array traversal missing last element?
        for po in portStats:
	    print "\nSwitch ID : " + po['node']['id'] +  " Type: " +  po['node']['type']
            for so in po['portStatistic']:
	       # ws.show( so )
	       nc = so['nodeConnector']
               print "\nPort : " + nc['id'] + " Type: " +  nc['type'] 
	       print "Connector Node : " + nc['node']['id'] +  " Type : " +  nc['node']['type']
               print "    Received Bytes  :        ", so['receiveBytes']
               print "    Received Packets:        ", so['receivePackets']
               print "    Received Drops:          ", so['receiveDrops']
               print "    Received Errors:         ", so['receiveErrors']
               print "    Received Frame Errors:   ", so['receiveFrameError']
               print "    Received Over Run Error: ", so['receiveOverRunError']
               print "    Received CRC Errors:     ", so['receiveCrcError']
               print "    Transmitted Packets:     ", so['transmitBytes']
               print "    Transmitted Errors:      ", so['transmitErrors']
               print "    Transmitted Drops:       ", so['transmitDrops']
               print "    Collision Count:         ", so['collisionCount']


    # adopted from fredhsu @ http://fredhsu.wordpress.com/2013/04/25/getting-started-with-opendaylight-and-python/
    def statistics_flows(self):
        self.ws.set_path('/controller/nb/v2/statistics/default/flow')
	self.ws.set_port(8080)	
        content = self.ws.get()
        allFlowStats = json.loads(content[2])

        flowStats = allFlowStats['flowStatistics']
	# These JSON dumps were handy when trying to parse the responses 
        #print json.dumps(flowStats[0]['flowStat'][1], indent = 2)
	#print json.dumps(flowStats[4], indent = 2)
        for fs in flowStats:
            print "\nSwitch ID : " + fs['node']['id']
	    print '{0:8} {1:8} {2:5} {3:15}'.format('Count', 'Action', 'Port', 'DestIP')
	    if not 'flowStatistic' in fs.values(): 
		print '              none'
		continue
	    for aFlow in fs['flowStatistic']:
		#print "*", aFlow, "*", " ", len(aFlow), " ", not aFlow
	        count = aFlow['packetCount']
	        actions = aFlow['flow']['actions'] 
	        actionType = ''
	        actionPort = ''
	        #print actions
	        if(type(actions) == type(list())):
		    actionType = actions[1]['type']
		    actionPort = actions[1]['port']['id']
		else:
	    	    actionType = actions['type']
		    actionPort = actions['port']['id']
		dst = aFlow['flow']['match']['matchField'][0]['value']
		print '{0:8} {1:8} {2:5} {3:15}'.format(count, actionType, actionPort, dst)

    def flowprogrammer_list(self):
        self.ws.set_path('/controller/nb/v2/flowprogrammer/default')
	self.ws.set_port(8080)	
        content = ws.get()
        j=json.loads(content[2])
        self.ws.show(j)
        #ws.show(content[2])
	return(j)


    def flowprogrammer_add(self, flow):
        # http://localhost:8080/controller/nb/v2/flowprogrammer/default/node/OF/00:00:00:00:00:00:00:01/staticFlow/flow1
        self.ws.set_path('/controller/nb/v2/flowprogrammer/default/node/' + flow['node']['type'] + '/' + flow['node']['id'] + '/staticFlow/' + flow['name'] )
	self.ws.set_port(8080)	
        self.ws.show(flow)
        content = self.ws.set(flow)
        #print content
	flowadd_response_codes = {
	201:"Flow Config processed successfully",
	400:"Failed to create Static Flow entry due to invalid flow configuration",
	401:"User not authorized to perform this operation",
	404:"The Container Name or nodeId is not found",
	406:"Cannot operate on Default Container when other Containers are active",
	409:"Failed to create Static Flow entry due to Conflicting Name or configuration",
	500:"Failed to create Static Flow entry. Failure Reason included in HTTP Error response",
	503:"One or more of Controller services are unavailable",
	} 
	msg=flowadd_response_codes.get(content[0])
	print content[0], content[1], msg

    def flowprogrammer_remove(self, flow):
        self.ws.set_path('/controller/nb/v2/flowprogrammer/default/node/' + flow['node']['type'] + '/' + flow['node']['id'] + '/staticFlow/' + flow['name'] )
	self.ws.set_port(8080)	
        content = self.ws.remove("", flow)

	flowdelete_reponse_codes = {
	204:"Flow Config deleted successfully",
	401:"User not authorized to perform this operation",
	404:"The Container Name or Node-id or Flow Name passed is not found",
	406:"Failed to delete Flow config due to invalid operation. Failure details included in HTTP Error response",
	500:"Failed to delete Flow config. Failure Reason included in HTTP Error response",
	503:"One or more of Controller service is unavailable",
	}
	msg=flowdelete_reponse_codes.get(content[0])
	print content[0], content[1], msg

    def flowprogrammer_remove_all(self):
	allFlowConfigs = self.flowprogrammer_list()
        flowConfigs = allFlowConfigs['flowConfig']
	# These JSON dumps were handy when trying to parse the responses 
        #print json.dumps(flowStats[0]['flowStat'][1], indent = 2)
	#print json.dumps(flowStats[4], indent = 2)
        for fl in flowConfigs:
	    print "Removing ", fl['name']
    	    self.flowprogrammer_remove(fl)
		
    def ovsdb_connect_get_all(self, manager):
        self.ws.set_path('/ovsdb/nb/v2/node/OVS/' + manager + '/tables/manager/rows')
	self.ws.set_port(8080)	
        content = self.ws.get()
        j=json.loads(content[2])
        self.ws.show(j)


    def ovsdb_connect(self, manager, port):
        self.ws.set_path('/controller/nb/v2/connectionmanager/node/' + manager + '/address/' + manager + '/port/' + str(port)) 
	self.ws.set_port(8080)	
	content = self.ws.put('')

	reponse_codes = {
	201:"ovsdb connection processed successfully",
	401:"User not authorized to perform this operation",
	406:"Invalid operation. Failure details included in HTTP Error response",
	500:"Failure Reason included in HTTP Error response",
	503:"One or more of Controller service is unavailable",
	}
	msg=reponse_codes.get(content[0])
	print content[0], content[1], msg

    def ovsdb_bridge_detailed_create(self, manager, name, dtype='OPENFLOW'):
	self.ws.set_path('/ovsdb/nb/v2/node/OVS/' + manager +'/tables/bridge/rows')
	self.ws.set_port(8080)	
	body = """
	{
	    "row": {
	        "Bridge": {
	       	     "name": "%s",
       		     "datapath_type": "%s"
        	}
    	    }
	}
	""" % (name, dtype)
	print body
	body = json.loads(body)
	content = self.ws.post(body)

	reponse_codes = {
	201:"ovsdb processed successfully",
	401:"User not authorized to perform this operation",
	406:"Invalid operation. Failure details included in HTTP Error response",
	500:"Failure Reason included in HTTP Error response",
	503:"One or more of Controller service is unavailable",
	}
	msg=reponse_codes.get(content[0])
	print content[0], content[1], content[2], msg
	return content[2]

    def ovsdb_bridge_all(self, manager, port_uuid):
	self.ws.set_path('/ovsdb/nb/v2/node/OVS/' + manager + '/tables/bridge/rows')
	self.ws.set_port(8080)	

	content = self.ws.get()

	reponse_codes = {
	200:"ovsdb processed successfully",
	401:"User not authorized to perform this operation",
	406:"Invalid operation. Failure details included in HTTP Error response",
	500:"Failure Reason included in HTTP Error response",
	503:"One or more of Controller service is unavailable",
	}
	msg=reponse_codes.get(content[0])
	print content[0], content[1], msg
	return content[0],content[2]

    def ovsdb_bridge_port_all(self, manager, port_uuid):
	self.ws.set_path('/ovsdb/nb/v2/node/OVS/' + manager + '/tables/port/rows')
	self.ws.set_port(8080)	

	content = self.ws.get()

	reponse_codes = {
	200:"ovsdb processed successfully",
	401:"User not authorized to perform this operation",
	406:"Invalid operation. Failure details included in HTTP Error response",
	500:"Failure Reason included in HTTP Error response",
	503:"One or more of Controller service is unavailable",
	}
	msg=reponse_codes.get(content[0])
	print content[0], content[1], msg
	return content[0],content[2]


    def ovsdb_bridge_controller_uuid_from_name(self, manager, name):
        ret, body = self.ovsdb_bridge_all(manager, name)
        allBridges = json.loads(body)

        theBridges = allBridges['rows']
	if theBridges is None:
		return False
	# print "theBridges ", json.dumps(theBridges, indent=4, sort_keys=True)
        for br in theBridges:
	    # print theBridges[br]['name']
	    if  theBridges[br]['name'] == name:
        	i = theBridges[br]['controller']
		print i
                k = i[1]
                print k
		try:
    			l = k[0]
		except IndexError:
    			return 'null'
		print l
		return l[1]

    def ovsdb_bridge_uuid_from_name(self, manager, name):
        ret, body = self.ovsdb_bridge_all(manager, name)
        allBridges = json.loads(body)

        theBridges = allBridges['rows']
	if theBridges is None:
		return False
	# print "theBridges ", json.dumps(theBridges, indent=4, sort_keys=True)
        for br in theBridges:
	    # print theBridges[br]['name']
	    if  theBridges[br]['name'] == name:
        	k = theBridges[br]['_uuid']
        	l = k[1]
		return l

    def ovsdb_bridge_port_uuid_from_name(self, manager, name):
        ret, body = self.ovsdb_bridge_port_all(manager, name)
        allPorts = json.loads(body)

        thePorts = allPorts['rows']
	if thePorts is None:
		return False
        for pr in thePorts:
	    # print thePorts[pr]['name']
	    if  thePorts[pr]['name'] == name:
        	k = thePorts[pr]['_uuid']
        	l = k[1]
		return l

    def ovsdb_bridge_port_get(self, manager, port_uuid):
	self.ws.set_path('/ovsdb/nb/v2/node/OVS/' + manager +'/tables/port/rows/' + port_uuid)
	self.ws.set_port(8080)	

	content = self.ws.get()

	reponse_codes = {
	200:"ovsdb processed successfully",
	401:"User not authorized to perform this operation",
	406:"Invalid operation. Failure details included in HTTP Error response",
	500:"Failure Reason included in HTTP Error response",
	503:"One or more of Controller service is unavailable",
	}
	msg=reponse_codes.get(content[0])
	print content[0], content[1], msg
	return content[0],content[2]


    def ovsdb_bridge_port_interface_get(self, manager, port_uuid):
        ret, body = self.ovsdb_bridge_port_get(manager, port_uuid)
        # XXX -- fix this mess
        j=json.loads(body)
        i = j['interfaces']
        k = i[1]
        l = k[0]
	#print l[1]
	return l[1]

    def ovsdb_bridge_exists(self, manager, name):
        ret, body = self.ovsdb_bridge_all(manager, name)
        allBridges = json.loads(body)

        theBridges = allBridges['rows']
	# print "theBridges ", json.dumps(theBridges, indent=4, sort_keys=True)
	if theBridges is None:
		return False
        for br in theBridges:
	    # print theBridges[br]['name'] + ' == ' + name
	    if  theBridges[br]['name'] == name:
	#	print "found"
		return True 
	# print "not found"
        return False

    def ovsdb_bridge_create(self, manager, name):
	self.ws.set_path('/controller/nb/v2/networkconfig/bridgedomain/bridge/OVS/' + manager +'/' + name)
	self.ws.set_port(8080)	
	content = self.ws.post({})
    	msg = self.response_code_get(content[0])
	print content[0], content[1], msg

    def ovsdb_bridge_port_add(self, manager, br_name, port_name):
	self.ws.set_path('/controller/nb/v2/networkconfig/bridgedomain/port/OVS/' + manager + '/' + br_name + '/' + port_name)
	self.ws.set_port(8080)	
	content = self.ws.post({})
    	msg = self.response_code_get(content[0])
	print content[0], content[1], msg


    def ovsdb_bridge_port_exists(self, manager, br_name, port_name):
        ret, body = self.ovsdb_bridge_port_all(manager, br_name)
        allPorts = json.loads(body)

        thePorts = allPorts['rows']
        for pr in thePorts:
	    if  thePorts[pr]['name'] == port_name:
		return True 
        return False

    def ovsdb_bridge_delete(self, manager, bridge_uuid):
	self.ws.set_path('/ovsdb/nb/v2/node/OVS/' + manager +'/tables/bridge/rows/' + bridge_uuid)
	self.ws.set_port(8080)	
	content = self.ws.delete()

	reponse_codes = {
	200:"ovsdb processed successfully",
	204:"ovsdb no content",
	401:"User not authorized to perform this operation",
	406:"Invalid operation. Failure details included in HTTP Error response",
	500:"Failure Reason included in HTTP Error response",
	503:"One or more of Controller service is unavailable",
	}
	msg=reponse_codes.get(content[0])
	print content[0], content[1], msg

    def ovsdb_bridge_controller_delete(self, manager, controller_uuid):
	self.ws.set_path('/ovsdb/nb/v2/node/OVS/' + manager + '/tables/controller/rows/' + controller_uuid)
	self.ws.set_port(8080)	
	content = self.ws.delete()

	reponse_codes = {
	200:"ovsdb processed successfully",
	204:"ovsdb no content",
	401:"User not authorized to perform this operation",
	406:"Invalid operation. Failure details included in HTTP Error response",
	500:"Failure Reason included in HTTP Error response",
	503:"One or more of Controller service is unavailable",
	}

	msg=reponse_codes.get(content[0])
	print content[0], content[1], msg

    def ovsdb_bridge_port_interface_remove(self, manager, interface_uuid):
	self.ws.set_path('/ovsdb/nb/v2/node/OVS/' + manager +'/tables/interface/rows/' + interface_uuid)
	self.ws.set_port(8080)	
	content = self.ws.delete()

	reponse_codes = {
	200:"ovsdb processed successfully",
	204:"ovsdb no content",
	401:"User not authorized to perform this operation",
	406:"Invalid operation. Failure details included in HTTP Error response",
	500:"Failure Reason included in HTTP Error response",
	503:"One or more of Controller service is unavailable",
	}
	msg=reponse_codes.get(content[0])
	print content[0], content[1], msg
	

    def ovsdb_bridge_port_remove(self, manager, port_uuid):
	self.ws.set_path('/ovsdb/nb/v2/node/OVS/' + manager +'/tables/port/rows/' + port_uuid)
	self.ws.set_port(8080)	
	content = self.ws.delete()

	reponse_codes = {
	201:"ovsdb processed successfully",
	204:"ovsdb no content",
	401:"User not authorized to perform this operation",
	406:"Invalid operation. Failure details included in HTTP Error response",
	500:"Failure Reason included in HTTP Error response",
	503:"One or more of Controller service is unavailable",
	}
	msg=reponse_codes.get(content[0])
	print content[0], content[1], msg

    def ovsdb_bridge_port_detailed_add(self, manager, bridge_uuid, port_name):
	self.ws.set_path('/ovsdb/nb/v2/node/OVS/' + manager +'/tables/port/rows')
	self.ws.set_port(8080)	
	body =	"""
	{
	     "parent_uuid":"%s",
		  "row":{
		      "Port":{
		           "name":"%s"
	      	      }
    	     }
	}
	""" % (bridge_uuid, port_name)

	print body
	body = json.loads(body)
	content = self.ws.post(body)
	reponse_codes = {
	201:"ovsdb processed successfully",
	401:"User not authorized to perform this operation",
	406:"Invalid operation. Failure details included in HTTP Error response",
	500:"Failure Reason included in HTTP Error response",
	503:"One or more of Controller service is unavailable",
	}
	msg=reponse_codes.get(content[0])
	print content[0], content[1], content[2], msg
	return content[2]

    def ovsdb_bridge_port_tunnel_configure_ro(self, manager, interface_uuid, remote_ip, ttype='gre'):
	self.ws.set_path('/ovsdb/nb/v2/node/OVS/' + manager +'/tables/interface/rows/' + interface_uuid)
	self.ws.set_port(8080)	
	body = """
	{
    	    "row": {
        	"Interface": {
            	"type": "%s",
            	"options": [
               		"map",
               		[
                   		[
                        		"key", "100"
                    		],
                    		[
                        		"remote_ip", "%s"
                    		]
                		]
            		]
        	}
    	    }
	}
	""" % (ttype, remote_ip)
	print body
	body = json.loads(body)
	content = self.ws.put(body)
    	msg = self.response_code_get(content[0])
	print content[0], content[1], msg

    def ovsdb_bridge_port_tunnel_configure(self, manager, interface_uuid, remote_ip, local_ip='127.0.0.1', ttype='gre'):
	self.ws.set_path('/ovsdb/nb/v2/node/OVS/' + manager +'/tables/interface/rows/' + interface_uuid)
	self.ws.set_port(8080)	
	body = """
	{
    	    "row": {
        	"Interface": {
            	"type": "%s",
            	"options": [
               		"map",
               		[
                   		[
                        		"key", "100"
                    		],
                    		[
                        		"local_ip", "%s"
                    		],
                    		[
                        		"remote_ip", "%s"
                    		]
                		]
            		]
        	}
    	    }
	}
	""" % (ttype, local_ip,remote_ip)
	print body
	body = json.loads(body)
	content = self.ws.put(body)
    	msg = self.response_code_get(content[0])
	print content[0], content[1], msg


    def ovsdb_build_bridge_and_tunnel_port(self, manager='10.197.1.220', bridge='superbridge0', port='gre100', remote_ip='10.197.2.222', local_ip='10.197.2.220', tunnel_type='gre'):
	    print "Check if bridge exists ..."
            # if the bridge exists we need to the the handles associated with the bridge
	    if not self.ovsdb_bridge_exists(manager, bridge):
	       print "Create bridge ..."
	       self.ovsdb_bridge_create(manager, bridge)
	       b_uuid =  self.ovsdb_bridge_uuid_from_name(manager, bridge)
	    else:
	       print "Get bridge id ..."
	       b_uuid =  self.ovsdb_bridge_uuid_from_name(manager, bridge)

            # if the port exists we need to get the handles associated with the port
	    if not self.ovsdb_bridge_port_exists(manager, bridge, port):
	       print "Add port to bridge ..."
	       self.ovsdb_bridge_port_add(manager, bridge, port)
	       p_uuid =  self.ovsdb_bridge_port_uuid_from_name(manager, port)
	    else:
	       print "Get bridge port id ..."
	       p_uuid =  self.ovsdb_bridge_port_uuid_from_name(manager, port)

	    print "Get bridge port interface id ..."
            # this is a bit tricky and yet another handle for an associated object
	    i_uuid = self.ovsdb_bridge_port_interface_get(manager, p_uuid)
	    self.ovsdb_bridge_port_tunnel_configure(manager, i_uuid, remote_ip, local_ip, tunnel_type)

	    return True

    def ovsdb_bridge_name_delete(self, manager, bridge):
	    if not self.ovsdb_bridge_exists(manager, bridge):
		return False
	    else:
	       print "Get bridge id ..."
	       b_uuid =  self.ovsdb_bridge_uuid_from_name(manager, bridge)
    	       self.ovsdb_bridge_delete( manager, b_uuid)
	    return True

    def ovsdb_bridge_tunnel_port_remove(self, manager, bridge, port):
            # if the port exists we need to get the handles associated with the port
	    if not self.ovsdb_bridge_port_exists(manager, bridge, port):
		return False
	    else:
	       print "Get bridge port id ..."
	       p_uuid =  self.ovsdb_bridge_port_uuid_from_name(manager, port)

    	    self.ovsdb_bridge_port_remove(manager, p_uuid)
	    return True

    def ovsdb_bridge_tunnel_port_add(self, manager, bridge, port, remote_ip, tunnel_type):
            # if the port exists we need to get the handles associated with the port
	    if self.ovsdb_bridge_port_exists(manager, bridge, port):
		# maybe remove it and go on to recreate it?
		return False
	    else:
	        self.ovsdb_bridge_port_add(manager, bridge, port)
	        p_uuid = self.ovsdb_bridge_port_uuid_from_name(manager, port)
	        i_uuid = self.ovsdb_bridge_port_interface_get(manager, p_uuid)
	        self.ovsdb_bridge_port_tunnel_configure_ro(manager, i_uuid, remote_ip, tunnel_type)
	    return True

    def ovsdb_bridge_of_controller_delete(self, manager, bridge):
	    print "Get bridge controller id ..."
	    c_uuid = self.ovsdb_bridge_controller_uuid_from_name( manager, bridge)
	    print "Delete bridge controller ...", c_uuid
	    # currently this command results in the linux interface being destroyed
	    self.ovsdb_bridge_controller_delete(manager, c_uuid)


class ODLMenu(object):
    def __init__(self, tests):
        self.tests = tests

    def print_menu(self):
        print (30 * '-')
        print ("   OPENDAYLIGHT       ")
        print (30 * '-')
        print ("1.  Add Flow 1        ")
        print ("2.  Add Flow 2        ")
        print ("3.  Add Several Flows ")
        print ("4.  Remove Flow 1     ")
        print ("5.  Remove Flow 2     ")
        print ("6.  Remove All Flows  ")
        print ("7.  Toggle Flow       ")
        print ("8.  List Flow Stats   ")
        print ("9.  List Topology     ")
        print ("10. List Flows        ")
        print ("11. List Ports        ")
        print ("12. Add PCMM Flow 1   ")
        print ("13. Remove PCMM Flow 1")
        print ("14. Add PCMM Flow 2   ")
        print ("15. Remove PCMM Flow 2")
        print ("16. Toggle PCMM Flows")
        print ("46. Nodes Connects List")
        print ("47. Flow Add")
        print ("48. Flow Remove")
        print ("49. OVSDB Tunnel Port Add - Full Sequence (Options 1)")
        print ("50. OVSDB Tunnel Port Add - Full Sequence (Options 2)")
        print ("51. OVSDB Tunnel Port Remove - Full Sequence")
        print ("52. OVSDB Bridge Delete")
        print ("53. OVSDB Connects Get All")
        print ("54. OVSDB Bridge Remove Controller")
        print ("55. OVSDB Bridge Simple Create")
        print ("56. OVSDB Bridge Detailed Create")
        print ("57. OVSDB Bridge Port Simple Add")
        print ("58. OVSDB Bridge Port Detailed Add")
        print ("59. OVSDB Bridge Port Tunnel Add Solo")
        print ("60. OVSDB Tunnel Build")
        print ("61. OVSDB Tunnel Port Add")
        print ("62. OVSDB Tunnel Port Remove")
        print ("63. OVSDB Tunnel Destroy")
        print ("64. OVSDB Bridge Controller Disable")
        print ("70. OVSDB Test Topology List")
        print ("q. Quit               ")
#        print (30 * '-')


    def no_such_action(self):
        print "Invalid option!"

    def run(self):
	#self.print_menu()
        actions = {
	"1": self.tests.flow_add_1, 
	"2": self.tests.flow_add_2, 
	"3": self.tests.flow_add_several, 
	"4": self.tests.flow_remove_1,
	"5": self.tests.flow_remove_2,
	"6": self.tests.flow_remove_all,
	"7": self.tests.flow_toggle,
	"8": self.tests.flow_list_stats,
	"9": self.tests.topology_list,
	"10":self.tests.flow_list,
	"11":self.tests.port_list,
	"12":self.tests.flow_add_pc_1,
	"13":self.tests.flow_remove_pc_1,
	"14":self.tests.flow_add_pc_2,
	"15":self.tests.flow_remove_pc_2,
	"16":self.tests.flow_toggle_pcmm,
        "46":self.tests.node_connections_list,
	"47":self.tests.flow_demo_add,
	"48":self.tests.flow_demo_remove,
	"49":self.tests.ovsdb_bridge_port_tunnel_add_1,
	"50":self.tests.ovsdb_bridge_port_tunnel_add_2,
	"51":self.tests.ovsdb_bridge_port_tunnel_remove,
        "52":self.tests.ovsdb_bridge_delete,
        "53":self.tests.ovsdb_connects_get,
	"54":self.tests.ovsdb_bridge_controller_remove,
	"55":self.tests.ovsdb_bridge_create_simple,
	"56":self.tests.ovsdb_bridge_create_detailed,
	"57":self.tests.ovsdb_bridge_port_add_simple,
	"58":self.tests.ovsdb_bridge_port_add_detailed,
	"59":self.tests.ovsdb_bridge_port_tunnel_add_solo,
	"60":self.tests.ovsdb_tunnel_build,
	"61":self.tests.ovsdb_tunnel_port_add,
	"62":self.tests.ovsdb_tunnel_port_remove,
	"63":self.tests.ovsdb_tunnel_destroy,
	"64":self.tests.ovsdb_bridge_controller_disable,
	"70":self.tests.ovsdb_test_topo_dump,
	"q" :self.tests.exit_app,
        }

        while True:
            self.print_menu()
            selection = raw_input("Enter selection: ")
            if "quit" == selection:
                return
            toDo = actions.get(selection, self.no_such_action)
            toDo()

# XXX - do not use underscores and dashes in flow names.
# XXX - ingress ports that possibly don't exist ? throw configuration errors
flow1 = {
        "actions": [
            "OUTPUT=2"
        ],         
        "installInHw":"false",
        "name":"flow1",
        "node":
        {
            "id":"00:00:00:00:00:00:00:02",
            "type":"OF"
        }, 
        "priority":"500",
        "etherType":"0x800",
        "nwSrc":"10.0.0.7",
        "tpSrc":"8081",
        "nwDst":"10.0.0.3", 
}

flow2 = {
        "actions": [
            "OUTPUT=2"
        ],         
        "installInHw":"false",
        "name":"flow2",
        "node":
	{
	    "id":"00:00:00:00:00:00:00:01",
	    "type":"OF"
        },
        "priority":"500",
        "etherType":"0x800",
        "nwSrc":"10.0.0.1",
        "tpSrc":"1369",
        "nwDst":"10.0.0.3", 
}


flow3 = {
     "actions": [
        "OUTPUT=3"
     ], 
     "etherType": "0x800", 
     "installInHw": "true", 
     "name": "flow2", 
     "node": {
           "id": "00:00:00:00:00:00:00:01", 
           "type": "OF"
     }, 
     "nwDst": "10.0.0.2", 
     "nwSrc": "10.0.0.1", 
     "priority": "500", 
     "protocol": "6"
} 


flow5={
     "actions": [
          "OUTPUT=2"
     ], 
     "etherType": "0x800", 
     "installInHw": "false", 
     "name": "flow5", 
     "node": {
         "id": "00:00:0e:21:52:b5:6b:44",
          "type": "OF"
      }, 
     "nwSrc": "10.0.0.10", 
     "priority": "500"
}

flow4={
   "actions": [
       "OUTPUT=2"
   ], 
   "etherType": "0x800", 
   "installInHw": "true", 
   "name": "flow4", 
   "node": {
           "id": "00:00:00:00:00:00:00:01", 
           "type": "OF"
    }, 
    "nwSrc": "10.0.0.1", 
    "priority": "500", 
    "vlanId": "1", 
    "vlanPriority": "1"
}

flow7={
   "actions": [
       "FLOOD"
   ], 
   "etherType": "0x800", 
   "installInHw": "true", 
   "name": "flow7", 
   "node": {
         "id": "00:00:92:a0:15:9b:bb:4a",
         "type": "OF"
    }, 
    "nwSrc": "10.0.0.1", 
    "priority": "500", 
}

''' Demo Kit  Layout

flow_pcmm_1 = {
     "actions": [
        "FLOOD"
     ], 
     "etherType": "0x800", 
     "installInHw": "true", 
     "name": "flowpcmmHighBW", 
     "node": {
           "id": "51966", 
           "type": "PC"
     }, 
     "tpDst":"8081",
     "nwDst": "10.32.4.208", 
     "nwSrc": "10.32.154.2", 
     "priority": "100", 
} 

flow_pcmm_2 = {
     "actions": [
        "FLOOD"
     ], 
     "etherType": "0x800", 
     "installInHw": "true", 
     "name": "flowpcmmLowBW", 
     "node": {
           "id": "51966", 
           "type": "PC"
     }, 
     "tpDst":"8081",
     "nwDst": "10.32.4.208", 
     "nwSrc": "10.32.154.2", 
     "priority": "64", 
} 
'''


''' LAB Workbench Layout 
'''

flow_pcmm_1 = {
     "actions": [
        "FLOOD"
     ], 
     "etherType": "0x800", 
     "installInHw": "true", 
     "name": "flowpcmmHighBW", 
     "node": {
           "id": "51966", 
           "type": "PC"
     }, 
     "tpDst":"8081",
     "nwDst": "10.200.90.10",
     "nwSrc": "10.50.201.151",
     "priority": "100", 
} 

flow_pcmm_2 = {
     "actions": [
        "FLOOD"
     ], 
     "etherType": "0x800", 
     "installInHw": "true", 
     "name": "flowpcmmLowBW", 
     "node": {
           "id": "51966", 
           "type": "PC"
     }, 
     "tpDst":"8081",
     "nwDst": "10.200.90.10",
     "nwSrc": "10.50.201.151",
     "priority": "64", 
} 


class ODLTests(object):
        def __init__(self, odl):
            self.odl = odl
            self.b_uuid = ''
            self.p_uuid = ''
            self.i_uuid = ''
            self.c_uuid = ''
	    self.manager = self.manager_a = '10.197.1.220'
	    self.manager_b = '10.197.1.222'
	    self.remote_ip = self.wan_ip_a = '10.197.2.222'
	    self.local_ip = self.wan_ip_b = '10.197.2.220'
	    self.bridge_ip_a = '192.168.222.220'
	    self.bridge_ip_b = '192.168.222.222'
	    self.br_name = 'superbridge0'
	    self.port_name = 'gre1000'
	    self.tunnel_type = 'vxlan'
	    
        def ovsdb_test_topo_dump(self):
            print "Current bridge uuid     ",self.b_uuid
            print "Current port uuid       ",self.p_uuid
            print "Current interface  uuid ",self.i_uuid
            print "Current controller uuid ",self.c_uuid
	    print "Compute endpoint   a    ",self.manager_a
	    print "Compute endpoint   a    ",self.manager_a
	    print "Compute manager         ",self.manager
	    print "Current wan ip b (remote) ",self.remote_ip
	    print "Current wan ip a (local)  ",self.local_ip
	    print "Current bridge ip a     ",self.bridge_ip_a
	    print "Current bridge ip b     ",self.bridge_ip_b
	    print "Current bridge name     ",self.br_name
	    print "Current bridge port     ",self.port_name
	    print "Current tunnel type     ",self.tunnel_type


	def setup_network(self, manager_a='10.197.1.220', manager_b='10.197.1.222', bridge='superbridge0', port='gre100', wan_ip_b='10.197.2.222', wan_ip_a='10.197.2.220', tunnel_type='gre', bridge_ip='192.168.222.222' ):
	    self.manager = self.manager_a = manager_a
	    self.manager_b = manager_b
	    self.remote_ip = self.wan_ip_b  = wan_ip_b
	    self.local_ip  = self.wan_ip_a  = wan_ip_a
	    self.br_name = bridge
	    self.port_name = port
	    self.tunnel_type = tunnel_type

	def flow_add_pc_1(self):
	    print "Test PCMM Flow 1     "
	    self.odl.flowprogrammer_add(flow_pcmm_1)

	def flow_remove_pc_1(self):
	    print "Remove PCMM Flow 1  "
	    self.odl.flowprogrammer_remove(flow_pcmm_1)


	def flow_add_pc_2(self):
	    print "Test PCMM Flow 2     "
	    self.odl.flowprogrammer_add(flow_pcmm_2)

	def flow_remove_pc_2(self):
	    print "Remove PCMM Flow 2  "
	    self.odl.flowprogrammer_remove(flow_pcmm_2)

	def flow_toggle_pcmm(self):
	    print "Toggle Flow    "
	    global toggle_pcmm
	    toggle_pcmm = 3 - toggle_pcmm
	    if toggle_pcmm == 1:
		self.flow_remove_pc_2()
		self.flow_add_pc_1()
	    else:
		self.flow_remove_pc_1()
		self.flow_add_pc_2()

	def flow_add_1(self):
	    print "Add Flow 1     "
	    self.odl.flowprogrammer_add(flow1)


	def flow_add_2(self):
	    print "Add Flow 2     "
	    self.odl.flowprogrammer_add(flow2)

	def flow_add_several(self):
	    print "Add Flow Several     "
	    self.odl.flowprogrammer_add(flow1)
	    self.odl.flowprogrammer_add(flow2)
	    self.odl.flowprogrammer_add(flow3)
	    self.odl.flowprogrammer_add(flow4)
	    self.odl.flowprogrammer_add(flow5)


	def flow_toggle(self):
	    print "Toggle Flow    "
	    global toggle
	    toggle = 3 - toggle
	    if toggle == 1:
		self.flow_remove_2()
		self.flow_add_1()
	    else:
		self.flow_remove_1()
		self.flow_add_2()


	def flow_remove_1(self):
	    print "Remove Flow 1  "
	    self.odl.flowprogrammer_remove(flow1)

	def flow_remove_2(self):
	    print "Remove Flow 2  "
	    self.odl.flowprogrammer_remove(flow2)

	def flow_remove_all(self):
	    print "Remove All Flows "
	    self.odl.flowprogrammer_remove_all()

	def flow_list_stats(self):
	    print "List Flow Stats"
	    self.odl.statistics_flows()

	def topology_list(self):
	    print "List Topology  "
	    self.odl.topology()

	def flow_list(self):
	    print "List Flows  "
            self.odl.flowprogrammer_list()

        def port_list(self):
            print "List Ports Stats  "
            self.odl.statistics_ports()

        def ovsdb_connects_get(self):
    	    self.odl.ovsdb_connect_get_all(self.manager)

        def node_connections_list(self):
    	    self.odl.node_connections_get_all()
	
	def flow_demo_add(self):
	    self.odl.flowprogrammer_add(flow7)

	def flow_demo_remove(self):
	    self.odl.flowprogrammer_remove(flow7)

        def exit_app(self):
            print "Quit           "
            exit(0)

	# this method seems equally valid but does not seem to create or leave a linux interface
	def ovsdb_bridge_port_tunnel_add_1(self):
	    self.odl.ovsdb_connect(self.manager, 6640)

	    print "Check if bridge exists ..."
	    if not self.odl.ovsdb_bridge_exists(self.manager, self.br_name):
	       print "Create bridge ..."
	       # option 1.
	       self.b_uuid = self.odl.ovsdb_bridge_detailed_create(self.manager, self.br_name)

	       print "b_uuid ", self.b_uuid
	    else:
	       print "Get bridge id ..."
	       self.b_uuid =  self.odl.ovsdb_bridge_uuid_from_name(self.manager, self.br_name)

	     

	    if not self.odl.ovsdb_bridge_port_exists(self.manager, self.br_name, self.port_name):
	       print "Add port to bridge ..."
	       self.p_uuid = self.odl.ovsdb_bridge_port_detailed_add(self.manager, self.b_uuid, self.port_name)
	    else:
	       print "Get bridge port id ..."
	       self.p_uuid =  self.odl.ovsdb_bridge_port_uuid_from_name(self.manager, self.port_name)

	    print "Get bridge port interface id ..."
	    self.i_uuid = self.odl.ovsdb_bridge_port_interface_get(self.manager, self.p_uuid)

	    print "Configure bridge port tunnel ... i_uuid"
	    self.odl.ovsdb_bridge_port_tunnel_configure(self.manager, self.i_uuid, self.remote_ip, self.local_ip, self.tunnel_type)

	    print "Get bridge controller id ..."
	    self.c_uuid = self.odl.ovsdb_bridge_controller_uuid_from_name( self.manager, self.br_name)
	    print "Delete bridge controller ...", self.c_uuid
	    # currently this command results in the linux interface being destroyed
	    self.odl.ovsdb_bridge_controller_delete(self.manager, self.c_uuid)


	def ovsdb_bridge_port_tunnel_add_2(self):
	    self.odl.ovsdb_connect(self.manager, 6640)

	    print "Check if bridge exists ..."
	    if not self.odl.ovsdb_bridge_exists(self.manager, self.br_name):
	       print "Create bridge ..."
	       # option 1.
	       # self.b_uuid = self.odl.ovsdb_bridge_detailed_create(self.manager, self.br_name)

	       # option 2.
	       self.odl.ovsdb_bridge_create(self.manager, self.br_name)
	       self.b_uuid =  self.odl.ovsdb_bridge_uuid_from_name(self.manager, self.br_name)
	       print "b_uuid ", self.b_uuid
	    else:
	       print "Get bridge id ..."
	       self.b_uuid =  self.odl.ovsdb_bridge_uuid_from_name(self.manager, self.br_name)

	     

	    if not self.odl.ovsdb_bridge_port_exists(self.manager, self.br_name, self.port_name):
	       print "Add port to bridge ..."
	       # self.p_uuid = self.odl.ovsdb_bridge_port_detailed_add(self.manager, self.b_uuid, self.port_name)
	       self.odl.ovsdb_bridge_port_add(self.manager, self.br_name, self.port_name)
	       self.p_uuid =  self.odl.ovsdb_bridge_port_uuid_from_name(self.manager, self.port_name)
	    else:
	       print "Get bridge port id ..."
	       self.p_uuid =  self.odl.ovsdb_bridge_port_uuid_from_name(self.manager, self.port_name)

	    print "Get bridge port interface id ..."
	    self.i_uuid = self.odl.ovsdb_bridge_port_interface_get(self.manager, self.p_uuid)

	    print "Configure bridge port tunnel ... ", self.i_uuid
	    self.odl.ovsdb_bridge_port_tunnel_configure(self.manager, self.i_uuid, self.remote_ip, self.local_ip, self.tunnel_type)

	    print "Get bridge controller id ..."
	    self.c_uuid = self.odl.ovsdb_bridge_controller_uuid_from_name( self.manager, self.br_name)
	    print "Delete bridge controller ...", self.c_uuid
	    # currently this command results in the linux interface being destroyed -- bug or miss use?  unclear
	    self.odl.ovsdb_bridge_controller_delete(self.manager, self.c_uuid)

	def ovsdb_tunnel_build(self):
	    # setup the parameters for the endpoint of both halves of the tunnel
	    # Need to setup only once.  Repeated connections to connection manager cause all ODL file handles to be exhausted
	     
	    self.odl.ovsdb_connect(self.manager_a, 6640)
            self.odl.ovsdb_build_bridge_and_tunnel_port(self.manager_a, self.br_name, self.port_name, self.wan_ip_b, self.wan_ip_a)

	    self.odl.ovsdb_connect(self.manager_b, 6640)
            self.odl.ovsdb_build_bridge_and_tunnel_port(self.manager_b, self.br_name, self.port_name, self.wan_ip_a, self.wan_ip_b)
	    
	    
	def ovsdb_tunnel_destroy(self):
            self.odl.ovsdb_bridge_name_delete(self.manager_a, self.br_name)
            self.odl.ovsdb_bridge_name_delete(self.manager_b, self.br_name)

	def ovsdb_tunnel_port_remove(self):
            self.odl.ovsdb_bridge_tunnel_port_remove(self.manager_a, self.br_name, self.port_name)
            self.odl.ovsdb_bridge_tunnel_port_remove(self.manager_b, self.br_name, self.port_name)

	def ovsdb_tunnel_port_add(self):
            self.odl.ovsdb_bridge_tunnel_port_add(self.manager_a, self.br_name, self.port_name, self.wan_ip_b, self.tunnel_type)
            self.odl.ovsdb_bridge_tunnel_port_add(self.manager_b, self.br_name, self.port_name, self.wan_ip_a, self.tunnel_type)

        def ovsdb_bridge_controller_disable(self):
            self.odl.ovsdb_bridge_of_controller_delete(self.manager_a, self.br_name)
            self.odl.ovsdb_bridge_of_controller_delete(self.manager_b, self.br_name)


	def ovsdb_bridge_port_tunnel_remove(self):
	    #self.odl.ovsdb_bridge_port_interface_remove(self.manager, self.i_uuid)
    	    #self.odl.ovsdb_bridge_port_interface_remove(self.manager, self.p_uuid)
            self.odl.ovsdb_bridge_port_remove(self.manager_a, self.p_uuid)

	def ovsdb_bridge_delete(self):
            self.odl.ovsdb_bridge_delete(self.manager, self.b_uuid)
    
	def ovsdb_bridge_controller_remove(self):
	    print "Get bridge controller id ..."
	    self.c_uuid = self.odl.ovsdb_bridge_controller_uuid_from_name( self.manager, self.br_name)
	    print "Delete bridge controller ...", self.c_uuid
	    self.odl.ovsdb_bridge_controller_delete(self.manager, self.c_uuid)

	def ovsdb_bridge_create_simple(self):
	    self.odl.ovsdb_bridge_create( self.manager, self.br_name)
	    self.b_uuid =  self.odl.ovsdb_bridge_uuid_from_name(self.manager, self.br_name)
	    print "bridge created ...", self.b_uuid

	def ovsdb_bridge_create_detailed(self):
	    self.b_uuid = self.odl.ovsdb_bridge_detailed_create( self.manager, self.br_name)
	    print "bridge created detailed ...", self.b_uuid

	def ovsdb_bridge_port_add_simple(self):
	    self.odl.ovsdb_bridge_port_add( self.manager, self.br_name, self.port_name)
	    self.p_uuid =  self.odl.ovsdb_bridge_port_uuid_from_name(self.manager, self.port_name)
	    print "bridge port add  ...", self.p_uuid

	def ovsdb_bridge_port_add_detailed(self):
	    self.p_uuid = self.odl.ovsdb_bridge_port_detailed_add(self.manager, self.b_uuid, self.port_name)
	    print "bridge port add  detailed ...", self.p_uuid

	def ovsdb_bridge_port_tunnel_add_solo(self):
	    print "Get bridge port interface id ..."
	    self.i_uuid = self.odl.ovsdb_bridge_port_interface_get(self.manager, self.p_uuid)
	    print "Configure bridge port tunnel ...", self.i_uuid
	    self.odl.ovsdb_bridge_port_tunnel_configure(self.manager, self.i_uuid, self.remote_ip, self.local_ip, self.tunnel_type)



if __name__ == "__main__":
    ws = RestfulAPI('127.0.0.1')
    #ws = RestfulAPI('192.168.56.10')
    ws.credentials('admin', 'admin')
    odl = ODL(ws)
    tests = ODLTests(odl)
    tests.setup_network( '10.197.1.220', '10.197.1.222', 'superbridge0', 'gre100', '10.197.2.222', '10.197.2.220', 'vxlan' )
    # LV mobile
    # tests.setup_network( '10.0.0.135', 10.0.0.136', 'superbridge0', 'gre100', '10.36.0.135', '10.36.0.136', 'gre' )

    menu=ODLMenu(tests)
    menu.run()
    exit(0)



