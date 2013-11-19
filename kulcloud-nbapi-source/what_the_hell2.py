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
import json
import uuid
import pdb
import MySQLdb as mdb
import time


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

    
class mlapi(mlapi_base_v1.MlapiBaseV1):	
    def __init__(self):
        self.json_serializer = mlapi_json_serialization()
        self.json_deserializer = mlapi_json_deserialization()   
        self.flow_tbl={}   
        self.fab_host_tbl={}
        self.alias_map = {}
        self.default_user_ip = "1.1.1.1"
        self.sdn_mode = True
        self.default_table = {}
        self.create_default_rule(0, "ALL", {"nfv_list" : ["NAT"]})
        #pdb.set_trace()
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
        str_dpid = mapping_dpid_to_real(dpid)
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
    
    """ ServiceChain API """
   
    def get_all_servicech(self, conf):
        """ TODO: Extract the allocated service chain informations from DB """        
        try:
            con = mdb.connect('localhost', 'root', 'of#123', 'skdemo2')
            cur = con.cursor(mdb.cursors.DictCursor)
        except:
            print "[ERROR] Fail to connect DB"
            pass
            
        cur.execute("SELECT * FROM user")
        user_list = cur.fetchall()

        result_list = list()

        for user in user_list:
            result = self.get_servicech(conf, user["phone_num"])
            result_list.append(result)

        return result_list
 
    
    def checkAndDeleteServiceChainLog(self, chain_id):
        """ Work from Chan"""
        try:
            con = mdb.connect('localhost', 'root', 'of#123', 'skdemo2')
            cur = con.cursor(mdb.cursors.DictCursor)
        except:
            print "[ERROR] failed connecting to DB"
            pass

        cur.execute("DELETE FROM servicechainlog WHERE chain_id = %s", chain_id)
        con.commit()
        con.close()
    
    def insertServiceChainLog(self, chain_id, nfv_name, nfv_order):
        """ Work from Chan"""
        try:
            con = mdb.connect('localhost', 'root', 'of#123', 'skdemo2')
            cur = con.cursor(mdb.cursors.DictCursor)
        except:
            print "[ERROR] failed connecting to DB"
            pass

        cur.execute("INSERT INTO servicechainlog VALUES ('%s', '%s' , '%s')" % (chain_id, nfv_name, nfv_order))
        con.commit()
        con.close()

    def insertORUpdateServiceChainLog(self, chain_id, nfv_name, nfv_order):
        """ Work from Chan"""
        try:
            con = mdb.connect('localhost', 'root', 'of#123', 'skdemo2')
            cur = con.cursor(mdb.cursors.DictCursor)
        except:
            print "[ERROR] failed connecting to DB"
            pass

        cur.execute("SELECT * FROM servicechainlog WHERE chain_id = %s", chain_id)
        row = cur.fetchone()
        
        if not row:
            cur.execute("INSERT INTO servicechainlog VALUES ('%s', '%s' , '%s')" % (chain_id, nfv_name, nfv_order))
            con.commit()
        else:
            print "[WARNING] update servicechainlog"
            cur.execute("UPDATE servicechainlog SET nfv_name = %s, nfv_order = %s WHERE chain_id = %s", (nfv_name, nfv_order, chain_id))
            con.commit()

        con.close()

    def init_ippool_address(self, userid):
        """ Work from Chan"""
        try:
            con = mdb.connect('localhost', 'root', 'of#123', 'skdemo2')
            cur = con.cursor(mdb.cursors.DictCursor)
        except:
            print "[ERROR] DB Connection Fail"
            pass

        cur.execute("UPDATE ippool SET user_id = 0 WHERE user_id = %s", userid)
        con.commit()
        con.close()

    def controller_call_for_flowadd(self, cur, chain_id, dpid, sip, dip, in_port, out_port, wildcards, prior, allocIP, src_vlan=0, dst_vlan = 0, is_set = False, is_strip = False, is_voms = False, is_nat = False, is_ovs=False,start_mac=None):
        """ Work from Chan"""
        VOMS_MAC = 'ac:16:2d:bb:b0:98'
        NAT_MAC = '00:26:66:d5:c1:cc'
        
        """ This Code is modified by Backguyn : 20130928 """
        cur.execute("SELECT dpid FROM logicswitch WHERE logical_dpid = %s", dpid)
        real_dpid = cur.fetchone()
        c_dpid = int(real_dpid['dpid'], 0)
        """ modified end """
        db_query = None
        #if not sip:
        #    wildcards = mul_nbapi.OFPFW_ALL & ~(mul_nbapi.OFPFW_NW_DST_MASK) & ~(mul_nbapi.OFPFW_DL_TYPE) & ~(mul_nbapi.OFPFW_IN_PORT)
        #else :
        #    wildcards = mul_nbapi.OFPFW_ALL & ~(mul_nbapi.OFPFW_NW_SRC_MASK) & ~(mul_nbapi.OFPFW_DL_TYPE) & ~(mul_nbapi.OFPFW_IN_PORT) 
        
        #flow = mul_nbapi.nbapi_flow_make_flow(str(obj['nw_src']), str(obj['nw_dst']), int(obj['in_port']), int(obj['dl_vlan']), int(obj['dl_type']), int(obj['tp_src']), int(obj['tp_dst']), str(obj['dl_src']), str(obj['dl_dst']), int(obj['dl_vlan_pcp']), int(obj['nw_tos']), int(obj['nw_proto']))
        if sip != None :
            sip = str(sip)
        if dip != None :
            dip = str(dip)

        #flow = mul_nbapi.nbapi_flow_make_flow(sip, dip, in_port, src_vlan, 0x0800, 0, 0, None, None, 0, 0, 0)
        action_list = []
        if is_ovs:
            action_list.append(mul_nbapi.nbapi_make_action_set_smac(str(start_mac)))
        if allocIP:
            # In the case of the first hop switch from the SSG : IP addr change.
            # Add the mapping logic between inport and service mac
            if not sip:
                action_list.append(mul_nbapi.nbapi_make_action_set_nw_daddr(str(allocIP)))
                flow = mul_nbapi.nbapi_flow_make_flow(sip, dip, in_port, src_vlan, 0x0800, 0, 0, None, None, 0, 0, 0)    # KONG Add
            else :
                action_list.append(mul_nbapi.nbapi_make_action_set_nw_saddr(str(allocIP)))
                flow = mul_nbapi.nbapi_flow_make_flow(sip, dip, in_port, src_vlan, 0x0800, 0, 0, None, str(start_mac), 0, 0, 0)    # KONG Add
            if not sip:
                cur.execute("INSERT INTO servicechainrule (chain_id, sip, dip, inport, outport, dpid, vlan, wildcard, prior, smac) VALUES (%s, NULL, %s, %s, %s, %s, %s, %s, %s, NULL)", (chain_id, dip, in_port, out_port, dpid, src_vlan, wildcards, prior))
            else:
                cur.execute("INSERT INTO servicechainrule (chain_id, sip, dip, inport, outport, dpid, vlan, wildcard, prior, smac) VALUES (%s, %s, NULL, %s, %s, %s, %s, %s, %s, %s)", (chain_id, sip, in_port, out_port, dpid, src_vlan, wildcards, prior, str(start_mac)))
                

        else :
            if is_set :
                flow = mul_nbapi.nbapi_flow_make_flow(sip, dip, in_port, src_vlan, 0x0800, 0, 0, None, None, 0, 0, 0)    # KONG Add
                if not sip:
                    cur.execute("INSERT INTO servicechainrule (chain_id, sip, dip, inport, outport, dpid, vlan, wildcard, prior, smac) VALUES (%s, NULL, %s, %s, %s, %s, %s, %s, %s, NULL)", (chain_id, dip, in_port, out_port, dpid, src_vlan, wildcards, prior))
                else:
                    cur.execute("INSERT INTO servicechainrule (chain_id, sip, dip, inport, outport, dpid, vlan, wildcard, prior, smac) VALUES (%s, %s, NULL, %s, %s, %s, %s, %s, %s, NULL)", (chain_id, sip, in_port, out_port, dpid, src_vlan, wildcards, prior))
            else :
                flow = mul_nbapi.nbapi_flow_make_flow(sip, dip, in_port, dst_vlan, 0x0800, 0, 0, None, None, 0, 0, 0)    # KONG Add
                if not sip:
                    cur.execute("INSERT INTO servicechainrule (chain_id, sip, dip, inport, outport, dpid, vlan, wildcard, prior, smac) VALUES (%s, NULL, %s, %s, %s, %s, %s, %s, %s, NULL)", (chain_id, dip, in_port, out_port, dpid, dst_vlan, wildcards, prior))
                else:
                    cur.execute("INSERT INTO servicechainrule (chain_id, sip, dip, inport, outport, dpid, vlan, wildcard, prior, smac) VALUES (%s, %s, NULL, %s, %s, %s, %s, %s, %s, NULL)", (chain_id, sip, in_port, out_port, dpid, dst_vlan, wildcards, prior))
        
        if is_set:
            action_list.append(mul_nbapi.nbapi_make_action_set_vid(int(dst_vlan)))
        if is_strip:
            action_list.append(mul_nbapi.nbapi_make_action_strip_vlan())
        if is_voms:
            action_list.append(mul_nbapi.nbapi_make_action_set_dmac(str(VOMS_MAC)))
            action_list.append(mul_nbapi.nbapi_make_action_set_vid(int(0)))
        if is_nat:
            action_list.append(mul_nbapi.nbapi_make_action_set_dmac(str(NAT_MAC)))
            action_list.append(mul_nbapi.nbapi_make_action_set_vid(int(0)))
        
        action_list.append(mul_nbapi.nbapi_make_action_output(int(out_port)))       

        #wildcards = mul_nbapi.OFPFW_ALL & ~(mul_nbapi.OFPFW_NW_SRC_MASK) & ~(mul_nbapi.OFPFW_DL_TYPE) & ~(mul_nbapi.OFPFW_NW_DST_MASK)
        resp = mul_nbapi.add_static_flow(c_dpid, flow, wildcards, prior, action_list)
               
        if resp == 0:
            return
        else:
            print "[ERROR] during Flow add"
            return
  
    def create_servicech(self, conf, params):
        """ Work from Chan""" 
        cur = None
        try:
            con = mdb.connect('localhost', 'root', 'of#123', 'skdemo2')
            cur = con.cursor(mdb.cursors.DictCursor)
        except:
            print "[ERROR] DB Connection Fail"
            pass

        """
        params parsing
        """
        user_id = 0
        user_ip = params["ip"]
        user_phone_num = params["mdn"]
        user_service_level = params["service_level"]

        #define result form
        result = {"ip":user_ip, "mdn":user_phone_num, "service_level":user_service_level, "services":[], "message":""}

        #get user id
        #cur.execute("SELECT userid FROM user WHERE userip = %s AND phone_num = %s", (user_ip, user_phone_num))
        cur.execute("SELECT * FROM user WHERE userip = %s", (user_ip))
        row = cur.fetchone()
        if not row:
            #insert user db
            cur.execute("SELECT userid FROM user ORDER BY userid DESC LIMIT 1")
            row1 = cur.fetchone()
            user_id = row1["userid"] + 1

            cur.execute("INSERT INTO user VALUES(%s, %s, %s, %s, %s)", (user_id, user_ip, user_phone_num, user_service_level, 1))
            con.commit()
        else:
            print "[WARNING] already registered"
            user_id = row["userid"]

            if row["phone_num"] != user_phone_num:
                cur.execute("SELECT * FROM user WHERE phone_num = %s", user_phone_num)
                temp = cur.fetchone()
                if not temp:
                    cur.execute("UPDATE user SET phone_num = %s WHERE userip = %s", (user_phone_num, user_ip))
                    con.commit()
                else:
                    print "[ERROR] already registered phone_num"
                    return {"message" : "FAIL"}

            if row['service_level'] != user_service_level:
                print "[WARING] update user service level"
                cur.execute("UPDATE user SET service_level = %s WHERE userid = %s", (user_service_level, user_id))
            #result["message"] = "FAIL"
            #return result
            cur.execute("UPDATE user SET active = 1 WHERE userid = %s", user_id)
            con.commit()
        
        cur.execute("SELECT * FROM sa")
        rows = cur.fetchall()

        #cur.execute("SELECT nfv FROM defaultRule ORDER BY nfv_order ASC")
        #defaults = cur.fetchall()
        cur.execute("SELECT chain_id, service_id FROM ippool WHERE user_id IN (SELECT userid FROM user WHERE userip = %s)", self.default_user_ip)
        default_chain_list = cur.fetchall()

        #default_list = {"nfv_list" : []}
        #for default in defaults:
            #default_list["nfv_list"].append(default["nfv"])

        for chain in default_chain_list:
        #for row in rows:
            cur.execute("SELECT * FROM servicechainlog WHERE chain_id = %s", chain["chain_id"])
            default_list = cur.fetchall()
            if not default_list:
                self.create_default_rule(conf, "ALL", {"nfv_list" : ["NAT"]})
            nfv_list = {"nfv_list" : []}
            #pdb.set_trace()
            for default in default_list:
                nfv_list["nfv_list"].append(default["nfv_name"])
            
            cur.execute("SELECT * FROM sa WHERE service_id = %s", chain["service_id"])
            service = cur.fetchone()
            node = self.create_service(conf, user_phone_num, service["service_type"], nfv_list)
            if node["message"] != "SUCCESS":
                print "[ERROR] user service create fail"
                result["message"] = "FAIL"
                return result

            result["services"].append(node["services"])
        
        result["message"] = "SUCCESS"
        return result



    def delete_servicech(self, conf, phone_num):
        """ 2013-09-12 Work from Backguyn """
        try:
            con = mdb.connect('localhost', 'root', 'of#123', 'skdemo2')
            cur = con.cursor(mdb.cursors.DictCursor)
        except:
            print "[ERROR] DB Connection Fail"
            pass

        cur.execute("SELECT * FROM user WHERE phone_num = %s", phone_num)
        user = cur.fetchone()

        result = {"message" : "SUCCESS"}
        
        if not user:
            print "[ERROR] This user is not on the DB"
            result["message"] = "E_MSG5"
            return result
       
        cur.execute("UPDATE user SET active = 0 WHERE phone_num = %s", phone_num)
        con.commit()

        return result

 
    def get_servicech(self, conf, phone_num):
        """ Work from Chan"""
        try:
            con = mdb.connect('localhost', 'root', 'of#123', 'skdemo2')
            cur = con.cursor(mdb.cursors.DictCursor)
        except:
            print "[ERROR] DB Connection Fail"
            pass

        """
        params parsing
        """
        user_phone_num = phone_num
        #define result form
        result = {"ip":"", "mdn":user_phone_num, "service_level":"", "services":[], "message":""}

        cur.execute("SELECT * FROM user WHERE phone_num = %s", user_phone_num)
        row = cur.fetchone()

        if not row:
            print "[ERROR] can not find user"
            result["message"] = "E_MSG5"
            return result
        
        result["ip"] = row["userip"]
        result["service_level"] = row["service_level"]
        user_id = row["userid"]
        
        cur.execute("SELECT * FROM servicechainlog as a, ippool as b, sa as c WHERE a.chain_id = b.chain_id AND b.service_id = c.service_id AND b.user_id = %s AND a.nfv_order = 0 ORDER BY a.chain_id, a.nfv_order", user_id)
        rows = cur.fetchall()
      
        for row in rows:
            result["services"].append({"service_type":row["service_type"], "service_chain_id":row["chain_id"], "service_ip":row["ip"]})

        #print result

        result["message"] = "SUCCESS"
        return result

    def update_servicech(self, conf, phone_num, body):
        pass  
    
    def show_service_chain_list(self, conf, service_chain_id):
        """ Work from Chan"""
        try:
            con = mdb.connect('localhost', 'root', 'of#123', 'skdemo2')
            cur = con.cursor(mdb.cursors.DictCursor)
        except:
            print "[ERROR] DB Connection Fail"
            pass

        result = dict()
        result["nfv_list"] = []

        if service_chain_id == "all":
            cur.execute("SELECT * FROM ippool WHERE user_id != 0")
            rows = cur.fetchall()

            for row in rows:
                service_list = self.show_service_chain_list(conf, row["chain_id"])          
                if service_list.has_key("message"):
                    pass
                else:
                    result["nfv_list"] += service_list["nfv_list"]

            return result
        else:
            cur.execute("SELECT * FROM ippool WHERE user_id != 0 AND chain_id = %s", service_chain_id)
            row = cur.fetchone()
            if not row:
                message = "This chain_id is not used"
                return {"message" : message}

            cur.execute("SELECT * FROM servicechainlog as a, nfv as b WHERE a.chain_id = %s AND a.nfv_name = b.nfv", service_chain_id)
            rows = cur.fetchall()
       
            if not rows:
                cur.execute("SELECT * FROM defaultRule as a, nfvvm as b, nfv as c WHERE a.nfv = c.nfv AND b.nfv_id = c.nfv_id")
                rows = cur.fetchall()
                if not rows:
                    return {"message" : "FAIL"}

            for row in rows:
                cur.execute("SELECT dpid FROM nfvvm WHERE nfv_id = %s", row["nfv_id"])
                dpid = cur.fetchone()
                result["nfv_list"].append({"name":row["nfv"],"DPID":dpid["dpid"], "chain_id":service_chain_id})
            
        return result   

    def show_statistic_service_chain(self, conf, service_chain_id):
        """ Work from Chan"""
        try:
            con = mdb.connect('localhost', 'root', 'of#123', 'skdemo2')
            cur = con.cursor(mdb.cursors.DictCursor)
        except:
            print "[ERROR] DB Connection Fail"
            pass
        
        cur.execute("SELECT * FROM servicechainrule WHERE chain_id = %s", service_chain_id)
        
        rows = cur.fetchall()

        result = dict()
        result['flows'] = []
        default_chain_id = False

        if not rows:
            #print "[ERROR] cannot find chain_id"
            cur.execute("SELECT * FROM user WHERE userip = %s", self.default_user_ip)
            default_user = cur.fetchone()

            cur.execute("SELECT * FROM servicechainlog as a, ippool as b WHERE a.chain_id = %s AND a.chain_id = b.chain_id AND b.user_id = %s", (service_chain_id, default_user["userid"]))
            rows = cur.fetchall()
            default_chain_id = True
            
            if not rows:
                result['message'] = "FAIL"
                return result

        if default_chain_id is True:
            cur.exeute("SELECT chain_id FROM servicechainlog WHERE nfv_name IN (SELECT nfv_name FROM servicechainlog WHERE chain_id = %s) GROUP BY chain_id", service_chain_id)
            chain_list = cur.fetchall()
            for chain in chain_list:
                cur.execute("SELECT chain_id FROM servicechainrule WHERE chain_id = %s GROUP BY chain_id", chain["chain_id"])
                rule = cur.fetchone()
                if not rule:
                    continue
                else:
                    node = self.show_statistic_service_chain(conf, rule["chain_id"])
                    if node["message"] == "SUCCESS":
                        break
            if node["message"] != "SUCCESS":
                return {"message" : "FAIL"}

            return node
                    
            
        for row in rows:
            c_dpid = row['dpid']
            in_port = row['inport']
            out_port = row['outport']
            vlan = row['vlan']
            wildcards = row['wildcard']
            prior = row['prior']
            sip = row['sip']
            dip = row['dip']
            smac = row['smac']
        
            cur.execute("SELECT dpid FROM logicswitch WHERE logical_dpid = %s", c_dpid)
            real_dpid = cur.fetchone()
            dpid = real_dpid['dpid']

            """ modified by backguyn 20131003 """
            cur.execute("SELECT nfv_name FROM nfvvm WHERE dpid = %s AND (in_port = %s OR in_port = %s OR out_port = %s OR out_port = %s)", (c_dpid, in_port, out_port, in_port, out_port))
            nfvvm = cur.fetchone()
            
            if not nfvvm:
                cur.execute("SELECT dpid FROM sa WHERE dpid = %s AND (in_port = %s OR out_port = %s)", (c_dpid, out_port, in_port))
                sa = cur.fetchone()
                if not sa:
                    continue

                nfv_vm_name = "start"
            else:
                nfv_vm_name = nfvvm["nfv_name"]

            try:
                if vlan is None:
                    if smac is None:
                        fl = mul_nbapi.nbapi_flow_make_flow(sip, dip, int(in_port), 0, 0x0800, 0, 0, None, None, 0, 0, 0)
                    else:
                        fl = mul_nbapi.nbapi_flow_make_flow(sip, dip, int(in_port), 0, 0x0800, 0, 0, None, str(smac), 0, 0, 0)
                else :
                    if smac is None:
                        fl = mul_nbapi.nbapi_flow_make_flow(sip, dip, int(in_port), int(vlan), 0x0800, 0, 0, None, None, 0, 0, 0)
                    else:
                        fl = mul_nbapi.nbapi_flow_make_flow(sip, dip, int(in_port), int(vlan), 0x0800, 0, 0, None, str(smac), 0, 0, 0)
                stats = mul_nbapi.get_flow_statistics(int(dpid,0), fl, wildcards, int(out_port), int(prior))
            except:
                print "[ERROR] during get flowinfo from controller"
                result['message'] = "FAIL"
                return result
            if stats is None:
                #print "[ERROR] there is no matched flow entry"
                result['message'] = "FAIL"
                return result
                
            #res = dict()
            #res['flow_info'] = dict()
            #res['flow_info']['sip'] = sip
            #res['flow_info']['dip'] = dip
            #res['flow_info']['inport'] = in_port
            #res['flow_info']['outport'] = out_port
            #res['flow_info']['dpid'] = dpid
            #res['flow_info']['vlan'] = vlan

            #res['flow_detail'] = dict()
            #res['flow_detail']['byte_count'] = stats.byte_count
            #res['flow_detail']['pkt_count'] = stats.packet_count
            #res['flow_detail']['avg_bps'] = mul_nbapi.nbapi_parse_bps_to_str(stats.bps)
            #res['flow_detail']['avg_pps'] = mul_nbapi.nbapi_parse_bps_to_str(stats.pps)

            res = dict()
            res['nfv_name'] = nfv_vm_name
            res['inport'] = in_port
            res['outport'] = out_port
            res['sip'] = sip
            res['dip'] = dip
            res['dpid'] = c_dpid
            res['vlan'] = vlan
            res['byte_count'] = stats.byte_count
            res['pkt_count'] = stats.packet_count
            res['avg_bps'] = mul_nbapi.nbapi_parse_bps_to_str(stats.bps)
            res['avg_pps'] = mul_nbapi.nbapi_parse_bps_to_str(stats.pps)
            result['flows'].append(res)
         
        result['message'] = "SUCCESS"
        return result


    """ Service API """
    def get_all_service(self, conf, phone_num):
        """ TODO: Extract the allocated service chain informations from DB """        
        pass
    
    def create_service(self, conf, phone_num, service_type, params, updatelog=False):
        """ Work from Chan"""
        """ COMMENT: [CAUTION]actually this logic going Food... so complicated :("""
        voms_nfv_id = 5
        nat_nfv_id = 8
        try:
            con = mdb.connect('localhost', 'root', 'of#123', 'skdemo2')
            cur = con.cursor(mdb.cursors.DictCursor)
        except:
            print "[ERROR] DB Connection Fail"
            pass
        
        """
        params parsing
        """
        user_phone_num = phone_num
        user_service_type = service_type

        #define result form
        result = {"ip":"", "mdn":user_phone_num, "service_level":"", "services":{}, "message":""}
        
        #delete DB - 'servicechainrule'
        #self.change_sdn_mode(conf, True)

        active = 1
        if user_phone_num == "ALL":
            active = 0

        cur.execute("SELECT * FROM user WHERE phone_num = %s AND active = %s", (user_phone_num, active))
        row = cur.fetchone()

        if not row:
            print "[ERROR] can not find user"
            result["message"] = "[ERROR] can not find user"
            return result
        
        user_ip = row["userip"]
        result["ip"] = user_ip
        result["service_level"] = row["service_level"]
        user_id = row["userid"]
        lnfv = params["nfv_list"]

        #pdb.set_trace()
        if updatelog is False and (lnfv[-1] != "VOMS" and lnfv[-1] != "NAT"):
            lnfv.append("NAT")
            
        """
        NFV Service level check
        """
        user_service_level = row["service_level"]
        for nfv in lnfv:
            cur.execute("SELECT service_level FROM nfv WHERE nfv = %s", nfv)
            row = cur.fetchone()

            if not row:
                message =  "[ERROR] can not find %s nfv" 
                result["message"] = message
                return result
            
            if row["service_level"] > user_service_level:
                message = "[ERROR] this user not satisfied the NFV service level"
                result["message"] = message
                return result
        
        """
        Service IP Pool Registration
        """
        cur.execute("SELECT service_id, service_type FROM sa WHERE service_type = %s AND active = 1", user_service_type)
        row = cur.fetchone()
        if not row:
            print "[ERROR] can not find service_type"
            result["message"] = "FAIL"
            return result

        result["services"] = {"service_type":row["service_type"], "service_chain_id":0, "nfv_list":[]}
        service_id = row["service_id"]

        cur.execute("SELECT * FROM ippool WHERE service_id = %s AND user_id = %s", (service_id, user_id))
        row1 = cur.fetchone()
        if not row1:
            cur.execute("SELECT * FROM ippool WHERE service_id = %s AND user_id = 0 ORDER BY chain_id LIMIT 1", row["service_id"])
            row2 = cur.fetchone()
            if not row2:
                print "[ERROR] not enough for assigning Service IP Address"
                result["message"] = "FAIL"
                return result
                
            service_chain_id = row2["chain_id"]
            service_ip = row2["ip"]
            cur.execute("UPDATE ippool SET user_id = %s WHERE chain_id = %s", (user_id, service_chain_id))
            con.commit()

        else:
            service_chain_id = row1["chain_id"]
            service_ip = row1["ip"]

        if phone_num == "ALL":
            self.default_table[service_id] = service_chain_id
        #update result form
        result["services"]["service_chain_id"] = service_chain_id
             
        """
        #TODO: for multiple Services input
        lnfv = []
        #init listNFV
        for i in range(length):
            lnfv.append([])
        ServiceNumber = 0

        #input listNFV
        for i in range(2, length):
            if (sys.argv[i].isdigit()):
                ServiceNumber = int(sys.argv[i])
            else:
                lnfv[ServiceNumber].append(sys.argv[i])
        """

        MAXIMUM_HOP = 100

        """
        service loop
        """
        cur.execute("SELECT * FROM sa WHERE service_id = '%d' AND active = 1" % service_id)
        row = cur.fetchone()

        if not row:
            print "[ERROR] can not find service_type"
            result["message"] = "FAIL"
            return result
        # KONG Debug 2013-09-02 : vlan wild card modify
        d_wildcards = mul_nbapi.OFPFW_ALL & ~(mul_nbapi.OFPFW_NW_DST_MASK) & ~(mul_nbapi.OFPFW_DL_TYPE) & ~(mul_nbapi.OFPFW_IN_PORT) & ~(mul_nbapi.OFPFW_DL_VLAN)
        s_wildcards = mul_nbapi.OFPFW_ALL & ~(mul_nbapi.OFPFW_NW_SRC_MASK) & ~(mul_nbapi.OFPFW_DL_TYPE) & ~(mul_nbapi.OFPFW_IN_PORT) & ~(mul_nbapi.OFPFW_DL_VLAN)

        start_dpid = row["dpid"]
        start_inport = row["in_port"]
        start_outport = row["out_port"]
        s_serviceIP = service_ip
        d_serviceIP = service_ip
        chain_id = service_chain_id
        start_mac = row["mac"]

        #result value
        s_s_inport = 0
        s_s_outport = start_inport
        s_d_inport = start_outport
        s_d_outport = 0
        s_dpid = start_dpid
        stopper = 0 
        src_nfv_vlan = 10
        dst_nfv_vlan = 10
        prev_dpid_type = 'physical'
        
        if updatelog is False:
            #self.checkAndDeleteServiceChainLog(chain_id)
            self.delete_service(conf, chain_id)
        #for debug
        #truncate servicechainrule
        else:
            cur.execute("DELETE FROM servicechainrule WHERE chain_id = %s", chain_id)
        #con.commit()
        for i in range(len(lnfv)):
            if not lnfv[i]:
                break
            else:
                #cur.execute("SELECT * FROM nfv as a, nfvvm as b WHERE a.nfv_id = b.nfv_id AND a.nfv = '%s' AND b.active = 1 ORDER BY b.active_threshold ASC, b.nfv_vm_id ASC LIMIT 1" % lnfv[i])
                """
                cur.execute("SELECT * FROM nfv as a, nfvvm as b, nfvvmStatus as c, nfvvmThreshold as d  WHERE a.nfv_id = b.nfv_id AND a.nfv = '%s' AND b.nfv_vm_id = c.nfv_vm_id AND d.nfv_id = a.nfv_id ORDER BY b.nfv_vm_id" % lnfv[i])
                row_result = cur.fetchall()
                for vm in row_result :
                    if vm["out_port_pps"] < vm["inport_pps_threshold"]:
                        row=vm
                        break
                """
                cur.execute("SELECT * FROM nfv as a, nfvvm as b WHERE a.nfv_id = b.nfv_id AND a.nfv = %s ORDER BY b.active_threshold ASC, b.nfv_vm_id ASC LIMIT 1", lnfv[i])
                row = cur.fetchone()
                nfv = row["nfv"]
                nfv_id = row["nfv_id"]
                nfv_name = row["nfv_name"]
                endnfv_dpid = row["dpid"]
                endnfv_inport = row["in_port"]
                endnfv_outport = row["out_port"]
                nfv_type = row["type"]
                
                src_nfv_vlan = dst_nfv_vlan
                dst_nfv_vlan = row["vlan"]
                prev_dpid = s_dpid
                    
                #for vlan
                # KONG Debug 2013-09-02
                #if (i == (len(lnfv)-1)):
                #    is_vlan_tagging = False
                #    is_strip_f = False
                #    is_strip_l = True
                #elif (i == 0):
                #    is_vlan_tagging = False
                #    is_strip_f = True
                #    is_strip_l = False
                #else:
                #    is_vlan_tagging = True
                #    is_strip_f = False
                #    is_strip_l = False
                is_vlan_tagging = True
                is_strip_f = False
                is_strip_l = False

                firstloopOfnfv = True 

                result["services"]["nfv_list"].append(nfv_name)
                if updatelog is False:
                    self.insertServiceChainLog(chain_id, nfv, i)
                    if user_ip == self.default_user_ip:
                        continue
                
                if row["active"] == 0:
                    cur.execute("UPDATE nfvvm SET active = 1 WHERE nfv_vm_id = %s", row["nfv_vm_id"])
                    cur.execute("UPDATE nfvvm SET active_threshold = 0 WHERE active_threshold = 1")
                    con.commit()

                while True:
                    s_serviceIP = service_ip
                    allocIP_src = None
                    allocIP_dst = None
                    s_wildcards = mul_nbapi.OFPFW_ALL & ~(mul_nbapi.OFPFW_NW_SRC_MASK) & ~(mul_nbapi.OFPFW_DL_TYPE) & ~(mul_nbapi.OFPFW_IN_PORT) & ~(mul_nbapi.OFPFW_DL_VLAN)
                    d_wildcards = mul_nbapi.OFPFW_ALL & ~(mul_nbapi.OFPFW_NW_DST_MASK) & ~(mul_nbapi.OFPFW_DL_TYPE) & ~(mul_nbapi.OFPFW_IN_PORT) & ~(mul_nbapi.OFPFW_DL_VLAN)
                    #always doing once in last per NFV
                    if s_dpid == endnfv_dpid:
                        #when absolutely first
                        if (s_dpid == start_dpid) and (stopper < 1):
                            s_s_inport = start_outport
                            s_s_outport = row["in_port"]
                            s_d_inport = row["out_port"]
                            s_d_outport = start_inport
                            allocIP_src = service_ip
                            allocIP_dst = user_ip
                            s_serviceIP = user_ip
                            stopper += 1
                        #when first of nfv
                        elif firstloopOfnfv:
                            s_s_inport = s_d_inport
                            s_d_outport = s_s_outport
                            s_s_outport = row["in_port"]
                            s_d_inport = row["out_port"]
                            firstloopOfnfv = False
                        else:
                            s_s_inport = s_s_outport
                            s_s_outport = endnfv_inport
                            s_d_outport = s_d_inport
                            s_d_inport = endnfv_outport

                        if is_vlan_tagging:
                            #print "sip:%s, dip:%s, dpid:%s, vlan:%s, in_port:%s, out_port:%s nfv_name:%s" % (s_serviceIP, 0, s_dpid, src_nfv_vlan, s_s_inport, s_s_outport, nfv_name)
                            #print "sip:%s, dip:%s, dpid:%s, vlan:%s, in_port:%s, out_port:%s, is_set:True" % (0, d_serviceIP, s_dpid, dst_nfv_vlan, s_d_inport, s_d_outport)
                            #self.controller_call_for_flowadd(s_dpid, s_serviceIP, None, s_s_inport, s_s_outport, s_wildcards, 1, allocIP_src, src_nfv_vlan)
                            #self.controller_call_for_flowadd(s_dpid, None, d_serviceIP, s_d_inport, s_d_outport, d_wildcards, 1, allocIP_dst, dst_nfv_vlan, True)
                            if (nfv_id == voms_nfv_id) and (i==len(lnfv)-1) :
                                d_wildcards = mul_nbapi.OFPFW_ALL & ~(mul_nbapi.OFPFW_NW_DST_MASK) & ~(mul_nbapi.OFPFW_DL_TYPE) & ~(mul_nbapi.OFPFW_IN_PORT) 
                                self.controller_call_for_flowadd(cur, chain_id, s_dpid, s_serviceIP, None, s_s_inport, s_s_outport, s_wildcards, 1, allocIP_src, src_nfv_vlan, dst_nfv_vlan, False, False, True)
                                self.controller_call_for_flowadd(cur, chain_id, s_dpid, None, d_serviceIP, s_d_inport, s_d_outport, d_wildcards, 1, allocIP_dst, dst_nfv_vlan, src_nfv_vlan, True)
                            elif (nfv_id == nat_nfv_id) and (i==len(lnfv)-1) :
                                d_wildcards = mul_nbapi.OFPFW_ALL & ~(mul_nbapi.OFPFW_NW_DST_MASK) & ~(mul_nbapi.OFPFW_DL_TYPE) & ~(mul_nbapi.OFPFW_IN_PORT) 
                                self.controller_call_for_flowadd(cur, chain_id, s_dpid, s_serviceIP, None, s_s_inport, s_s_outport, s_wildcards, 1, allocIP_src, src_nfv_vlan, dst_nfv_vlan, False, False, False, True)
                                self.controller_call_for_flowadd(cur, chain_id, s_dpid, None, d_serviceIP, s_d_inport, s_d_outport, d_wildcards, 1, allocIP_dst, dst_nfv_vlan, src_nfv_vlan, True)
                            #elif (i==0) :
                            #    self.controller_call_for_flowadd(cur, chain_id, s_dpid, s_serviceIP, None, s_s_inport, s_s_outport, s_wildcards, 1, allocIP_src, src_nfv_vlan, dst_nfv_vlan, True)
                            #    self.controller_call_for_flowadd(cur, chain_id, s_dpid, None, d_serviceIP, s_d_inport, s_d_outport, d_wildcards, 1, allocIP_dst, dst_nfv_vlan, src_nfv_vlan, True)
                            else:
                                if nfv_type == 'virtual':
                                    if prev_dpid == s_dpid:
                                        self.controller_call_for_flowadd(cur, chain_id, s_dpid, s_serviceIP, None, s_s_inport, s_s_outport, s_wildcards, 1, allocIP_src, src_nfv_vlan, dst_nfv_vlan, True)
                                        self.controller_call_for_flowadd(cur, chain_id, s_dpid, None, d_serviceIP, s_s_outport, s_s_inport, d_wildcards, 1, allocIP_dst, dst_nfv_vlan, src_nfv_vlan, True)
                                    else:
                                        self.controller_call_for_flowadd(cur, chain_id, s_dpid, s_serviceIP, None, s_s_inport, s_s_outport, s_wildcards, 1, allocIP_src, src_nfv_vlan, dst_nfv_vlan)
                                        self.controller_call_for_flowadd(cur, chain_id, s_dpid, None, d_serviceIP, s_s_outport, s_d_outport, d_wildcards, 1, allocIP_dst, dst_nfv_vlan, src_nfv_vlan, True)
                                    #self.controller_call_for_flowadd(cur, chain_id, s_dpid, s_serviceIP, None, s_s_inport, s_s_outport, s_wildcards, 1, allocIP_src, src_nfv_vlan, dst_nfv_vlan)
                                    #self.controller_call_for_flowadd(cur, chain_id, s_dpid, None, d_serviceIP, s_s_outport, s_d_outport, d_wildcards, 1, allocIP_dst, dst_nfv_vlan, src_nfv_vlan, True)
                                elif nfv_type == 'dphysical':
                                    if prev_dpid_type == 'virtual':
                                        self.controller_call_for_flowadd(cur, chain_id, s_dpid, s_serviceIP, None, s_s_inport, s_s_outport, s_wildcards, 1, allocIP_src, src_nfv_vlan, dst_nfv_vlan)
                                        self.controller_call_for_flowadd(cur, chain_id, s_dpid, None, d_serviceIP, s_s_outport, s_d_outport, d_wildcards, 1, allocIP_dst, dst_nfv_vlan, src_nfv_vlan, True)
                                        pass
                                    else:
                                        self.controller_call_for_flowadd(cur, chain_id, s_dpid, s_serviceIP, None, s_s_inport, s_s_outport, s_wildcards, 1, allocIP_src, src_nfv_vlan, dst_nfv_vlan)
                                        self.controller_call_for_flowadd(cur, chain_id, s_dpid, None, d_serviceIP, s_s_outport, s_s_inport, d_wildcards, 1, allocIP_dst, dst_nfv_vlan, src_nfv_vlan, True)
                                        #self.controller_call_for_flowadd(cur, chain_id, s_dpid, None, d_serviceIP, s_s_outport, s_d_outport, d_wildcards, 1, allocIP_dst, dst_nfv_vlan, src_nfv_vlan, True)
                                    
                                else :
                                    self.controller_call_for_flowadd(cur, chain_id, s_dpid, s_serviceIP, None, s_s_inport, s_s_outport, s_wildcards, 1, allocIP_src, src_nfv_vlan, dst_nfv_vlan)
                                    self.controller_call_for_flowadd(cur, chain_id, s_dpid, None, d_serviceIP, s_d_inport, s_d_outport, d_wildcards, 1, allocIP_dst, dst_nfv_vlan, src_nfv_vlan, True)
                            #rule DB Add
                            #cur.execute("INSERT INTO servicechainrule (chain_id, sip, dip, inport, outport, dpid, vlan, wildcard, prior) VALUES (%s, %s, NULL, %s, %s, %s, %s, %s, 1), (%s, NULL, %s, %s, %s, %s, %s, %s, 1)", (chain_id, s_serviceIP, s_s_inport, s_s_outport, s_dpid, src_nfv_vlan, s_wildcards, chain_id, d_serviceIP, s_d_inport ,s_d_outport, s_dpid, dst_nfv_vlan, d_wildcards))
                        else:
                            #print "sip:%s, dip:%s, dpid:%s, vlan:0, in_port:%s, out_port:%s" % (s_serviceIP, 0, s_dpid, s_s_inport, s_s_outport)
                            #print "sip:%s, dip:%s, dpid:%s, vlan:0, in_port:%s, out_port:%s, is_strip:%s" % (0, d_serviceIP, s_dpid, s_d_inport, s_d_outport, is_strip_f)
                            #self.controller_call_for_flowadd(s_dpid, s_serviceIP, None, s_s_inport, s_s_outport, s_wildcards, 1, allocIP_src, 0)
                            #self.controller_call_for_flowadd(s_dpid, None, d_serviceIP, s_d_inport, s_d_outport, d_wildcards, 1, allocIP_dst, 0, False, is_strip_f)
                            self.controller_call_for_flowadd(cur, chain_id, s_dpid, s_serviceIP, None, s_s_inport, s_s_outport, s_wildcards, 1, allocIP_src)
                            self.controller_call_for_flowadd(cur, chain_id, s_dpid, None, d_serviceIP, s_d_inport, s_d_outport, d_wildcards, 1, allocIP_dst, 0, 0, False, is_strip_f)
                            #rule DB Add
                            #cur.execute("INSERT INTO servicechainrule (chain_id, sip, dip, inport, outport, dpid, vlan, wildcard, prior) VALUES (%s, %s, NULL, %s, %s, %s, 0, %s, 1), (%s, NULL, %s, %s, %s, %s, 0, %s, 1)", (chain_id, s_serviceIP, s_s_inport, s_s_outport, s_dpid, s_wildcards, chain_id, d_serviceIP, s_d_inport ,s_d_outport, s_dpid, d_wildcards))
                        #con.commit()
                        break

                    elif stopper > MAXIMUM_HOP:
                        break

                    cur.execute("SELECT * FROM topo WHERE dpid = '%s' AND dst_dpid = '%s'" % (s_dpid, endnfv_dpid))
                    row = cur.fetchone()
                    if not row:
                        print "[ERROR] finding topology"
                        exit()
                    dpid_type = row["type"]
                    if (s_dpid == start_dpid) and (stopper < 1):
                        s_s_inport = start_outport
                        s_s_outport = row["in_port"]
                        s_d_inport = row["out_port"]
                        s_d_outport = start_inport
                        allocIP_src = service_ip
                        allocIP_dst = user_ip
                        s_serviceIP = user_ip
                        s_wildcards = mul_nbapi.OFPFW_ALL & ~(mul_nbapi.OFPFW_NW_SRC_MASK) & ~(mul_nbapi.OFPFW_DL_TYPE) & ~(mul_nbapi.OFPFW_IN_PORT)
                        is_set = True
                    elif firstloopOfnfv:
                        s_s_inport = s_d_inport
                        s_d_outport = s_s_outport
                        s_s_outport = row["in_port"]
                        s_d_inport = row["out_port"]
                        s_wildcards = mul_nbapi.OFPFW_ALL & ~(mul_nbapi.OFPFW_NW_SRC_MASK) & ~(mul_nbapi.OFPFW_DL_TYPE) & ~(mul_nbapi.OFPFW_IN_PORT) & ~(mul_nbapi.OFPFW_DL_VLAN)
                        is_set = True
                        firstloopOfnfv = False
                    else:
                        s_s_inport = s_s_outport
                        s_s_outport = row["in_port"]
                        s_d_outport = s_d_inport
                        s_d_inport = row["out_port"]
                        s_wildcards = mul_nbapi.OFPFW_ALL & ~(mul_nbapi.OFPFW_NW_SRC_MASK) & ~(mul_nbapi.OFPFW_DL_TYPE) & ~(mul_nbapi.OFPFW_IN_PORT) & ~(mul_nbapi.OFPFW_DL_VLAN)
                        is_set = False

                    if is_vlan_tagging:
                        #print "sip:%s, dip:%s, dpid:%s, vlan:%s, in_port:%s, out_port:%s, is_set:%s, nfv_name:%s " % (s_serviceIP, 0, s_dpid, src_nfv_vlan, s_s_inport, s_s_outport, is_set, nfv_name)
                        #print "sip:%s, dip:%s, dpid:%s, vlan:%s, in_port:%s, out_port:%s" % (0, d_serviceIP, s_dpid, dst_nfv_vlan, s_d_inport, s_d_outport)
                        if ((s_dpid == start_dpid) and (i==0)) :
                            s_wildcards = mul_nbapi.OFPFW_ALL & ~(mul_nbapi.OFPFW_NW_SRC_MASK) & ~(mul_nbapi.OFPFW_DL_TYPE) & ~(mul_nbapi.OFPFW_IN_PORT) & ~(mul_nbapi.OFPFW_DL_DST)
                            self.controller_call_for_flowadd(cur, chain_id, s_dpid, s_serviceIP, None, s_s_inport, s_s_outport, s_wildcards, 1, allocIP_src, src_nfv_vlan, dst_nfv_vlan, is_set, False, False, False, False, start_mac)
                            self.controller_call_for_flowadd(cur, chain_id, s_dpid, None, d_serviceIP, s_d_inport, s_d_outport, d_wildcards, 1, allocIP_dst, src_nfv_vlan, dst_nfv_vlan, False, False, False, False, True, start_mac)
                        else :
                            pdpi_vlan = 19
                            self.controller_call_for_flowadd(cur, chain_id, s_dpid, s_serviceIP, None, s_s_inport, s_s_outport, s_wildcards, 1,allocIP_src, src_nfv_vlan, dst_nfv_vlan, is_set)
                            if dpid_type == 'virtual' or src_nfv_vlan == pdpi_vlan:
                                self.controller_call_for_flowadd(cur, chain_id, s_dpid, None, d_serviceIP, s_d_inport, s_s_inport, d_wildcards, 1, allocIP_dst, dst_nfv_vlan, src_nfv_vlan)
                            else:
                                self.controller_call_for_flowadd(cur, chain_id, s_dpid, None, d_serviceIP, s_d_inport, s_d_outport, d_wildcards, 1, allocIP_dst, dst_nfv_vlan, src_nfv_vlan)

                        #rule DB Add, KONG Debug : 2013-09-10
                        #cur.execute("INSERT INTO servicechainrule (chain_id, sip, dip, inport, outport, dpid, vlan, wildcard, prior) VALUES (%s, %s, NULL, %s, %s, %s, %s, %s, 1), (%s, NULL, %s, %s, %s, %s, %s, %s, 1)", (chain_id, s_serviceIP, s_s_inport, s_s_outport, s_dpid, src_nfv_vlan, s_wildcards, chain_id, d_serviceIP, s_d_inport ,s_d_outport, s_dpid, dst_nfv_vlan, d_wildcards))
                        if is_set:
                            is_set = False
                    else:
                        #print "sip:%s, dip:%s, dpid:%s, vlan:0, in_port:%s, out_port:%s, is_strip:%s" % (s_serviceIP, 0, s_dpid, s_s_inport, s_s_outport, is_strip_l)
                        #print "sip:%s, dip:%s, dpid:%s, vlan:0, in_port:%s, out_port:%s" % (0, d_serviceIP, s_dpid, s_d_inport, s_d_outport)
                        #self.controller_call_for_flowadd(s_dpid, s_serviceIP, None, s_s_inport, s_s_outport, s_wildcards, 1, allocIP_src, 0, False, is_strip_l)
                        self.controller_call_for_flowadd(cur, chain_id, s_dpid, s_serviceIP, None, s_s_inport, s_s_outport, s_wildcards, 1, allocIP_src, 0)
                        self.controller_call_for_flowadd(cur, chain_id, s_dpid, None, d_serviceIP, s_d_inport, s_d_outport, d_wildcards, 1, allocIP_dst, 0)
                        #rule DB Add
                        #cur.execute("INSERT INTO servicechainrule (chain_id, sip, dip, inport, outport, dpid, vlan, wildcard, prior) VALUES (%s, %s, NULL, %s, %s, %s, 0, %s, 1), (%s, NULL, %s, %s, %s, %s, 0, %s, 1)", (chain_id, s_serviceIP, s_s_inport, s_s_outport, s_dpid, s_wildcards, chain_id, d_serviceIP, s_d_inport ,s_d_outport, s_dpid, d_wildcards))
                        if is_strip_l:
                            is_strip_l = False

                    #con.commit()

                    s_dpid = row["nexthop_dpid"]
                    prev_dpid_type = row["type"]
                    stopper += 1
                    firstloopOfnfv = False

        con.commit()
        result["message"] = "SUCCESS"
        return result

    def controller_call_for_flowdel(self, cur, dpid, sip, dip, in_port, out_port, prior, vlan, wildcard, smac=None):
        """ Work from Chan"""
        """ This Code is modified by Backguyn : 20130928 """
        cur.execute("SELECT dpid FROM logicswitch WHERE logical_dpid = %s", dpid)
        real_dpid = cur.fetchone()
        """ modified end """
        # KONG Debug : 2013-09-10
        #print "sip:%s, dip:%s, dpid:%s, vlan:0, in_port:%s, out_port:%s" % (sip, dip, real_dpid['dpid'], in_port, out_port)
        #if not sip:
        #    wildcards = mul_nbapi.OFPFW_ALL & ~(mul_nbapi.OFPFW_NW_DST_MASK) & ~(mul_nbapi.OFPFW_DL_TYPE) & ~(mul_nbapi.OFPFW_IN_PORT)
        #else :
        #    wildcards = mul_nbapi.OFPFW_ALL & ~(mul_nbapi.OFPFW_NW_SRC_MASK) & ~(mul_nbapi.OFPFW_DL_TYPE) & ~(mul_nbapi.OFPFW_IN_PORT)
        #vlan need
        #flow = mul_nbapi.nbapi_flow_make_flow(str(sip), str(dip), int(in_port), int(vlan), 0x0800, int(0), int(0), None, None, int(0), int(0), int(0))
        if smac is not None:
            flow = mul_nbapi.nbapi_flow_make_flow(sip, dip, int(in_port), int(vlan), 0x0800, 0, 0, None, str(smac), 0, 0, 0)
        else :
            flow = mul_nbapi.nbapi_flow_make_flow(sip, dip, int(in_port), int(vlan), 0x0800, 0, 0, None, None, 0, 0, 0)

        #action_list = []
        #if allocIP:
        #    if not sip:
        #        action_list.append(mul_nbapi.nbapi_make_action_set_nw_daddr(str(allocIP)))
        #    else :
        #        action_list.append(mul_nbapi.nbapi_make_action_set_nw_saddr(str(allocIP)))
        #action_list.append(mul_nbapi.nbapi_make_action_output(int(out_port)))       
        resp = mul_nbapi.delete_static_flow(int(real_dpid['dpid'], 0), flow, wildcard, int(out_port), int(prior))
               
        if resp == 0:
            return
        else:
            print "[ERROR] during Flow del"
            return

    def delete_service(self, conf, chain_id, updatelog=False):
        """ Work from Chan"""
        try:
            con = mdb.connect('localhost', 'root', 'of#123', 'skdemo2')
            cur = con.cursor(mdb.cursors.DictCursor)
        except:
            print "[ERROR] DB Connection Fail"
            pass

        #parsing body
        i_chain_id = chain_id
        result = dict()
        
        try:
            #False : User, True : Controller
            if updatelog is False:
                self.checkAndDeleteServiceChainLog(chain_id)

            #controller call for delete
            cur.execute("SELECT * FROM servicechainrule WHERE chain_id = %s", chain_id)
            rows = cur.fetchall()
                
            if not rows:
                print "[ERROR] servicechainrule have no this rule"
                return {"message" : "FAIL"}

                
            cur.execute("DELETE FROM servicechainrule WHERE chain_id = %s", chain_id)
            con.commit()

            for row in rows:
                # KONG Debug : 2013-09-10
                #self.controller_call_for_flowdel(cur, row["dpid"], row["sip"], row["dip"], row["inport"], row["outport"], 1, row["vlan"])
                #cur.execute("SELECT dpid FROM logicswitch WHERE logical_dpid = %s", row["dpid"])
                #real_dpid = cur.fetchone()
                #dpid = real_dpid['dpid']
                self.controller_call_for_flowdel(cur, row["dpid"],row["sip"], row["dip"], row["inport"], row["outport"], row["prior"], row["vlan"], row["wildcard"],row["smac"])
        
            result["message"] = "SUCCESS"

        except Exception as err:
            con.rollback()
            result["message"] = "FAil"
            print ""
            print err
            print ""   
       
        con.close() 
        return result         
    
    def old_delete_service(self, conf, phone_num, service_type):
        """ NOT USE DEF"""
        """ Work from Chan"""
        try:
            con = mdb.connect('localhost', 'root', 'of#123', 'skdemo2')
            cur = con.cursor(mdb.cursors.DictCursor)
        except:
            print "[ERROR] DB Connection Fail"
            pass

        #parsing body
        i_service_type = service_type
        i_mdn = phone_num
        result = dict()
        
        #check sainfo
        cur.execute("SELECT * FROM sa WHERE service_type = %s", i_service_type)
        row = cur.fetchone()
        if not row:
            result["message"] = "FAIL"
            return result
        service_id = row["service_id"]

        #check userinfo
        cur.execute("SELECT * FROM user WHERE phone_num = %s", i_mdn)
        row = cur.fetchone()
        if not row:
            result["message"] = "FAIL"
            return result
        user_id = row["userid"]
                
        #check ippool
        cur.execute("SELECT * FROM ippool WHERE service_id = %s AND user_id = %s", (service_id, user_id))
        row = cur.fetchone()
        if not row:
            result["message"] = "FAIL"
            return result
        chain_id = row["chain_id"]

        try:
            #update ippool
            cur.execute("UPDATE ippool SET user_id = 0 WHERE chain_id = %s", chain_id)
        
            #delete info
            cur.execute("DELETE FROM servicechainlog WHERE chain_id = %s", chain_id)
            con.commit()
            result["message"] = "SUCCESS"

        except:
            con.rollback()
            result["message"] = "FAIL"   
        
        return result         


    def show_switch_list(self, conf):
        """ Work from Chan"""
        try:
            con = mdb.connect('localhost', 'root', 'of#123', 'skdemo2')
            cur = con.cursor(mdb.cursors.DictCursor)
        except:
            print "[ERROR] DB Connection Fail"
            pass

        cur.execute("SELECT * FROM switch")
        rows = cur.fetchall()
        result = dict()
        result["switch_list"] = []

        for row in rows:
            result["switch_list"].append({"dpid":row["dpid"], "ip":row["ip"]})

        return result

    def show_switch_statistic(self, conf, dpid):
        """ Work from Chan"""
        try:
            con = mdb.connect('localhost', 'root', 'of#123', 'skdemo2')
            cur = con.cursor(mdb.cursors.DictCursor)
        except:
            print "[ERROR] DB Connection Fail"
            pass

        cur.execute("SELECT * FROM switch WHERE dpid = %s", dpid)
        row = cur.fetchone()
        
        if not row:
            print "[ERROR] cannot find Switch dpid"
            return {"message":"FAIL"}

        flow_list = mul_nbapi.get_switch_statistics_all(int(dpid, 0))
        
        result = dict() 
        stats = self.stat_all_port_parse(flow_list)
        
        result["message"] = "SUCCESS"
        result["flows"] = stats

        return result
        

    def get_service(self, conf, phone_num, service_type):
        pass
    
    def update_service(self, conf, phone_num, service_type, body):
        pass  
    
    """ SADB API """
    def get_all_sadb(self, conf):
        """ Work from Chan"""
        """ 2013-09-12 modify by Backguyn """
        DEFAULT_SA_DPID = '0x03'
        try:
            con = mdb.connect('localhost', 'root', 'of#123', 'skdemo2')
            cur = con.cursor(mdb.cursors.DictCursor)
        except:
            print "[ERROR] DB Connection Fail"
            pass

        cur.execute("SELECT * FROM sa WHERE active = 1")
        rows = cur.fetchall()
        
        result = dict()
        result["services"] = []

        for row in rows:
            #result["services"].append({"service_type":row["service_type"],"DPID":row["dpid"],"IP":row["ip"],"IN_PORT":row["in_port"],"OUT_PORT":row["out_port"]})
            result["services"].append({"service_type":row["service_type"],"DPID":DEFAULT_SA_DPID,"IP":row["ip"],"PORT":row["ssg_port"]})
            
        return result   

    def create_SADB(self, conf, params):
        """ Work from Chan"""
        """ 2013-09-12 modify by Backguyn """
        try:
            con = mdb.connect('localhost', 'root', 'of#123', 'skdemo2')
            cur = con.cursor(mdb.cursors.DictCursor)
        except:
            print "[ERROR] DB Connection Fail"
            pass

        #cur.execute("SELECT * FROM sa WHERE service_type = %s", params['service_type'])
        cur.execute("SELECT * FROM sa WHERE ip = %s", params["ip"])
        service = cur.fetchone()

        if not service:
            print "[ERROR] this service is not"
            con.close()
            return {"message" : "FAIL"}

        """ check the equal dpid and equal port """
        cur.execute("SELECT * FROM sa WHERE ip != %s AND ((dpid = %s AND in_port = %s))", (params["ip"], params["dpid"], params["port"]))
        row = cur.fetchone()
        if not row:
            #cur.execute("UPDATE sa SET dpid = %s, in_port = %s, out_port = %s WHERE ip = %s", (params["dpid"], params["port"], params["port"], params["ip"]))
            #con.commit()
            pass
        else:
            err_msg =  "[ERROR] This dpid and port is already used"
            print err_msg
            con.close()
            #return {"message" : "FAIL"}
            return {"message" : err_msg }

        cur.execute("SELECT * FROM sa WHERE ip != %s AND service_type = %s", (params["ip"], params["service_type"]))
        row = cur.fetchone()
        if not row:
            cur.execute("UPDATE sa SET service_type = %s WHERE ip = %s", (params["service_type"], params["ip"]))
            con.commit()
        else:
            err_msg =  "[ERROR] This service name is already used"
            print err_msg
            con.close()
            return {"message" : err_msg}
        
        """
        cur.execute("SELECT * FROM sa WHERE dpid = %s AND in_port = %s AND service_type != %s", (params['dpid'], params['port'], params['service_type']))
        row = cur.fetchone()

        if row:
            cur.execute("UPDATE sa SET service_type = %s WHERE ip = %s", (params["service_type"], params["ip"]))
            con.commit()
            #print "[ERROR] The service using this dpid and port already exist"
            #con.close()
            #return {"message" : "E_MSG0"}
        
        cur.execute("SELECT ip FROM sa WHERE ip = %s AND service_type != %s", (params['ip'], params['service_type']))
        row = cur.fetchone()

        if row:
            print "[ERROR] The service using this ip already exist"
            con.close()
            return {"message" : "FAIL"}
        """
        
        if service['active'] == 0:
            cur.execute("UPDATE sa SET active = 1 WHERE service_type = %s", params['service_type'])
            con.commit()

        #cur.execute("UPDATE sa SET dpid = %s, in_port = %s, out_port = %s, ip = %s WHERE service_type = %s", (params["dpid"], params["port"], params["port"], params["ip"], params["service_type"]) )

        con.close()
        
        return {"message" : "SUCCESS"}


    def delete_SADB(self, conf, service_type):
        """ Work from Chan"""
        """ 2013-09-12 modify by Backguyn """
        try:
            con = mdb.connect('localhost', 'root', 'of#123', 'skdemo2')
            cur = con.cursor(mdb.cursors.DictCursor)
        except:
            print "[ERROR] DB Connection Fail"
            pass

        cur.execute("SELECT * FROM sa WHERE service_type = %s", service_type)
        row = cur.fetchone()
        
        cur.execute("SELECT * FROM ippool WHERE service_id = %s AND user_id != 0 LIMIT 1", row['service_id'])
        user = cur.fetchone()
        if user:
            print "[ERROR] this service is used to user"
            return {"message" : "E_MSG1"}
        
        if row['active'] != 0:
            try:
                cur.execute("UPDATE sa SET active = 0 WHERE service_type = %s", service_type)
                con.commit()
            except:
                con.rollback()
                print "[ERROR] Fail to update DB"
                return {"message" : "FAIL"}

        return {"message" : "SUCCESS"}

    
    """ NFVDB API """
    def get_all_nfvdb(self,conf):
        """ Work from Chan"""
        """ 2013-09-12 modify from backguyn """
        try:
            con = mdb.connect('localhost', 'root', 'of#123', 'skdemo2')
            cur = con.cursor(mdb.cursors.DictCursor)
        except:
            print "[ERROR] DB Connection Fail"
            pass

        #cur.execute("SELECT * FROM nfv as a, nfvvm as b, (SELECT * FROM (SELECT * FROM nfvvmStatus ORDER BY time DESC) as aa GROUP BY nfv_vm_id) as c WHERE a.nfv_id = b.nfv_id AND b.nfv_vm_id = c.nfv_vm_id")
        cur.execute("SELECT nfv, type, service_level, nfv_name, dpid, in_port, out_port, b.nfv_id FROM nfv as a, nfvvm as b WHERE a.nfv_id = b.nfv_id AND b.active = 1 ORDER BY a.nfv_id ASC, b.nfv_vm_id ASC")
        rows = cur.fetchall()
        if not rows:
            return {"message" : "FAIL"}

        result = dict()
        result["nfv_list"] = []

        for row in rows:
            #result["nfv_list"].append({"type":row["type"],"name":row["nfv_name"],"DPID":row["dpid"],"IN_PORT":row["in_port"],"IN_PORT_PPS":row["in_port_pps"],"OUT_PORT":row["out_port"],"OUT_PORT_PPS":row["out_port_pps"],"CPU_USAGE":row["cpu_usage"]})
            #result["nfv_list"].append({"type":row["type"],"name":row["nfv_name"],"DPID":row["dpid"],"IN_PORT":row["in_port"],"OUT_PORT":row["out_port"]})
            result["nfv_list"].append({"name":row["nfv"],"type":row["type"], "service_level":row["service_level"],"nfv_name":row["nfv_name"],"DPID":row["dpid"],"IN_PORT":row["in_port"],"OUT_PORT":row["out_port"], "index":row['nfv_id']})

        con.close()
        return result   

    def get_nfvdb_bymdn(self, conf, mdn):
        """ Work from Chan"""
        try:
            con = mdb.connect('localhost', 'root', 'of#123', 'skdemo2')
            cur = con.cursor(mdb.cursors.DictCursor)
        except:
            print "[ERROR] DB Connection Fail"
            pass
        
        cur.execute("SELECT service_level FROM user WHERE phone_num = %s", mdn)
        row = cur.fetchone()
        if not row:
            return {"message" : "E_MSG5"}

        service_level = row["service_level"]

        cur.execute("SELECT * FROM nfv as a, nfvvm as b WHERE a.nfv_id = b.nfv_id AND b.active = 1 AND a.service_level <= %s ORDER BY b.nfv_id ASC, b.nfv_vm_id ASC", service_level)
        rows = cur.fetchall()
        if not rows:
            return {"message" : "FAIL"}
        
        result = dict()
        result["nfv_list"] = []

        for row in rows:
            result["nfv_list"].append({"name":row["nfv"],"type":row["type"], "service_level":row["service_level"],"nfv_name":row["nfv_name"],"DPID":row["dpid"],"IN_PORT":row["in_port"],"OUT_PORT":row["out_port"],"index":row["nfv_id"]})
            
        return result   
    

    def get_nfvdb_vm(self, conf):
        """ 2013-09-13 Work from Backguyn """
        try:
            con = mdb.connect("localhost", "root", "of#123", "skdemo2")
            cur = con.cursor(mdb.cursors.DictCursor)
        except:
            print "[ERROR] DB Connection Fail"
            pass

        cur.execute("SELECT nfv_id FROM nfv")
        id_list = cur.fetchall()

        result = dict()
        result['nfv_list'] = list()

        for nfv_id in id_list:
        
            cur.execute("SELECT * FROM nfv, nfvvm WHERE nfv.nfv_id = nfvvm.nfv_id AND nfv.nfv_id = %s AND nfvvm.active = 1 ORDER BY nfvvm.nfv_id ASC, nfvvm.nfv_vm_id ASC", nfv_id['nfv_id'])
            rows = cur.fetchall()
            if not rows:
                return {"message" : "FAIL"}

            for row in rows:
                temp = dict()
                temp['name'] = row['nfv']
                temp['nfv_name'] = row['nfv_name']

                result['nfv_list'].append(temp)

        return result


    def create_nfvdb(self, conf, params):
        """ Work from Chan"""
        """ 2013-09-12 modify by Backguyn """
        try:
            con = mdb.connect('localhost', 'root', 'of#123', 'skdemo2')
            cur = con.cursor(mdb.cursors.DictCursor)
        except:
            print "[ERROR] DB Connection Fail"
            pass

        #parse argv
        nfv_name = params["name"]
        nfv_vm_name = params["nfv_name"]
        nfv_type = params["type"]
        nfv_dpid = params["dpid"]
        nfv_inport = params["in_port"]
        nfv_outport = params["out_port"]
        nfv_index = params["index"]

        if nfv_index < 0 and nfv_index > 10:
            print "[ERROR] Index is out of range"
            return {"message" : "FAIL"}

        cur.execute("SELECT * FROM nfv WHERE nfv = %s", nfv_name)
        nfv = cur.fetchone()

        cur.execute("SELECT * FROM nfv WHERE nfv_id = %s", nfv_index)
        row = cur.fetchone()
        
        if nfv:
            """ This nfv name is already in the DB """
            if row:
                if nfv['nfv'] != row['nfv']: #other nfv is already
                    print "[ERROR] This index_num is already"
                    return {"message" : "FAIL"}
        else:
            """ This nfv name is not DB """
            if row:
                print "[ERROR] This index_num is already"
                return {"message" : "FAIL"}
            try:
                cur.execute("INSERT INTO nfv (nfv_id, nfv, type, service_level) VALUES (%s, %s, %s, 0)", (nfv_index, nfv_name, nfv_type))
                con.commit()
            except:
                con.rollback()
                print "[ERROR] Fail DB Update"
                return {"message" : "FAIL"}
        
        cur.execute("SELECT * FROM nfvvm WHERE dpid = %s AND nfv_name != %s AND (in_port = %s OR out_port = %s)", (nfv_dpid, nfv_vm_name, nfv_inport, nfv_inport))
        row = cur.fetchone()
        if row:
            print "[ERROR] This port num conflicts with the another port"
            return {"message" : "E_MSG2"}

        cur.execute("SELECT * FROM nfvvm WHERE dpid = %s AND nfv_name != %s AND (in_port = %s OR out_port = %s)", (nfv_dpid, nfv_vm_name, nfv_outport, nfv_outport))
        row = cur.fetchone()
        if row:
            print "[ERROR] This port num conflicts with the another port"
            return {"message" : "E_MSG3"}

        
        """ Check that nfvvm Database have nfv_vm_name """
        cur.execute("SELECT * FROM nfvvm WHERE nfv_name = %s", nfv_vm_name)
        nfv_vm = cur.fetchone()

        if nfv_vm:
            """ If nfv_vm_name is already, this action is modification """
            try:
                cur.execute("UPDATE nfvvm SET dpid = %s, in_port = %s, out_port = %s, active = 1 WHERE nfv_name = %s", (nfv_dpid, nfv_inport, nfv_outport, nfv_vm_name))
                cur.execute("UPDATE nfv SET nfv_id = %s WHERE nfv = %s", (nfv_index, nfv_name))
                cur.execute("UPDATE nfvvm SET nfv_id = %s WHERE nfv_id = %s", (nfv_index, nfv_vm['nfv_id']))
                con.commit()
            except:
                print "[ERROR] Fail to update DB"
                return {"message" : "FAIL"}
            
        else:
            """ If nfv_vm_name is not on the DB, this action is failed """
            print "[ERROR] This nfv_vm can not be found"
            return {"message" : "FAIL"} 

        return {"message" : "SUCCESS"}
            

    def delete_nfvdb(self, conf, name):
        """ Work from Chan"""
        """ 2013-09-12 modify by Backguyn """
        try:
            con = mdb.connect('localhost', 'root', 'of#123', 'skdemo2')
            cur = con.cursor(mdb.cursors.DictCursor)
        except:
            print "[ERROR] DB Connection Fail"
            pass       
        
        #parsing argv
        nfv_name = name

        #check coordination
        cur.execute("SELECT * FROM nfvvm WHERE nfv_name = %s", nfv_name)
        row = cur.fetchone()

        if not row:
            print "[ERROR] can not find NFV name"
            return {"message": "FAIL"}

        nfv_vm_id = row["nfv_vm_id"]
        nfv_id = row["nfv_id"]
        
        cur.execute("SELECT * FROM servicechainlog WHERE nfv_name = %s LIMIT 1", nfv_name)
        row = cur.fetchone()

        if not row:
            #ongoing delete
            try:
                #cur.execute("DELETE FROM nfvvmStatus WHERE nfv_vm_id = %s", nfv_vm_id)
                """ modify 2013-09-12"""
                cur.execute("UPDATE nfvvm SET active = 0 WHERE nfv_vm_id = %s", nfv_vm_id)
                con.commit()
            except:
                con.rollback()
                return {"message":"FAIL"}
        
            return {"message" : "SUCCESS"}

        else:
            print "[ERROR] someone occupied this NFV"
            return {"message": "E_MSG4"}
    
    def update_nfvdb(self, conf, name, body):
        """ TODO: Update NFV Node from the DB """
        pass  

    def create_nfvvmdb(self, conf, params):
        """ NOT USED FUNC."""
        """ Work from Chan"""
        try:
            con = mdb.connect('localhost', 'root', 'of#123', 'skdemo2')
            cur = con.cursor(mdb.cursors.DictCursor)
        except:
            print "[ERROR] DB Connection Fail"
            pass

        cur.execute("SELECT nfv_id FROM nfv WHERE nfv = %s LIMIT 1", params['name'])
        row = cur.fetchone()

        if not row:
            print "[ERROR] N/A nfv name"
            return {"result": "FAIL"}
        else:
            nfv_id = row["nfv_id"]
            nfv_name = params["nfv_name"]
            nfv_dpid = params["dpid"]
            nfv_inport = params["in_port"]
            nfv_outport = params["out_port"]

            cur.execute("SELECT nfv_name FROM nfvvm WHERE nfv_name = %s LIMIT 1", nfv_name)
            row = cur.fetchone()
            
            if not row:
                #go on
                cur.execute("SELECT nfv_vm_id FROM nfvvm ORDER BY nfv_vm_id DESC LIMIT 1")
                row = cur.fetchone()
                nfv_vmid = row["nfv_vm_id"] + 1

                try:
                    cur.execute("INSERT INTO nfvvm VALUES (%s, %s, %s, %s, %s, %s)",(nfv_id, nfv_vmid, nfv_name, nfv_dpid, nfv_inport, nfv_outport))
                    con.commit()
                    cur.execute("INSERT INTO nfvvmStatus (nfv_vm_id, in_port_pps, out_port_pps, cpu_usage) VALUES (%s, 0, 0, 0)", nfv_vmid)
                    con.commit()
                    return {"result": "SUCCESS"}
                except:
                    con.rollback()
                    return {"result": "FAIL"}
            else:
                #modify
                print "[ERROR] duplicated nfv_vm name"
                return {"result": "FAIL"}



    def get_vm_statistic(self, conf, nfv_name):
        """Work from Chan"""
        try:
            con = mdb.connect('localhost', 'root', 'of#123', 'skdemo2')
            cur = con.cursor(mdb.cursors.DictCursor)
        except:
            print "[ERROR] failed connecting to DB at nfv_vm_Threshold"
            pass
       
        if nfv_name == "ALL":
            cur.execute("SELECT b.nfv_name, b.nfv_id, a.nfv_vm_id, a.in_port_pps, a.out_port_pps, a.cpu_usage FROM nfvvmStatus as a, nfvvm as b WHERE a.nfv_vm_id = b.nfv_vm_id AND b.active = 1 ORDER BY b.nfv_id, b.nfv_vm_id")
            rows = cur.fetchall()

            if not rows:
                return {"message" : "FAIL", "flow" : []}

            result = dict()
            result["message"] = "SUCCESS"
            result["flow"] = list()
            for row in rows:
                threshold = self.get_nfv_vm_threshold(conf, row["nfv_id"])
                
                temp = dict()
                temp["nfv_name"] = row["nfv_name"]
                temp["index"] = row["nfv_id"]
                temp["nfv_vm_id"] = row["nfv_vm_id"]
                temp["inport_pps"] = row["in_port_pps"] + row["out_port_pps"]
                cpu_usage = row["cpu_usage"]
                if temp["inport_pps"] > 0 and cpu_usage == 0:
                    cpu_usage = 1
                temp["cpu_usage"] = cpu_usage
                temp["cpu_usage_threshold"] = threshold["cpu_usage_threshold"]
                temp["cpu_duration"] = threshold["cpu_usage_duration"]
                temp["inport_pps_threshold"] = threshold["inport_pps_threshold"]
                temp["inport_pps_duration"] = threshold["inport_pps_duration"]
                result["flow"].append(temp)
                
            con.close()
            return result
        else: 
            cur.execute("SELECT b.nfv_name, b.nfv_id, a.nfv_vm_id, a.in_port_pps, a.out_port_pps, a.cpu_usage FROM nfvvmStatus as a, nfvvm as b WHERE a.nfv_vm_id = b.nfv_vm_id AND b.nfv_name = %s AND b.active = 1 ORDER BY a.time DESC LIMIT 1", nfv_name)
            row = cur.fetchone()

            if not row:
                return {"message" : "FAIL", "flow" : []}

            threshold = self.get_nfv_vm_threshold(conf, row["nfv_id"])
            #print "id : ", row["nfv_vm_id"], "pps : ", row["out_port_pps"]
            con.close()
            pps = row["in_port_pps"] + row["out_port_pps"]
            cpu_usage = row["cpu_usage"]
            if temp["inport_pps"] > 0 and cpu_usage == 0:
                cpu_usage = 1
            
            return {"message" : "SUCCESS", "flow" : [{"index" : row["nfv_id"], "nfv_name": row["nfv_name"], "nfv_vm_id": row["nfv_vm_id"], "inport_pps": pps, "cpu_usage": cpu_usage, "cpu_usage_threshold": threshold["cpu_usage_threshold"], "cpu_duration": threshold["cpu_usage_duration"], "inport_pps_threshold": threshold["inport_pps_threshold"], "inport_pps_duration": threshold["inport_pps_duration"]}]}

    def get_group_statistic(self, conf, nfv_groupname):
        """Work from Chan"""
        try:
            con = mdb.connect('localhost', 'root', 'of#123', 'skdemo2')
            cur = con.cursor(mdb.cursors.DictCursor)
        except:
            print "[ERROR] failed connecting to DB at nfv_vm_Threshold"
            pass

        #cur.execute("SELECT a.nfv, b.nfv_id, AVG(c.in_port_pps) as avg_inport_pps, AVG(c.cpu_usage) as avg_cpu_usage FROM nfv as a, nfvvm as b, (SELECT * FROM (SELECT * FROM nfvvmStatus ORDER BY time DESC) as aa GROUP BY nfv_vm_id) as c WHERE a.nfv_id = b.nfv_id AND b.nfv_vm_id = c.nfv_vm_id AND a.nfv = %s GROUP BY b.nfv_id", nfv_groupname)
        cur.execute("SELECT a.nfv, b.nfv_id, SUM(c.in_port_pps) as avg_inport_pps, SUM(c.out_port_pps) as avg_outport_pps, AVG(c.cpu_usage) as avg_cpu_usage FROM nfv as a, nfvvm as b, nfvvmStatus as c WHERE a.nfv_id = b.nfv_id AND b.nfv_vm_id = c.nfv_vm_id AND a.nfv = %s AND b.active = 1", nfv_groupname )
        row = cur.fetchone()

        avg_inport_pps = float(row["avg_inport_pps"] + row["avg_outport_pps"])
        avg_cpuusage = float(row["avg_cpu_usage"])

        con.close()

        return {"message" : "SUCCESS", "flows" : [{"nfv_id": row["nfv_id"], "inport_pps": avg_inport_pps, "cpu_usage": avg_cpuusage}]}



    """nfv_vm_threshold_db"""
    def update_nfvvmThresholddb(self, conf, group_name, params):
        """Work BackGuyn"""
        try:
            con = mdb.connect('localhost', 'root', 'of#123', 'skdemo2')
            cur = con.cursor(mdb.cursors.DictCursor)
        except:
            print "[ERROR] failed connecting to DB at nfv_vm_Threshold"
            pass

        cur.execute("SELECT nfv_id FROM nfv WHERE nfv = %s", group_name)
        row = cur.fetchone()

        if not row:
            print "[ERROR] N/A nfv_name at nfv_vm_Threshold"
            return {"message":"FAIL"}
        else:
            nfv_id = row["nfv_id"]
            cpu_usage_threshold = params["cpu_threshold"]
            cpu_usage_duration = params["cpu_duration"]
            inport_pps_threshold = params["pps_threshold"]
            inport_pps_duration = params["pps_duration"]

            cur.execute("SELECT nfv_id FROM nfvvmThreshold WHERE nfv_id = %s LIMIT 1", nfv_id)
            row = cur.fetchone()

        if not row:
            """Insert"""
            try:
                cur.execute("INSERT INTO nfvvmThreshold VALUES ('%s', '%s', '%s', '%s')", (cpu_usage_threshold, cpu_duration, inport_pps_threshold, inport_pps_duration) )
                con.commit()
            except:
                con.rollback()
                return {"message":"FAIL"}
        
        else:
            """Update"""
            try:
                cur.execute("UPDATE nfvvmThreshold SET cpu_usage_threshold = %s, cpu_usage_duration = %s, inport_pps_threshold = %s, inport_pps_duration = %s WHERE nfv_id = %s", (cpu_usage_threshold, cpu_usage_duration, inport_pps_threshold, inport_pps_duration, nfv_id) )
                con.commit()
            except:
                con.rollback()
                return {"message":"FAIL"}

        return {"message":"SUCCESS"}


    def get_nfv_vm_threshold(self, conf, nfvid):
        try:
            con = mdb.connect("localhost", "root", "of#123", "skdemo2")
            cur = con.cursor(mdb.cursors.DictCursor)
        except:
            print "[ERROR] DB Connection Fail"
            pass

        cur.execute("SELECT * FROM nfvvmThreshold WHERE nfv_id = %s", nfvid)
        threshold = cur.fetchone()
        return threshold



    def create_default_rule(self, conf, service_type, body):
        result = {}

        try:
            con = mdb.connect('localhost', 'root', 'of#123', 'skdemo2')
            cur = con.cursor(mdb.cursors.DictCursor)
        except:
            print "[ERROR] DB Connection Fail"

        if service_type == "ALL": 
            cur.execute("SELECT a.service_id, b.phone_num, a.chain_id FROM ippool as a, user as b WHERE b.userip = %s AND a.user_id = b.userid", self.default_user_ip)
            chain_list = cur.fetchall()

            for chain in chain_list:
                cur.execute("SELECT * FROM sa WHERE service_id = %s", chain["service_id"])
                service = cur.fetchone()
                node = self.create_service(conf, chain["phone_num"], service["service_type"], body)
                
                if node["message"] != "SUCCESS":
                    return {"message" : "FAIL"}

        else:
            cur.execute("SELECT phone_num FROM user WHERE userip = %s", self.default_user_ip)
            user = cur.fetchone()
            result = self.create_service(conf, user["phone_num"], service_type, body)
            return result

        return {"message" : "SUCCESS"}
    


    def calculate_path_by_default_rule(self, conf):
        try:
            con = mdb.connect("localhost", "root", "of#123", "skdemo2")
            cur = con.cursor(mdb.cursors.DictCursor)
        except:
            print "[ERROR] DB Connect Fail"
            return None

        cur.execute("SELECT a.nfv_order, a.nfv, nfvvm.dpid, nfvvm.in_port, nfvvm.out_port, nfvvm.vlan FROM defaultRule as a, nfv, nfvvm WHERE a.nfv = nfv.nfv AND nfv.nfv_id = nfvvm.nfv_id ORDER BY a.nfv_order")
        defaultRule_list = cur.fetchall()

        cur.execute("SELECT * FROM sa ORDER BY service_id")
        service_list = cur.fetchall()

        all_service_path_list = dict()
        all_service_path_list['forward'] = list()
        all_service_path_list['reverse'] = list()

        for service in service_list:
            forward_path_list = list()
            reverse_path_list = list()
            start = dict()
            start['dpid'] = service['dpid']
            start['in_port'] = service['in_port']
            start['out_port'] = service['out_port']
            cur.execute("SELECT vlan FROM nfvvm WHERE dpid = %s LIMIT 1", start['dpid'])
            row = cur.fetchone()

            if not row:
                vlan_num = 0
            else:
                vlan_num = row['vlan']

            start['vlan'] = vlan_num

            prev_node = start
            curr_node = start
            dRule_iter = defaultRule_list.__iter__()
            dest_nfv = dRule_iter.next()
            curr_vlan = start['vlan']

            while True:
                forward_path = dict()
                reverse_path = dict()

                if dest_nfv['dpid'] == curr_node['dpid']:
                    #in
                    forward_path['dpid'] = dest_nfv['dpid']
                    forward_path['in_port'] = prev_node['in_port']
                    forward_path['out_port'] = dest_nfv['in_port']
                    forward_path['vlan'] = dest_nfv['vlan']

                    reverse_path['dpid'] = dest_nfv['dpid']
                    reverse_path['in_port'] = dest_nfv['out_port']
                    reverse_path['out_port'] = prev_node['out_port']
                    reverse_path['vlan'] = curr_vlan

                    forward_path_list.append(forward_path)
                    reverse_path_list.append(reverse_path)

                    #out
                    try:
                        forward_path = dict()
                        reverse_path = dict()
            
                        forward_path['dpid'] = dest_nfv['dpid']
                        forward_path['in_port'] = dest_nfv['in_port']
                        forward_path['out_port'] = dest_nfv['out_port']
        
                        reverse_path = forward_path

                        #Change DEST_NFV
                        curr_vlan = dest_nfv['vlan']
                        dest_nfv = dRule_iter.next()

                        forward_path['vlan'] = dest_nfv['vlan']
                        reverse_path['vlan'] = curr_vlan

                        forward_path_list.append(forward_path)
                        reverse_path_list.append(reverse_path)

                        prev_node = curr_node
                        prev_node['in_port'] = forward_path['out_port']
                        prev_node['out_port'] = forward_path['in_port']
                        curr_node['dpid'] = forward_path['dpid']
                        continue
                    except StopIteration:
                        break

                cur.execute("SELECT * FROM topo WHERE dpid = %s AND dst_dpid = %s", (curr_node['dpid'], dest_nfv['dpid']))
                next_node = cur.fetchone()
                cur.execute("SELECT * FROM topo WHERE dpid = %s AND dst_dpid = %s", (next_node['nexthop_dpid'], curr_node['dpid']))
                reverse_node = cur.fetchone()
                try:
                    #the in & out port of next_node is
                    # actually port of 'curr_node'
                    forward_path['dpid'] = curr_node['dpid']
                    forward_path['in_port'] = prev_node['in_port']
                    forward_path['out_port'] = next_node['in_port']
                    forward_path['vlan'] = dest_nfv['vlan']

                    reverse_path['dpid'] = curr_node['dpid']
                    reverse_path['in_port'] = reverse_node['in_port']
                    reverse_path['out_port'] = prev_node['out_port']
                    reverse_path['vlan'] = curr_vlan
                except Exception as err:
                    print "[ERROR] this dest_nfv route fail"
                    return None

                forward_path_list.append(forward_path)
                reverse_path_list.append(reverse_path)

                prev_node = curr_node
                prev_node['in_port'] = next_node['in_port']
                prev_node['out_port'] = next_node['out_port']

                curr_node['dpid'] = next_node['nexthop_dpid']

            all_service_path_list['forward'].append(forward_path_list)
            all_service_path_list['reverse'].append(reverse_path_list)

        con.close()
        return all_service_path_list
    
    def apply_default_rule(self, conf, userid):
        result = dict()
        result['message'] = "FAIL"
        result['services'] = list()

        try:
            con = mdb.connect("localhost", "root", "of#123", "skdemo2")
            cur = con.cursor(mdb.cursors.DictCursor)
        except:
            print "[ERROR] DB Connect Fail"
            return result

        all_path = self.calculate_path_by_default_rule(conf)
        
        d_wildcards = mul_nbapi.OFPFW_ALL & ~(mul_nbapi.OFPFW_NW_DST_MASK) & ~(mul_nbapi.OFPFW_DL_TYPE) & ~(mul_nbapi.OFPFW_IN_PORT)
        s_wildcards = mul_nbapi.OFPFW_ALL & ~(mul_nbapi.OFPFW_NW_SRC_MASK) & ~(mul_nbapi.OFPFW_DL_TYPE) & ~(mul_nbapi.OFPFW_IN_PORT)

        forward_list = all_path['forward']
        reverse_list = all_path['reverse']

        cur.execute("SELECT * FROM user, ippool WHERE user.userid = ippool.user_id AND user.userid = %s", userid)
        chain_list = cur.fetchall()
        num = 0
        for chain in chain_list:
            service_num = chain['service_id'] - 1
            forward_iter = forward_list[service_num].__iter__()
            reverse_iter = reverse_list[service_num].__iter__()
            flow_add_start = True

            try:
                #delete tuple from servicechainrule
                #self.insertORUpdateServiceChainLog(chain["chain_id"], 
                cur.execute("DELETE FROM servicechainrule WHERE chain_id = %s", chain["chain_id"])
                pass
            except:
                pass
           
            while True:
                if flow_add_start is True:
                    forward_ip = chain['userip']
                    reverse_ip = chain['ip']
                    allocIP_src = chain['ip']
                    allocIP_dst = chain['userip']
                    flow_add_start = False
                else:
                    forward_ip = chain['ip']
                    reverse_ip = forward_ip
                    allocIP_src = None
                    allocIP_dst = None
                
                try:
                    forward = forward_iter.next()
                    reverse = reverse_iter.next()
                except StopIteration:
                    break

                try:
                    #print "forward" ,forward, forward_ip, allocIP_src
                    #print "reverse", reverse, reverse_ip, allocIP_dst
                    #print ""
                
                    self.controller_call_for_flowadd(cur, chain['chain_id'], forward['dpid'],  forward_ip, None, forward['in_port'], forward['out_port'], s_wildcards, 0, allocIP_src)
                    self.controller_call_for_flowadd(cur, chain['chain_id'], reverse['dpid'],  None, reverse_ip, reverse['in_port'], reverse['out_port'], d_wildcards, 0, allocIP_dst)

                    #insert tuple to servicechainrule
                    #cur.execute("INSERT INTO servicechainrule (chain_id, sip, dip, inport, outport, dpid, vlan, wildcard, prior) VALUES (%s, %s, NULL, %s, %s, %s, %s, %s, 0)", (chain['chain_id'], forward_ip, forward['in_port'], forward['out_port'], forward['dpid'], 0, s_wildcards))
                    #cur.execute("INSERT INTO servicechainrule (chain_id, sip, dip, inport, outport, dpid, vlan, wildcard, prior) VALUES (%s, NULL, %s, %s, %s, %s, %s, %s, 0)", (chain['chain_id'], reverse_ip, reverse['in_port'], reverse['out_port'], reverse['dpid'], 0, d_wildcards))
                except:
                    con.rollback()
                    return result
            
            cur.execute("SELECT sa.service_type, sa.service_id FROM sa WHERE service_id = %s", chain['service_id'])
            row = cur.fetchone()
            result['services'].append({"service_type" : row['service_type'], "service_id" : row['service_id']})

        try:
            con.commit() 
        except:
            con.rollback()
            return result

        con.close()
        result['message'] = "SUCCESS"
        return result

    
    def get_default_rule(self, conf):
        try:
            con = mdb.connect("localhost", "root", "of#123", "skdemo2")
            cur = con.cursor(mdb.cursors.DictCursor)
        except:
            print "[ERROR] Fail to connect DB"
            return {"message" : "FAIL"}

        cur.execute("SELECT * FROM defaultRule ORDER BY nfv_order ASC")
        rule_list = cur.fetchall()

        result = dict()
        result['nfv_list'] = list()
        for rule in rule_list:
            result['nfv_list'].append(rule['nfv'])
            
        con.close()
        return result


    def parse_logical_dpid(logical_dpid):
        try:
            con = mdb.connect("localhost", "root", "of#123", "skdemo2")
            cur = con.cursor(mdb.cursors.DictCursor)
        except:
            print "[ERROR] Fail to connect DB"
            return logical_dpid

        cur.execute("SELECT * FROM logicswitch WHERE logical_dpid = %s", logical_dpid)
        dpid = cur.fetchone()

        cur.close()
        con.close()

        if not dpid:
            return logical_dpid

        real_dpid = dpid["dpid"]
        return real_dpid


    def mapping_dpid_to_logical(self, real_dpid):
        try:
            con = mdb.connect("localhost", "root", "of#123", "skdemo2")
            cur = con.cursor(mdb.cursors.DictCursor)
        except:
            return real_dpid

        cur.execute("SELECT * FROM logicswitch WHERE dpid = %s", real_dpid)
        dpid = cur.fetchone()

        cur.close()
        con.close()

        if not dpid:
            return real_dpid

        else:
            return str(dpid["logical_dpid"])


    def mapping_dpid_to_real(self, logical_dpid):
        try:
            con = mdb.connect("localhost", "root", "of#123", "skdemo2")
            cur = con.cursor(mdb.cursors.DictCursor)
        except:
            return logical_dpid

        cur.execute("SELECT * FROM logicswitch WHERE logical_dpid = %s", logical_dpid)
        dpid = cur.fetchone()

        cur.close()
        con.close()

        if not dpid:
            return logical_dpid
        else:
            return str(dpid["dpid"])

    def create_service_by_chain_log(self, conf, params, admin=True):
        try:
            con = mdb.connect("localhost", "root", "of#123", "skdemo2")
            cur = con.cursor(mdb.cursors.DictCursor)
        except:
            print "[ERROR] Fail to connect DB"
            pass
        dpid = self.mapping_dpid_to_logical(params["dpid"])
        port_num = params["port"]
        src_ip_addr = params["ip"]


        """ search for a user """
        #cur.execute("SELECT * FROM user WHERE userip = %s AND active = 1", src_ip_addr)
        cur.execute("SELECT * FROM user as a, ippool as b WHERE userip = %s AND active = 1 AND a.userid = b.user_id", src_ip_addr)
        user = cur.fetchone()

        if not user:
            print "[ERROR] Fail to search for user"
            return 404
        
        """ search for a service type """
        cur.execute("SELECT * FROM sa WHERE dpid = %s AND ssg_port = %s", (dpid, port_num))
        sa_list = cur.fetchall()

        if not sa_list:
            print "[ERROR] Fail to search for a service"
            return 400
        """ This code is static code. must be modified """
        if self.get_sdn_mode() == False:
            nfv_list = ["vWTCP", "vDPI", "vURL_Filtering", "vHE", "DPI", "VOMS"]
            for sa in sa_list:
                node = self.create_service(conf, user["phone_num"], sa["service_type"], {"nfv_list":nfv_list}, admin)

            return 201
        """ This code is static code. must be modified """

        for sa in sa_list:
            cur.execute("SELECT nfv_name FROM servicechainlog WHERE chain_id = %s", user["chain_id"])
            log_list = cur.fetchall()
            
            if not log_list:
                cur.execute("SELECT nfv_name FROM servicechainlog WHERE chain_id = %s", self.default_table[sa["service_id"]])
                log_list = cur.fetchall()
                if not log_list:
                    return 404

            nfv_list = dict()
            nfv_list["nfv_list"] = list()
            for log in log_list:
                nfv_list["nfv_list"].append(log["nfv_name"])

            node = self.create_service(conf, user["phone_num"], sa["service_type"], nfv_list)
            if node["message"] != "SUCCESS":
                return 500

        return 201
        """
        for sa in sa_list:
            cur.execute("SELECT nfv_name FROM servicechainlog WHERE chain_id IN (SELECT chain_id FROM ippool WHERE user_id = %s AND service_id = %s)", (user["userid"], sa["service_id"]) )
            log_list = cur.fetchall()
            params = dict()
            params["nfv_list"] = list()
            
            if not log_list:
                print "[WARNING] Failt to search for a log : set default rule"
                #cur.execute("SELECT * FROM defaultRule ORDER BY nfv_order")
                cur.execute("SELECT * FROM user WHERE userip = %s", self.default_user_ip)
                default_user = cur.fetchone()
                cur.execute("SELECT nfv_name FROM servicechainlog WHERE chain_id IN (SELECT chain_id FROM ippool WHERE user_id = %s AND service_id = %s)", (default_user["userid"], sa["service_id"]) )
                log_list = cur.fetchall()
                if not log_list:
                    print "[ERROR] default rule is nothing"
                    return 404

            for log in log_list:
                params["nfv_list"].append(log["nfv_name"])

            node = self.create_service(conf, user["phone_num"], sa["service_type"], params, admin)
            
            if node["message"] == "FAIL":
                print "[ERROR] Fail to create user service"
                return 400
            
        return 201
        """
    def delete_service_by_chain_log(self, conf, dpid, port_num, src_ip_addr, admin=True):
        try:
            con = mdb.connect("localhost", "root", "of#123", "skdemo2")
            cur = con.cursor(mdb.cursors.DictCursor)
        except:
            print "[ERROR] Fail to connect DB"
            pass

        cur.execute("SELECT * FROM user WHERE userip = %s", src_ip_addr)
        user = cur.fetchone()

        if not user:
            print "[ERROR] Fail to search for a user"
            return 404

        dpid = self.mapping_dpid_to_logical(dpid)
        cur.execute("SELECT * FROM sa WHERE dpid = %s AND ssg_port = %s", (dpid, port_num))
        sa_list = cur.fetchall()

        if not sa_list:
            print "[ERROR] Fail to search for a service"
            return 400

        cur.execute("SELECT * FROM defaultRule ORDER BY nfv_order")
        default_list = cur.fetchall()

        for sa in sa_list:
            cur.execute("SELECT * FROM ippool WHERE user_id = %s AND service_id = %s", (user["userid"], sa["service_id"]))
            chain = cur.fetchone()
            
            if not chain:
                continue
            result = self.delete_service(conf, chain["chain_id"], admin)
            if result["message"] == "FAIL":
                return 500

        return 200


    
    def create_legacy_service(self, conf, params):
        try:
            con = mdb.connect("localhost", "root", "of#123", "skdemo2")
            cur = con.cursor(mdb.cursors.DictCursor)
        except:
            print "[ERROR] Fail to connect DB"
            return {"message" : "FAIL"}

        #self.change_sdn_mode(conf, False)
        if self.get_sdn_mode() == True:
            self.set_sdn_mode(False)
            cur.execute("SELECT chain_id FROM servicechainrule GROUP BY chain_id")
            chain_list = cur.fetchall()

            for chain in chain_list:
                self.delete_service(conf, chain["chain_id"], True)

        cur.execute("SELECT nfv FROM defaultRule ORDER BY nfv_order")
        default_list = cur.fetchall()

        nfv_list = dict()
        nfv_list["nfv_list"] = [nfv["nfv"] for nfv in default_list]

        cur.execute("SELECT * FROM sa")
        service_list = cur.fetchall()

        phone_num = params["mdn"]
        result = list()

        if phone_num == "ALL":
            cur.execute("SELECT * FROM user WHERE active = 1")
            user_list = cur.fetchall()
            for user in user_list:
                for service in service_list:
                    node = self.create_service(conf, user["phone_num"], service["service_type"], nfv_list, True)
                    if node["message"] != "SUCCESS":
                        return {"message" : "FAIL"}
        else:        
            for service in service_list:
                node = self.create_service(conf, phone_num, service["service_type"], nfv_list, True)
            if node["message"] != "SUCCESS":
                return {"message" : "FAIL"}
        
        return {"message" : "SUCCESS"}
      
 
    def get_sdn_mode(self):
        return self.sdn_mode

    def set_sdn_mode(self, mode):
        self.sdn_mode = mode

    def change_sdn_mode(self, conf, mode=True):
        try:
            con = mdb.connect("localhost", "root", "of#123", "skdemo2")
            cur = con.cursor(mdb.cursors.DictCursor)
        except:
            print "[ERROR] Fail to connect DB"
            pass

        result = {"message" : "SUCCESS"}
        if self.get_sdn_mode() != mode:
            self.set_sdn_mode(mode)
            #cur.execute("SELECT chain_id FROM servicechainrule GROUP BY chain_id")
            cur.execute("SELECT * FROM servicechainrule WHERE sip IS NOT null GROUP BY chain_id")
            chain_list = cur.fetchall()

            for chain in chain_list:
                self.delete_service(conf, chain["chain_id"], True)
            
            cur.execute("SELECT * FROM sa WHERE active = 1")
            service_list = cur.fetchall()

            cur.execute("SELECT * FROM user WHERE active = 1")
            user_list = cur.fetchall()
            

            if self.get_sdn_mode() is True:
                for user in user_list:
                    cur.execute("SELECT a.chain_id, b.service_type FROM ippool as a, sa as b WHERE a.service_id = b.service_id AND user_id = %s", user["userid"])
                    chain_list = cur.fetchall()
                    
                    nfv_list = dict()
                    for chain in chain_list:
                        cur.execute("SELECT nfv_name FROM servicechainlog WHERE chain_id = %s", chain["chain_id"])
                        log_list = cur.fetchall()
                        nfv_list["nfv_list"] = [nfv["nfv_name"] for nfv in log_list]
                        node = self.create_service(conf, user["phone_num"], chain["service_type"], nfv_list, True)
                        if node["message"] != "SUCCESS":
                            return {"message" : "what"}
                
            else:
                cur.execute("SELECT nfv FROM defaultRule ORDER BY nfv_order")
                default_list = cur.fetchall()

                nfv_list = dict()
                nfv_list["nfv_list"] = [nfv["nfv"] for nfv in default_list]

                phone_num = params["mdn"]
                result = list()

                for user in user_list:
                    for service in service_list:
                        node = self.create_service(conf, user["phone_num"], service["service_type"], nfv_list, True)
                        if node["message"] != "SUCCESS":
                            return {"message" : "FAIL"}

           
        else:
            result["message"] = "SUCCESS"
        con.close()
        cur.close()
        return result

