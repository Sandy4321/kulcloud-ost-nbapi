#  
#  Copyright (C) 2013, Seok Hwan Kong <seokhwan.kong@kulcloud.net>
# 
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.
#

from kulcloud.core import mlapi_base_v1
from kulcloud.core.v1.mul_nbapi import ofp_switch_features
from kulcloud.core.v1.mul_nbapi import nbapi_switch_brief_list_t
from kulcloud.core.v1.mul_nbapi import ofp_phy_port
from kulcloud.core.v1.mul_nbapi import nbapi_port_list_t
from kulcloud.core.v1.mul_nbapi import flow as mul_flow
import kulcloud.core.v1.mul_nbapi as mul_nbapi
from kulcloud.core.v1.nbapi_error_code import Error


import json
import uuid
import pdb
import MySQLdb as mdb
import time
from pymongo import MongoClient
from bson.objectid import ObjectId



DB_HOST = '127.0.0.1'
DB_PORT = 27017
DB_NAME = 'kulcloud_nfv'


class mlapi_json_serialization():
    def __init__(self):
        pass
    
    def nbapi_switch_brief_list_t_serialization(self, resp):
        return [{'peer':s.conn_str,'state':s.state, 'ports':s.n_ports,'dpid':'0x%lx' % s.switch_id.datapath_id} 
                    for s in resp]
    
    def nbapi_path_elem_t_serialization(self, resp, alias_map):
        return {'dpid': alias_map[resp.switch_alias],'ingress_port':resp.ingress_port_no, 'egress_port':resp.egress_port_no} 
            
    
    def nbapi_port_list_t_serialization(self, resp):
        return [self.ofp_phy_port_serialization(port) for port in resp]
       
    
    def nbapi_port_list_t_of_switch_serialization(self, ports_len, resp):
    	s_ports = mul_nbapi.ofp_phy_port_array.frompointer(resp)
        return [self.ofp_phy_port_serialization(s_ports[i]) for i in range(ports_len)]
    
    def nbapi_path_elem_list_t_serialization(self, resp, alias_map):
        return [self.nbapi_path_elem_t_serialization(path_elem, alias_map) for path_elem in resp]
    
    def nbapi_port_neigh_list_t_serialization(self, resp, alias_map):
        port_neigh_list = []
        for neigh in resp:
            if neigh.neigh_present == 1:
                port_neigh_list.append(self.c_ofp_port_neigh_serialization(neigh, alias_map))
        
        return port_neigh_list
    
    
    def nbapi_switch_flow_list_t_serialization(self, resp):
        switch_flow_list = []
        for flow in resp:
            switch_flow_list.append(self.c_ofp_flow_info_serialization(flow))
        
        return switch_flow_list
    
    def nbapi_fabric_host_list_t_serialization(self, resp):
        fab_host_list = []
        for host in resp:
            fab_host_list.append(self.c_ofp_host_mod_serialization(host))
        
        return fab_host_list
    
    def c_ofp_flow_info_serialization(self, resp):
        wildcard = mul_nbapi.OFPFW_ALL & ~(mul_nbapi.OFPFW_NW_SRC_MASK) & ~(mul_nbapi.OFPFW_DL_TYPE)
        flow_id = self.flow_tbl.match(resp.datapath_id, resp.flow, wildcard, resp.oport, 0)
        return {'flow_id':flow_id, 'flow_info':{'dpid':'0x%lx' % resp.datapath_id, 
                'nw_src': mul_nbapi.nbapi_parse_nw_addr_to_str(resp.flow.nw_src),
                'nw_dst': mul_nbapi.nbapi_parse_nw_addr_to_str(resp.flow.nw_dst),
                'dl_src': mul_nbapi.nbapi_parse_mac_to_str(resp.flow.dl_src),
                'dl_dst': mul_nbapi.nbapi_parse_mac_to_str(resp.flow.dl_dst),
                'vlan': resp.flow.dl_vlan,
                'in_port': resp.flow.in_port,
                'out_port': resp.oport,
                'bps': mul_nbapi.nbapi_parse_bps_to_str(resp.bps),
                'pps': mul_nbapi.nbapi_parse_bps_to_str(resp.pps),
                'pkt_count': resp.packet_count,
                'byte_count': resp.byte_count}
                }
        
    def c_ofp_host_mod_serialization(self, resp):
        return {'dpid': resp.switch_id.datapath_id,
                'nw_src': mul_nbapi.nbapi_parse_nw_addr_to_str(resp.host_flow.nw_src),
                'dl_src': mul_nbapi.nbapi_parse_mac_to_str(resp.host_flow.dl_src),
                'in_port': resp.host_flow.in_port
                }

    def c_ofp_port_neigh_serialization(self, resp, alias_map):
        return {'port_no':resp.port_no, 'neighbor_dpid': alias_map[resp.neigh_dpid],
                'neighbor_port_no' : resp.neigh_port }
        
    def ofp_phy_port_serialization(self, resp):
        return {'port_no':resp.port_no, 'hw_addr':mul_nbapi.nbapi_parse_mac_to_str(resp.hw_addr), 
                 'name':resp.name, 'config':resp.config, 'state':resp.state, 
                 'curr':resp.curr, 'advertised':resp.advertised,
                 'supported':resp.supported, 'peer':resp.peer} 
        
    
    def ofp_switch_fetures_serialization(self, resp):
        return {'dpid':'0x%lx' % resp.datapath_id,'n_buffers':resp.n_buffers, 'n_tables':resp.n_tables,
                            'capabilites':resp.capabilities, 'actions':resp.actions , 
                            'port_list':self.nbapi_port_list_t_of_switch_serialization((resp.header.length-32)/48, resp.ports)}
    
    
    
    def nbapi_flow_brief_list_t_serialization(self, resp):
        pass
    
        
class mlapi_json_deserialization():
    def __init__(self):
        pass 
    
    def action_deserialization(self, obj):
        act = None
        obj['action']=str(obj['action'])
        if 'OUTPUT' in obj['action'] :
            act = mul_nbapi.nbapi_make_action_output(int(obj['value']))
        elif 'SET_VLAN_VID' in obj['action'] :
            act = mul_nbapi.nbapi_make_action_set_vid(int(obj['value']))
        elif 'SET_VLAN_PCP' in obj['action'] :
            act = mul_nbapi.nbapi_make_action_set_vlan_pcp(int(obj['value']))
        elif 'STRIP_VLAN' in obj['action'] :
            act = mul_nbapi.nbapi_make_action_strip_vlan(int(obj['value']))
        elif 'SET_DL_SRC' in obj['action'] :
            act = mul_nbapi.nbapi_make_action_set_smac(str(obj['value']))
        elif 'SET_DL_DST' in obj['action'] :
            act = mul_nbapi.nbapi_make_action_set_dmac(str(['value']))
        elif 'SET_NW_SRC' in obj['action'] :
            act = mul_nbapi.nbapi_make_action_set_nw_saddr(str(obj['value']))
        elif 'SET_NW_DST' in obj['action'] :
            act = mul_nbapi.nbapi_make_action_set_nw_daddr(str(obj['value']))
        elif 'SET_NW_TOS' in obj['action'] :
            act = mul_nbapi.nbapi_make_action_set_nw_tos(int(obj['value']))
        elif 'SET_TP_SRC' in obj['action'] :
            act = mul_nbapi.nbapi_make_action_set_tp_sport(int(obj['value']))
        elif 'SET_TP_DST' in obj['action'] :
            act = mul_nbapi.nbapi_make_action_set_tp_dport(int(obj['value']))
        return act
        
    
    def flow_deserialization(self, obj):
        flow = mul_nbapi.nbapi_flow_make_flow(str(obj['nw_src']), str(obj['nw_dst']),
                                            int(obj['in_port']), int(obj['dl_vlan']),
                                            int(obj['dl_type']), int(obj['tp_src']),
                                            int(obj['tp_dst']), str(obj['dl_src']),
                                            str(obj['dl_dst']), int(obj['dl_vlan_pcp']),
                                            int(obj['nw_tos']), int(obj['nw_proto']))
               
        return flow   
    
    def fabric_deserialization(self, obj):
        flow = mul_nbapi.nbapi_fabric_make_flow(str(obj['nw_src']), str(obj['dl_src']), obj['in_port'])               
        return flow   
  
    def actions_deserialization(self, obj):
        actions = []
        for action in obj:
            act = self.action_deserialization(action)
            actions.append(act)
        return actions
    
    def object_decoder(self, obj):
        if obj['type'] == 'flow':            
            return self.flow_deserialization(obj)
        if obj['type'] == 'actions':            
            return self.actions_deserialization(obj['actions'])
        if obj['type'] == 'fabric':            
            return self.fabric_deserialization(obj)
        #if '__type__' in obj and obj['__type__'] == 'actions':            
        #    return self.action_deserialization(obj)
        return obj

    
""" modified by backguyn 20131004 """
class check_pps():
    def __init__(self):
        pass

    def check_port_pps(self, dpid, port_num, pps_type):
        return mul_nbapi.get_switch_statistics_port(int(dpid, 0), port_num, pps_type)

mode_changing = False
    
class mlapi(mlapi_base_v1.MlapiBaseV1):	
    def __init__(self):
        self.json_serializer = mlapi_json_serialization()
        self.json_deserializer = mlapi_json_deserialization()   
        self.flow_tbl={}   
        self.fab_host_tbl={}
        self.alias_map = {}
        
        self.db_client = MongoClient(DB_HOST, DB_PORT)
        self.db = self.db_client[DB_NAME]
        
        self.err = Error()
        
        ''' Make API and DB mapping table '''
        ServiceChainMgr_package = __import__('kulcloud.api.v1')
        ServiceChainMgr_module = getattr(ServiceChainMgr_package, 'ServiceChainManager')
        ServiceChainMgr_validator = getattr(ServiceChainMgr_module, 'input_validation')
        
        NFVTopologyMgr_package = __import__('kulcloud.api.v1')
        NFVTopologyMgr_module = getattr(NFVTopologyMgr_package, 'NFVTopologyManager')
        NFVTopologyMgr_validator = getattr(NFVTopologyMgr_module, 'input_validation')
        
        ServiceChainDefaultRuleMgr_package = __import__('kulcloud.api.v1')
        ServiceChainDefaultRuleMgr_module = getattr(ServiceChainDefaultRuleMgr_package, 'ServiceChainDefaultRuleManager')
        ServiceChainDefaultRuleMgr_validator = getattr(ServiceChainDefaultRuleMgr_module, 'input_validation')      
        
           
        self.db_collection['NFVGroupMgr']={'name':'NFVGroupMgr', 'keys':['name'], 'validator':None}
        self.db_collection['NFVTopologyMgr']={'name':'NFVTopologyMgr', 'keys':['dpid','in_port','out_port','name'], 'validator':NFVTopologyMgr_validator}
        self.db_collection['ServiceChainDefaultRuleMgr']={'name':'ServiceChainDefaultRuleMgr', 'keys':['service_id', 'service_level'], 'validator':ServiceChainDefaultRuleMgr_validator}
        self.db_collection['ServiceChainMgr']={'name':'ServiceChainMgr', 'keys':['ip','service_id'], 'validator':ServiceChainMgr_validator}
        self.db_collection['ServiceMgr']={'name':'ServiceMgr', 'keys':['name', 'dpid', 'in_port', 'out_port'], 'validator':None}
        self.db_collection['UserMgr']={'name':'UserMgr', 'keys':['mdn', 'ip'], 'validator':None}
        
        
        
	resp =[]
        # TODO : Threading to check the switch pull status and alias_map
	try:
	    resp = mul_nbapi.get_switch_all()    	
	except:
	    print 'error'
        for s in resp:
            sw_info = mul_nbapi.get_switch(s.switch_id.datapath_id)
            self.alias_map[mul_nbapi.get_switch_alias_from_switch_info(sw_info)]='0x%lx' % s.switch_id.datapath_id
            
    
    def str_uuid(self):
	return str(uuid.uuid4())
    
    
    def get_all_flow(self, conf, dpid):
	pass
	#resp = mul_nbapi.get_flows(dpid)
	#return self.json_serializer.nbapi_flow_brief_list_t_serialization(resp)
	
    def get_flow(self, conf, dpid, flow_id):
	pass
	
    def create_flow(self, conf, dpid, params):
        dpid = int(dpid, 0)
        flow_id = '' 
        params['type'] = 'flow'
        flow = self.json_deserializer.object_decoder(params)
        params['type'] = 'actions'
        action_list = self.json_deserializer.object_decoder(params)        
        #wildcards = mul_nbapi.OFPFW_ALL & ~(mul_nbapi.OFPFW_NW_SRC_MASK) & ~(mul_nbapi.OFPFW_DL_TYPE) & ~(mul_nbapi.OFPFW_NW_DST_MASK)
        wildcards = mul_nbapi.OFPFW_ALL & ~(mul_nbapi.OFPFW_NW_SRC_MASK) & ~(mul_nbapi.OFPFW_DL_TYPE)
        prio = 0
        resp = mul_nbapi.add_static_flow(dpid,flow, wildcards, prio, action_list)
        
        # flow id hash table
        # flow_id -> flow, wildcards, dpid, prioiry
        
        if resp == 0 :
            flow_id = self.str_uuid()
            self.flow_tbl[flow_id] = [dpid, flow, wildcards, action_list[-1][0].port, prio]
        else :
	    pass
	return {'flow_id' : flow_id}
	
    def update_flow(self, conf, dpid, flow_id, params):
	pass

    def delete_flow(self, conf, dpid, flow_id):
	flow_arr = self.flow_tbl[flow_id]        
        resp = mul_nbapi.delete_static_flow(flow_arr[0], flow_arr[1], flow_arr[2], flow_arr[3], flow_arr[4])
        if resp == 0 :
            resp = flow_id
        return resp
	
    def get_all_switch(self, conf):
        resp = []
        try:
            resp = mul_nbapi.get_switch_all()
        except:
            return None
        return self.json_serializer.nbapi_switch_brief_list_t_serialization(resp)
    
    def get_switch(self, conf, dpid):
        resp = None
        
        try:
            con = mdb.connect("localhost", "root", "of#123", "skdemo")
            cur = con.cursor(mdb.cursors.DictCursor)
        except:
            print "[ERROR] Fail to connect DB"
            pass

        cur.execute("SELECT * FROM logicswitch WHERE logical_dpid = %s", dpid)
        logic = cur.fetchone()
        real_dpid = str(logic["dpid"])
        
        cur.close()
        con.close()
        try:
            resp = mul_nbapi.get_switch(int(real_dpid, 0))
        except:
            return None
	return self.json_serializer.ofp_switch_fetures_serialization(resp)
	
	
    def get_all_port(self, conf, dpid):
        resp = None
        
        try:
            con = mdb.connect("localhost", "root", "of#123", "skdemo")
            cur = con.cursor(mdb.cursors.DictCursor)
        except:
            print "[ERROR] Fail to connect DB"
            pass

        cur.execute("SELECT * FROM logicswitch WHERE logical_dpid = %s", dpid)
        logic = cur.fetchone()
        real_dpid = str(logic["dpid"])
        
        cur.close()
        con.close()
        try:
            resp = mul_nbapi.get_switch_port_all(int(real_dpid, 0))
        except:
            return None
	return self.json_serializer.nbapi_port_list_t_serialization(resp)
		
	
    def get_port(self, conf, dpid, port_id):
        resp = None

        try:
            con = mdb.connect("localhost", "root", "of#123", "skdemo")
            cur = con.cursor(mdb.cursors.DictCursor)
        except:
            print "[ERROR] Fail to connect DB"
            pass

        cur.execute("SELECT * FROM logicswitch WHERE logical_dpid = %s", dpid)
        logic = cur.fetchone()
        real_dpid = str(logic["dpid"])

        cur.close()
        con.close()
        try:
            resp = mul_nbapi.get_switch_port(int(real_dpid, 0), int(port_id))
        except:
            return None
	return self.json_serializer.ofp_phy_port_serialization(resp)
		
	
    def get_all_link(self, dpid):
	pass
	
    def get_link(self, conf, dpid):
        resp = None

        real_dpid = self.mapping_dpid_to_real(dpid)

        try:
            resp = mul_nbapi.get_switch_neighbor_all(int(real_dpid, 0))
        except:
            return None
        return {'ports':self.json_serializer.nbapi_port_neigh_list_t_serialization(resp, self.alias_map)}
    	
    def get_all_path(self, conf):
	pass
	
    def get_path(self, path_id):
	pass
	
    def get_all_host(self, conf, tenant_id, network_id):
        fab_host_list = None
        try:
            fab_host_list = mul_nbapi.get_fabric_host_all(1)
        except:
            return None
        return self.json_serializer.nbapi_fabric_host_list_t_serialization(fab_host_list)        
    
        

    def create_host(self, conf, tenant_id, network_id, params):
        resp = None
        host_id = None
        params['type'] = 'flow'
        #real_dpid = self.mapping_dpid_to_real(dpid)
        
        flow = self.json_deserializer.object_decoder(params)
        resp = mul_nbapi.add_fabric_host(int(params['dpid'],0), int(tenant_id) , int(network_id),
                                         flow, params['is_gw'])
        
        if resp > 0 :
            host_id = self.str_uuid()
            self.fab_host_tbl[host_id] = [int(params['dpid'],0), int(tenant_id), int(network_id), flow]
        else :
            return resp
        return {'host_id':host_id}
	
	
    def delete_host(self, conf, tenant_id, network_id, host_id):
        resp = None
        host_arr = self.fab_host_tbl[host_id]        
        resp = mul_nbapi.delete_fabric_host(host_arr[0], host_arr[1], host_arr[2], host_arr[3])
        if resp > 0 :
            resp = host_id
        return resp
	
	
    def get_host(self, conf, tenant_id, network_id, host_id):
	pass
	
    def update_host(self, conf, tenant_id, network_id, host_id, body):
	pass
	
    def get_all_stat(self, conf, dpid):
        flow_list = None
        
        real_dpid = self.mapping_dpid_to_real(dpid)
        try:
            flow_list = mul_nbapi.get_switch_statistics_all(int(real_dpid, 0))
        except:
            return None
        return {'flows':self.json_serializer.nbapi_switch_flow_list_t_serialization(flow_list)}   
    
    def stat_port_parse(self, flow_list, port_no):
        ingress={}
        egress={}
        ingress['type']='ingress'
        ingress['pkt_count']=0.0
        ingress['byte_count']=0.0
        ingress['avg_bps']=0.0
        ingress['avg_pps']=0.0
        ingress['flow_count']=0.0
        
        egress['type']='egress'
        egress['pkt_count']=0.0
        egress['byte_count']=0.0
        egress['avg_bps']=0.0
        egress['avg_pps']=0.0
        egress['flow_count']=0.0
        
        
        for flow in flow_list:
            if flow.flow.in_port == port_no:
                ingress['pkt_count']=ingress['pkt_count']+flow.packet_count
                ingress['byte_count']=ingress['byte_count']+flow.byte_count
                ingress['avg_bps']=ingress['avg_bps']+float(mul_nbapi.nbapi_parse_bps_to_str(flow.bps))
                ingress['avg_pps']=ingress['avg_pps']+float(mul_nbapi.nbapi_parse_pps_to_str(flow.pps))
                ingress['flow_count']=ingress['flow_count']+1
                
            if flow.oport == port_no:
                egress['pkt_count']=egress['pkt_count']+flow.packet_count
                egress['byte_count']=egress['byte_count']+flow.byte_count
                egress['avg_bps']=egress['avg_bps']+float(mul_nbapi.nbapi_parse_bps_to_str(flow.bps))
                egress['avg_pps']=egress['avg_pps']+float(mul_nbapi.nbapi_parse_pps_to_str(flow.pps))
                egress['flow_count']=egress['flow_count']+1
       
        if (ingress['flow_count'] != 0): 
            ingress['avg_pps']=ingress['avg_pps']/ingress['flow_count']
        if (egress['flow_count'] != 0):    
            egress['avg_pps']=egress['avg_pps']/egress['flow_count'] 
        
        
        return {'ingress':ingress, 'egress':egress}       

    def stat_all_port_parse(self, flow_list):
        """ Work from Chan"""
        stats = dict()
        result = list()
        port_list = dict()
        list_index = 0

        for flow in flow_list:
            
            stat = dict()

            stat['port_num'] = 0
            stat['in_pkt_count'] = 0
            stat['in_byte_count'] = 0
            stat['in_avg_bps'] = 0.0
            stat['in_avg_pps'] = 0.0
            stat['in_flow_count'] = 0
                
            stat['e_pkt_count'] = 0
            stat['e_byte_count'] = 0
            stat['e_avg_bps'] = 0.0
            stat['e_avg_pps'] = 0.0
            stat['e_flow_count'] =0
           
            if not flow.flow.in_port in port_list:
                port_list[flow.flow.in_port] = list_index
                result.append(stat.copy())
                result[list_index]['port_num'] = flow.flow.in_port
                list_index = list_index + 1
            
            if not flow.oport in port_list:
                port_list[flow.oport] = list_index
                result.append(stat.copy())
                result[list_index]['port_num'] = flow.oport
                list_index = list_index + 1
            
            in_index = port_list[flow.flow.in_port]
            result[in_index]['in_pkt_count'] += flow.packet_count
            result[in_index]['in_byte_count'] += flow.byte_count
            result[in_index]['in_avg_bps'] += float(mul_nbapi.nbapi_parse_bps_to_str(flow.bps))
            result[in_index]['in_avg_pps'] += float(mul_nbapi.nbapi_parse_bps_to_str(flow.pps))
            result[in_index]['in_flow_count'] += 1

            e_index = port_list[flow.oport]
            result[e_index]['e_pkt_count'] += flow.packet_count        
            result[e_index]['e_byte_count'] += flow.byte_count        
            result[e_index]['e_avg_bps'] += float(mul_nbapi.nbapi_parse_bps_to_str(flow.bps))
            result[e_index]['e_avg_pps'] += float(mul_nbapi.nbapi_parse_bps_to_str(flow.pps))
            result[e_index]['e_flow_count'] += 1

        for port in result:
            try:
                port['in_avg_bps'] = port['in_avg_bps'] / port['in_flow_count']
            except:
                port['in_avg_bps'] = 0

            try:
                port['in_avg_pps'] = port['in_avg_pps'] / port['in_flow_count']
            except:
                port['in_avg_pps'] = 0

            try:
                port['e_avg_bps'] = port['e_avg_bps'] / port['e_flow_count']
            except:
                port['e_avg_bps'] = 0

            try:
                port['e_avg_pps'] = port['e_avg_pps'] / port['e_flow_count']
            except:
                port['e_avg_pps'] = 0
        
        return result

    
    def get_stat_port(self, conf, dpid, port_no):        
        type_pps = 1
        str_dpid = str(dpid)
        port_num = int(port_no)
        pps = mul_nbapi.get_switch_statistics_port(int(str_dpid, 0), port_num, type_pps)

        if pps is None:
            return {"message" : "FAIL", "pps" : 0.0}

        return {"message" : "SUCCESS", "pps" : pps}
       
    
    def get_stat(self, conf, dpid, flow_id):
        pass

    def path_show_route_path(self, conf, version, src_dpid, src_port, dst_dpid, dst_port):
        src_sw = None
        dst_sw = None
        src_alias = None
        dst_alias = None
        path = None
        try:
            src_sw = mul_nbapi.get_switch(int(src_dpid, 0))
            dst_sw = mul_nbapi.get_switch(int(dst_dpid, 0))
            src_alias = mul_nbapi.get_switch_alias_from_switch_info(src_sw)
            dst_alias = mul_nbapi.get_switch_alias_from_switch_info(dst_sw)
            path = mul_nbapi.get_simple_path(src_alias,int(src_port, 0),dst_alias,int(dst_port, 0))
        except:
            return None
        
        return {'hops':self.json_serializer.nbapi_path_elem_list_t_serialization(path,self.alias_map)}
    
   
    """ Utility Function """
    def key_fields(self, controller_name, body):
        return {body[key] for key in self.db_collection[controller_name]['keys']}
    
    def get_obj_id(self, _id):
        return ObjectId(_id)
    
    def db_alive(self):
        return self.db_client.alive()
    
    def mongo_db_index_func(self, controller_name):
        if not self.db_alive():
            return  self.err.ERROR_DB_DISCONNET()
        return self.db[self.db_collection[controller_name]].find() 
    
    def mongo_db_show_func(self, controller_name, name):    
        if not self.db_alive():
            return self.err.ERROR_DB_DISCONNET() 
        return self.db[self.db_collection[controller_name]].find_one({'_id':self.get_obj_id(name)}) 
    
    def mongo_db_delete_func(self, controller_name, name):
        if not self.db_alive():
            return self.err.ERROR_DB_DISCONNET() 
        body = self.db[self.db_collection[controller_name]].find_one({'_id':self.get_obj_id(name)})
        if body is not None:
            self.db[self.db_collection[controller_name]].remove({'_id':self.get_obj_id(name)}) # return message:{'connectionId','ok','err','n'}            
            return body
        else:
            return self.err.ERROR_DB_NONEXIST()     

    
    def mongo_db_create_func(self, controller_name, body):  
        # TODO : Exception handling for specific APIs
        # ex) ServiceChainMgr : check wheather user request for the exist of body['nfv_group_list'], body['service_id']
        # NFVTopologyMgr : check exist of body['group_id'] in the db. 
        # ServiceChainDefaultRuleMgr : body['service_id'], body['service_level'], body['nfv_group_list']
        if self.db_collection[controller_name]['validator'].input_validation(body) != 0:
            return self.err.ERROR_INPUT_ARGS()    
        if not self.db_alive():
            return self.err.ERROR_DB_DISCONNET() 
        if self.db[self.db_collection[controller_name]].find_one(self.key_fields(controller_name, body)):
            return self.err.ERROR_DB_EXIST()
        else :
            body['id'] = self.str_uuid()
            self.db[self.db_collection[controller_name]].insert(body)
            return body['id']
        
    def mongo_db_update_func(self, controller_name, name, body):
        if not self.db_alive():
            return self.err.ERROR_DB_DISCONNET() 
        
        if self.db[self.db_collection[controller_name]].find_one({'_id':self.get_obj_id(name)}):
            self.db[self.db_collection[controller_name]].update({'_id':self.get_obj_id(name)}, body)
            return body['id']
        else :
            return self.err.ERROR_DB_NONEXIST()
        
    """ NFVTopologyMgr API """
    def index_nfvtopo(self, conf):               
        return self.mongo_db_index_func(self.db_collection['NFVTopologyMgr']['name'])                        
    
    def create_nfvtopo(self, conf, body):        
        nfv_uuid = self.mongo_db_create_func(self, self.db_collection['NFVTopologyMgr']['name'], body) 
        if nfv_uuid :
            try:
                mul_nbapi.NFVTopology_node_insert(body['group_id'], int(body['dpid'],0), int(body['in_port']),
                                              int(body['out_port']), str(body['name']), 0)
            except :
                return {"error" : self.err.MUL_NBAPI_ERROR()}
        else :
            return {"error" : nfv_uuid}
        return {"nfv_uuid":nfv_uuid}
    
    def update_nfvtopo(self, conf, name, body):
        nfv_uuid = self.mongo_db_update_func(self, self.db_collection['NFVTopologyMgr']['name'], name, body)
        if nfv_uuid :
            try:
                mul_nbapi.NFVTopology_node_update(body['group_id'], int(body['dpid'],0), int(body['in_port']),
                                              int(body['out_port']), str(body['name']), 0)
            except :
                return {"error" : self.err.MUL_NBAPI_ERROR()}
        else :
            return {"error" : nfv_uuid}
        return {"nfv_uuid":nfv_uuid}
    
    def delete_nfvtopo(self, conf, name):
        body = self.mongo_db_delete_func(self, self.db_collection['NFVTopologyMgr']['name'], name)
        if body :
            try:
                mul_nbapi.NFVTopology_node_remove(int(body['dpid'],0), int(body['in_port']),
                                                  int(body['out_port']), str(body['name']))
            except:
                return {"error" : self.err.MUL_NBAPI_ERROR()}
        else :
            return {"error" : body}
        return {"SUCCESS"}  
            
    
    def show_nfvtopo(self, conf, name):
        return self.mongo_db_show_func(self.db_collection['NFVTopologyMgr']['name'], name)
    
    
    
    # TODO: NFVGroupManager API    
    def index_nfvgroup(self, conf):        
        return self.mongo_db_index_func(self.db_collection['NFVGroupMgr']['name'])  
    
    def create_nfvgroup(self, conf, body):
        nfv_uuid = self.mongo_db_create_func(self, self.db_collection['NFVGroupMgr']['name'], body) 
        if nfv_uuid :
            try:
                mul_nbapi.NFVGroup_insert(str(body['name']))
            except :
                return {"error" : self.err.MUL_NBAPI_ERROR()}
        else :
            return {"error" : nfv_uuid}
        return {"nfv_uuid":nfv_uuid}
    
    def update_nfvgroup(self, conf, name, body):
        nfv_uuid = self.mongo_db_update_func(self, self.db_collection['NFVGroupMgr']['name'], name, body)
        if nfv_uuid :
            try:
                mul_nbapi.NFVGroup_update(str(body['name']))
            except :
                return {"error" : self.err.MUL_NBAPI_ERROR()}
        else :
            return {"error" : nfv_uuid}
        return {"nfv_uuid":nfv_uuid}
    
    def delete_nfvgroup(self, conf, name):
        body = self.mongo_db_delete_func(self, self.db_collection['NFVGroupMgr']['name'], name)
        if body :
            try:
                mul_nbapi.NFVGroup_remove(str(body['name']))
            except:
                return {"error" : self.err.MUL_NBAPI_ERROR()}
        else :
            return {"error" : body}
        return {"SUCCESS"} 
    
    def show_nfvgroup(self, conf, name):
        return self.mongo_db_show_func(self.db_collection['NFVGroupMgr']['name'], name)
   
   
    # TODO: ServiceChainManager API 
    def index_servicech(self, conf):        
        return self.mongo_db_index_func(self.db_collection['ServiceChainMgr']['name'])  
       
    def create_servicech(self, conf, body):
        chain_uuid = self.mongo_db_create_func(self, self.db_collection['ServiceChainMgr']['name'], body) 
        if chain_uuid :
            try:
                mul_nbapi.ServiceChain_insert(int(body['service_id']), int(body['ip']), body['nfv_group_list'])
            except :
                return {"error" : self.err.MUL_NBAPI_ERROR()}
        else :
            return {"error" : chain_uuid}
        return {"chain_uuid":chain_uuid}
    
    def update_servicech(self, conf, name, body):
        nfv_uuid = self.mongo_db_update_func(self, self.db_collection['ServiceChainMgr']['name'], name, body)
        if nfv_uuid :
            try:
                mul_nbapi.ServiceChain_update(str(body['name']))
            except :
                return {"error" : self.err.MUL_NBAPI_ERROR()}
        else :
            return {"error" : nfv_uuid}
        return {"nfv_uuid":nfv_uuid}

    def delete_servicech(self, conf, name):
        body = self.mongo_db_delete_func(self, self.db_collection['ServiceChainMgr']['name'], name)
        if body :
            try:
                mul_nbapi.ServiceChain_remove(str(body['name']))
            except:
                return {"error" : self.err.MUL_NBAPI_ERROR()}
        else :
            return {"error" : body}
        return {"SUCCESS"} 
 
    def show_servicech(self, conf, name):
        return self.mongo_db_show_func(self.db_collection['ServiceChainMgr']['name'], name)  
    
    
    # TODO: ServiceChainDefaultRuleManager API    
    def index_servicechaindefaultrule(self, conf):        
        return self.mongo_db_index_func(self.db_collection['ServiceChainDefaultRuleMgr']['name']) 
    
    def create_servicechaindefaultrule(self, conf, body):
        chaindefault_rule_uuid = self.mongo_db_create_func(self, self.db_collection['ServiceChainDefaultRuleMgr']['name'], body) 
        if chaindefault_rule_uuid :
            try:
                mul_nbapi.ServiceChainDefaultRule_insert(int(body['service_id']), int(body['service_level']), body['nfv_group_list'])
            except :
                return {"error" : self.err.MUL_NBAPI_ERROR()}
        else :
            return {"error" : chaindefault_rule_uuid}
        return {"default_rule_uuid":chaindefault_rule_uuid}
    
    def update_servicechaindefaultrule(self, conf, name, body):
        chaindefault_rule_uuid = self.mongo_db_update_func(self, self.db_collection['ServiceChainDefaultRuleMgr']['name'], name, body)
        if chaindefault_rule_uuid :
            try:
                mul_nbapi.ServiceChainDefaultRule_update(int(body['service_id']), int(body['service_level']), body['nfv_group_list'])
            except :
                return {"error" : self.err.MUL_NBAPI_ERROR()}
        else :
            return {"error" : chaindefault_rule_uuid}
        return {"default_rule_uuid":chaindefault_rule_uuid}
    
    def delete_servicechaindefaultrule(self, conf, name):
        body = self.mongo_db_delete_func(self, self.db_collection['ServiceChainDefaultRuleMgr']['name'], name)
        if body :
            try:
                mul_nbapi.ServiceChainDefaultRule_remove(int(body['service_id']), int(body['service_level']))
            except:
                return {"error" : self.err.MUL_NBAPI_ERROR()}
        else :
            return {"error" : body}
        return {"SUCCESS"} 
    
    def show_servicechaindefaultrule(self, conf, name):
        return self.mongo_db_show_func(self.db_collection['ServiceChainDefaultRuleMgr']['name'], name)    
    
    # TODO: TopologyManager API    
    def index_topology(self, conf):        
        return 
    
    def create_topology(self, conf, body):
        return
    
    def update_topology(self, conf, name, body):
        return
    
    def delete_topology(self, conf, name):
        return
    
    def show_topology(self, conf, name):
        return
    
    # TODO: ServiceManager API    
    def index_service(self, conf):        
        return self.mongo_db_index_func(self.db_collection['ServiceMgr']['name']) 
    
    def create_service(self, conf, body):
        service_uuid = self.mongo_db_create_func(self, self.db_collection['ServiceMgr']['name'], body) 
        if service_uuid :
            try:
                mul_nbapi.Service_insert(int(body['dpid'], 0), int(body['in_port']), int(body['out_port']), str(body['name']))
            except :
                return {"error" : self.err.MUL_NBAPI_ERROR()}
        else :
            return {"error" : service_uuid}
        return {"service_uuid":service_uuid}
    
    def update_service(self, conf, name, body):
        service_uuid = self.mongo_db_update_func(self, self.db_collection['ServiceMgr']['name'], name, body)
        if service_uuid :
            try:
                mul_nbapi.Service_update(int(body['dpid'], 0), int(body['in_port']), int(body['out_port']), str(body['name']))
            except :
                return {"error" : self.err.MUL_NBAPI_ERROR()}
        else :
            return {"error" : service_uuid}
        return {"service_uuid":service_uuid}
    
    def delete_service(self, conf, name):
        body = self.mongo_db_delete_func(self, self.db_collection['ServiceMgr']['name'], name)
        if body :
            try:
                mul_nbapi.Service_remove(int(body['dpid'], 0), int(body['in_port']), int(body['out_port']), str(body['name']))
            except:
                return {"error" : self.err.MUL_NBAPI_ERROR()}
        else :
            return {"error" : body}
        return {"SUCCESS"} 
    
    def show_service(self, conf, name):
        return self.mongo_db_show_func(self.db_collection['ServiceMgr']['name'], name)    
