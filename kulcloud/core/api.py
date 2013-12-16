

import logging
import functools
import eventlet
import copy
import pdb

from openstack.common import exception
import kulcloud.exception as exc

from kulcloud.core import commands
#from kulcloud.core import topology_status
from kulcloud.core import scheduler
from kulcloud import drivers
from kulcloud.db import api as db_api
from kulcloud.common import utils
from kulcloud.common import cfg
from kulcloud.core.v1.mlapi import mlapi


LOG = logging.getLogger(__name__)
NOT_SUPPORTED = "not supported yet"
mul_intf = {}



"""
mul_interface_opts = [
    # TODO:
    cfg.StrOpt('servers', default='localhost:8800'),
    cfg.StrOpt('serverauth', default='username:password'),
    cfg.BoolOpt('serverssl', default=False),
    cfg.BoolOpt('syncdata', default=False),
    cfg.IntOpt('servertimeout', default=10),
]

cfg.CONF.register_opts(mul_interface_opts, "MUL_NBAPI")


class Mul_interface(object):
    def __init__(self, args):
        LOG.debug("Initializing the Mul_interface  % : " % args)
        services = cfg.CONF.MUL_NBAPI.services
"""


        


def make_client():
	"""
    version_map = {'1.0':'kulcloud.core.v1.mlapi.mlapi'}
    for k,v in version_map.items():
	       mul_intf[k]=utils.import_class(v)
	"""
	mul_intf['1.0'] = mlapi()

        
def asynchronous(func):
    @functools.wraps(func)
    def _inner(*args, **kwargs):
        if kwargs.pop('async', True):
            eventlet.spawn(func, *args, **kwargs)
        else:
            return func(*args, **kwargs)
    return _inner


""" fabric manager """

def Fabric_get_index(conf, version):    
    return NOT_SUPPORTED

def fabric_get_data(conf, version, topology_id):
    return NOT_SUPPORTED


def fabric_show_details(conf, version, topology_id):
    return NOT_SUPPORTED


def create_Fabric(conf, version, params):
    return NOT_SUPPORTED


@asynchronous
def update_fabric(conf, version, topology_id, topology_body):
    return NOT_SUPPORTED
    

def delete_fabric(conf, version, topology_id):
    return NOT_SUPPORTED



""" Flowtable Manager"""
def flowtable_get_index(conf, version):
    return NOT_SUPPORTED     

def create_flowtable(conf, version, params):
    return NOT_SUPPORTED

def delete_flowtable(conf, version, dpid):
    return NOT_SUPPORTED

def flowtable_get_data(conf, version, dpid):
    return NOT_SUPPORTED

def flowtable_show_details(conf, version, dpid):
    return NOT_SUPPORTED

def update_flowtable(conf, version, dpid, body):
    return NOT_SUPPORTED





""" Stats Manager """

def stats_get_index(conf, version):
    return NOT_SUPPORTED


def stats_get_data(conf, version, dpid):
    return NOT_SUPPORTED


def stats_show_details(conf, version, dpid): 
    return NOT_SUPPORTED


def create_stats(conf, version, params):
    return NOT_SUPPORTED


@asynchronous
def update_stats(conf, version, dpid, stats_body):
    return NOT_SUPPORTED
  

def delete_stats(conf, version, dpid):
    return NOT_SUPPORTED
   
""" Stats Flow Manager """

def stats_flow_get_index(conf, version, dpid): 
    stats_list = mul_intf[version].get_all_stat(conf, dpid)
    return stats_list

def stats_flow_get_data(conf, version, dpid, flow_id):
	#TODO : MLAPI Integration  
    flow_list = []    
    flow = {"flow_id":"1", "bps":"1", "pps":"1","pkt_count":"1","byte_count":"1"}
    flow_list.append(flow)
    return {'flows':flow_list}


def stats_flow_show_details(conf, version, dpid, flow_id): 
    return NOT_SUPPORTED


def create_stats_flow(conf, version, dpid, params):
    return NOT_SUPPORTED


@asynchronous
def update_stats_flow(conf, version, dpid, flow_id, stats_body):
    return NOT_SUPPORTED
  

def delete_stats_flow(conf, version, dpid, flow_id):
    return NOT_SUPPORTED


def stats_port_get_index(conf, version, dpid, port_no):
    stats_list = mul_intf[version].get_stat_port(conf, dpid, port_no)
    return stats_list


""" Flow Manager """
def flow_unpack_extra(flow):
    return

def flow_get_index(conf, version, dpid):
	#TODO : MLAPI Integration      
    flow_list = []
    action_list = []
    action = {'action':'x','value':'x'}
    flow = {'flow_id':'x','priority':'x','in_port':'x','src_mac':'x',
            'dst_mac':'x','src_nw':'x','dst_nw':'x','vlan_id':'x',
            'src_port':'x','dst_port':'x','actions':[]}
    flow['actions'].append(action)
    flow_list.append(flow)
    
    """With MUL SWIG Service
    flow_list = mul_intf[version].get_all_flow(conf, dpid)
    flow_list = [flow_unpack_extra(flow) for flow in flow_list]
    """   

    return {'flows':flow_list}


def flow_get_data(conf, version, dpid, flow_id ):
	#TODO : MLAPI Integration  
    flow = {'flow_id':'x','priority':'x','in_port':'x','src_mac':'x',
            'dst_mac':'x','src_nw':'x','dst_nw':'x','vlan_id':'x',
            'src_port':'x','dst_port':'x','actions':[]}
    
    """With MUL SWIG Service
    flow = mul_intf[version].get_flow(conf, dpid, flow_id)
    return flow
    """
    return flow


def flow_show_details(conf, version, dpid, flow_id):
    return NOT_SUPPORTED


def create_flow(conf, version, dpid, params):
    flow_id = mul_intf[version].create_flow(conf, dpid, params)
    return {'flow_id':flow_id}

@asynchronous
def update_flow(conf, version, dpid, flow_id, params):
	#TODO : MLAPI Integration  
    """With MUL SWIG Service
    flow_id = mul_intf[version].update_flow(conf, dpid, flow_id, params)
    return {'flow_id':flow_id}
    """
    return {'flow_id' : 1} 



def delete_flow(conf, version, dpid, flow_id):
    flow_id = mul_intf[version].delete_flow(conf, dpid, flow_id)
    return {'flow_id':flow_id}
 
    
""" Switch Manager"""
def switch_unpack_extra(sw_list):
    return
    
def switch_get_index(conf, version):
    sw_list = mul_intf[version].get_all_switch(conf)
    return {'switches': sw_list}

def create_switch(conf, version, params):
    return NOT_SUPPORTED

def delete_switch(conf, version, dpid):
    return NOT_SUPPORTED

def switch_get_data(conf, version, dpid):
    sw = mul_intf[version].get_switch(conf, dpid)
    return sw

def switch_show_details(conf, version, flow_id):
    return NOT_SUPPORTED

def update_switch(conf, version, lb_id, body):
    return NOT_SUPPORTED


""" Port Manager"""
def port_unpack_extra(port_list):
    return
    
    
def port_get_index(conf, version, dpid):
    port_list = mul_intf[version].get_all_port(conf, dpid)
    return {'ports':port_list}    

def create_port(conf, version, dpid, params):
    return NOT_SUPPORTED

def delete_port(conf, version, dpid, port_id):
    return NOT_SUPPORTED

def port_get_data(conf, version, dpid, port_id):
    port = mul_intf[version].get_port(conf, dpid, port_id)
    return port

def port_show_details(conf, version, dpid, port_id):
    return NOT_SUPPORTED

def update_port(conf, version, dpid, port_id, body):
    return NOT_SUPPORTED


""" Link Manager"""
def link_get_index(conf, version):
	#TODO : MLAPI Integration  
    sw_list=[]
    sw={'dpid':'xxx'}
    link={'ports':[{'port_no':'x','neighbor':'neighbor_dpid',
                    'neighbor_port':'neighbor_port'}]}    
    sw['links']=link    
    sw_list.append(sw)
    
    """With MUL SWIG Service
    sw_list = mul_intf[version].get_all_switch(conf)
    for sw in sw_list:
        link=mul_intf[version].get_all_link(sw['dpid'])   
        sw['links']=link_unpack_extra(link)    
    """    
    
    return {'switches':sw_list}    

def create_link(conf, version, params):
    return NOT_SUPPORTED

def delete_link(conf, version, dpid):
    return NOT_SUPPORTED

def link_get_data(conf, version, dpid):	
    resp = mul_intf[version].get_link(conf, dpid)    
    return resp

def link_show_details(conf, version, dpid):
    return NOT_SUPPORTED
   
def update_link(conf, version, dpid, body):
    return NOT_SUPPORTED

""" Route Manager"""
def route_get_index(conf, version):
	#TODO : MLAPI Integration  
    return {'algorithms':['warshall', 'dijkstra']}

def create_route(conf, version, params):
    return NOT_SUPPORTED

def delete_route(conf, version, link_id):
    return NOT_SUPPORTED

def route_get_data(conf, version, link_id):
    return NOT_SUPPORTED

def route_show_details(conf, version, link_id):
    return NOT_SUPPORTED

def update_route(conf, version, link_id, body):
    return NOT_SUPPORTED

""" path Manager"""
def path_unpack_extra(path):
    return

def path_show_route_path(conf, version, src_dpid, src_port, dst_dpid, dst_port):
    path_list = mul_intf[version].path_show_route_path(conf, version, src_dpid, src_port, dst_dpid, dst_port)
    return path_list    


def path_get_index(conf, version):  
	#TODO : MLAPI Integration    
    path_list = []
    path = {}
    hops = []
    hop_1 = {}
    hop_2 = {}
    
    path['path_id'] = 1
    path['src_dev_id'] = 1
    path['dst_dev_id'] = 2
    path['algorithm'] = "warshall"
    
    hop_1['hop_count'] = 0
    hop_1['dpid'] = 1
    hop_1['outgress_port'] = 1
    hop_1['neighbor'] = 2
    hop_1['neighbor_port'] = 3
    hop_1['flow_id'] = 1
    
    hop_2['hop_count'] = 1
    hop_2['dpid'] = 2 
    hop_2['outgress_port'] = 3
    hop_2['neighbor'] = 3
    hop_2['neighbor_port'] = 4
    hop_2['flow_id'] = 2
    
    hops.append(hop_1)
    hops.append(hop_2)
    path['hops'] = hops
    path_list.append(path) 
    
    """With MUL SWIG Service
    path_list = mul_intf[version].get_all_path(conf)
    path_list = [path_unpack_extra(path) for path in path_list]
    """
    
    return {'paths':path_list}

def create_path(conf, version, params):
	#TODO : MLAPI Integration  
    return {'path_id':1}

def delete_path(conf, version, path_id):
	#TODO : MLAPI Integration  
    return {'path_id':1}

def path_get_data(conf, version, path_id):
	#TODO : MLAPI Integration  
    path = {}
    hops = []
    hop_1 = {}
    hop_2 = {}
    
    path['path_id'] = 1
    path['src_dev_id'] = 1
    path['dst_dev_id'] = 2
    path['algorithm'] = "warshall"
    
    hop_1['hop_count'] = 0
    hop_1['dpid'] = 1
    hop_1['outgress_port'] = 1
    hop_1['neighbor'] = 2
    hop_1['neighbor_port'] = 3
    hop_1['flow_id'] = 1
    
    hop_2['hop_count'] = 1
    hop_2['dpid'] = 2 
    hop_2['outgress_port'] = 3
    hop_2['neighbor'] = 3
    hop_2['neighbor_port'] = 4
    hop_2['flow_id'] = 2
    
    hops.append(hop_1)
    hops.append(hop_2)
    path['hops'] = hops
    
    
    """With MUL SWIG Service
    path = mul_intf[version].get_path(path_id)
    path = path_unpack_extra(path)
    """
    
    return path

def path_show_details(conf, version, link_id):
    return NOT_SUPPORTED

def update_path(conf, version, link_id, body):
	#TODO : MLAPI Integration  
    return {'path_id':1}



""" Tenant Manager"""
def tenant_get_index(conf, version):
    return NOT_SUPPORTED    

def create_tenant(conf, version, params):
    return NOT_SUPPORTED

def delete_tenant(conf, version, tenant_id):
    return NOT_SUPPORTED

def tenant_get_data(conf, version, tenant_id):
    return NOT_SUPPORTED

def tenant_show_details(conf, version, tenant_id):
    return NOT_SUPPORTED

def update_tenant(conf, version, tenant_id, body):
    return NOT_SUPPORTED

""" Network Manager"""
def network_get_index(conf, version, tenant_id):
    return NOT_SUPPORTED   

def create_network(conf, version, tenant_id, params):
    return NOT_SUPPORTED

def delete_network(conf, version, tenant_id, network_id):
    return NOT_SUPPORTED
 
def network_get_data(conf, version, tenant_id, network_id):
    return NOT_SUPPORTED

def network_show_details(conf, version, tenant_id, network_id):
    return NOT_SUPPORTED

def update_network(conf, version, tenant_id, network_id, body):
    return NOT_SUPPORTED

""" Host Manager"""
def host_unpack_extra(host):
    return

def host_get_index(conf, version, tenant_id, network_id):
    host_list = mul_intf[version].get_all_host(conf, tenant_id, network_id)
    return {'hosts':host_list}

def create_host(conf, version, tenant_id, network_id, params):
    host_id = mul_intf[version].create_host(conf, tenant_id, network_id, params)
    return {'host_id':host_id}
   

def delete_host(conf, version, tenant_id, network_id, host_id):
    host_id = mul_intf[version].delete_host(conf, tenant_id, network_id, host_id)
    return {'host_id':host_id}

def host_get_data(conf, version, tenant_id, network_id, host_id):
	#TODO : MLAPI Integration  
    host = {}
    host['host_id'] = 1
    host['dpid'] = 1
    host['port'] = 1
    host['host_ip'] = 1
    host['host_mac'] = 1
    
    """With MUL SWIG Service
    host = mul_intf[version].get_host(conf, tenant_id, network_id, host_id)
    host = host_unpack_extra(host)
    """  
    
    return host

def host_show_details(conf, version, tenant_id, network_id, host_id):
    return NOT_SUPPORTED

def update_host(conf, version, tenant_id, network_id, host_id, body):
    """With MUL SWIG Service
    host_id = mul_intf[version].update_host(conf, tenant_id, network_id, host_id, body)
    """ 
    return {'host_id' : 1} 



""" Default Rule """
def create_default_rule(conf, version, body):
    result = mul_intf[version].create_default_rule(conf, "ALL", body)
    return result

""" Service Manager"""
def create_service_by_chain_log(conf, version, params):
    result = mul_intf[version].create_service_by_chain_log(conf, params)
    return result

def delete_service_by_chain_log(conf, version, dpid, port, ip):
    result = mul_intf[version].delete_service_by_chain_log(conf, dpid, port, ip)
    return result

def create_legacy_service(conf, version, body):
    result = mul_intf[version].create_legacy_service(conf, body)
    return result

def old_delete_service(conf, version, phone_num, service_type):
    result = mul_intf[version].old_delete_service(conf, phone_num, service_type)
    return result
 
def service_get_data(conf, version, phone_num, service_type):
    result = mul_intf[version].get_service(conf, phone_num, service_type)
    return {'phone_num':result}

def service_show_details(conf, version, phone_num, service_type):
    return NOT_SUPPORTED

def servicech_show_service_chain_list(conf, version, service_chain_id):
    #print "what" 
    result = mul_intf[version].show_service_chain_list(conf, service_chain_id)
    return result

def servicech_show_statistic_service_chain(conf, version, service_chain_id):
    result = mul_intf[version].show_statistic_service_chain(conf, service_chain_id)
    return result

def show_switch_list(conf, version):
    result = mul_intf[version].show_switch_list(conf)
    return result

def show_switch_statistic(conf, version, dpid):
    result = mul_intf[version].show_switch_statistic(conf, dpid)
    return result



""" SADB Manager"""
def SADB_get_index(conf, version):
    result = mul_intf[version].get_all_sadb(conf)
    return result   

def create_SADB(conf, version, params):
    result = mul_intf[version].create_SADB(conf, params)
    return result

def delete_SADB(conf, version, service_type):
    result = mul_intf[version].delete_SADB(conf, service_type)
    return result


""" NFVDB Manager"""
def nfvdb_get_index(conf, version):
    result = mul_intf[version].get_all_nfvdb(conf)
    return result   

def nfvdb_get_index_bymdn(conf, version, mdn):
    result = mul_intf[version].get_nfvdb_bymdn(conf, mdn)
    return result  

def nfvdb_get_vm(conf, version):
    result = mul_intf[version].get_nfvdb_vm(conf)
    return result 

def create_nfvdb(conf, version, params):
    result = mul_intf[version].create_nfvdb(conf, params)
    return result

def delete_nfvdb(conf, version, name):
    result = mul_intf[version].delete_nfvdb(conf, name)
    return result

def update_nfvdb(conf, version, name, body):
    result = mul_intf[version].update_nfvdb(conf, name, body)
    return result



def sync_nfvtopology(conf, version):
    result = mul_intf[version].resync_nfvtopo(conf)
    return result

def sync_servicech(conf, version):
    result = mul_intf[version].resync_servicech(conf)
    return result

def sync_service(conf, version):
    result = mul_intf[version].resync_service(conf)
    return result

def sync_nfvgroup(conf, version):
    result = mul_intf[version].resync_nfvgroup(conf)
    return result

def sync_servicechaindefaultrule(conf, version):
    result = mul_intf[version].resync_servicechaindefaultrule(conf)
    return result





def create_nfvvmdb(conf, version, params):
    result = mul_intf[version].create_nfvvmdb(conf, params)
    return result

def get_nfvvmStatistic(conf, version, nfv_name):
    result = mul_intf[version].get_vm_statistic(conf, nfv_name)
    return result

def get_nfvGroupStatistic(conf, version, nfv_groupname):
    result = mul_intf[version].get_group_statistic(conf, nfv_groupname)
    return result

def update_nfvvmThresholddb(conf, version, name, body):
    result = mul_intf[version].update_nfvvmThresholddb(conf, name, body)
    return result

def get_nfv_vm_threshold(conf, version, nfvid):
    result = mul_intf[version].get_nfv_vm_threshold(conf, nfvid)
    return result

def get_stat_port(conf, version, dpid, port_num):
    result = mul_intf[version].get_stat_port(conf, dpid, port_num)
    return result

"""Default rule api - From NFVDB"""
def get_default_rule(conf, version):
    result = mul_intf[version].get_default_rule(conf)
    return result

def change_sdn_mode(conf, version):
    result = mul_intf[version].change_sdn_mode(conf)
    return result
   
def get_current_sdn_mode(conf, version):
    result = mul_intf[version].get_current_sdn_mode(conf)
    return result

def create_service_wrapper(conf, version, body):
    result = mul_intf[version].create_service_wrapper(conf, body)
    return result 

def get_vm_map(conf, version):
    result = mul_intf[version].get_vm_map(conf)
    return result

def get_vm_threshold(conf, version):
    result = mul_intf[version].get_vm_threshold(conf)
    return result


""" Kulcloud-NFV-NBAPI START """


"""NFVTopologyManager api - From NFVTopologyMgr"""
def create_nfvtopo(conf, version, body):
    result = mul_intf[version].create_nfvtopo(conf, body)
    return result

def index_nfvtopo(conf, version):
    result = mul_intf[version].index_nfvtopo(conf)
    return result

def update_nfvtopo(conf, version, name, body):
    result = mul_intf[version].update_nfvtopo(conf, name, body)
    return result 

def show_nfvtopo(conf, version, name):
    result = mul_intf[version].show_nfvtopo(conf, name)
    return result

def delete_nfvtopo(conf, version, name):
    result = mul_intf[version].delete_nfvtopo(conf, name)
    return result

"""NFVGroupManager api - From NFVGroupMgr"""
def create_nfvgroup(conf, version, body):
    result = mul_intf[version].create_nfvgroup(conf, body)
    return result

def index_nfvgroup(conf, version):
    result = mul_intf[version].index_nfvgroup(conf)
    return result

def update_nfvgroup(conf, version, name, body):
    result = mul_intf[version].update_nfvgroup(conf, name, body)
    return result 

def show_nfvgroup(conf, version, name):
    result = mul_intf[version].show_nfvgroup(conf, name)
    return result

def delete_nfvgroup(conf, version, name):
    result = mul_intf[version].delete_nfvgroup(conf, name)
    return result

""" ServiceChain Manager"""
def index_servicech(conf, version):
    result = mul_intf[version].index_servicech(conf)
    return result   

def create_servicech(conf, version, body):
    result = mul_intf[version].create_servicech(conf, body)
    return result

def delete_servicech(conf, version, name):
    result = mul_intf[version].delete_servicech(conf, name)
    return result
 
def show_servicech(conf, version, name):
    result = mul_intf[version].show_servicech(conf, name)
    return result

def update_servicech(conf, version, name, body):
    result = mul_intf[version].update_servicech(conf, name, body)
    return result

"""ServiceChainDefaultRuleManager api - From ServiceChainDefaultRuleMgr"""
def create_servicechaindefaultrule(conf, version, body):
    result = mul_intf[version].create_servicechaindefaultrule(conf, body)
    return result

def index_servicechaindefaultrule(conf, version):
    result = mul_intf[version].index_servicechaindefaultrule(conf)
    return result

def update_servicechaindefaultrule(conf, version, name, body):
    result = mul_intf[version].update_servicechaindefaultrule(conf, name, body)
    return result 

def show_servicechaindefaultrule(conf, version, name):
    result = mul_intf[version].show_servicechaindefaultrule(conf, name)
    return result

def delete_servicechaindefaultrule(conf, version, name):
    result = mul_intf[version].delete_servicechaindefaultrule(conf, name)
    return result


"""TopologyManager api - From TopologyMgr"""
def create_topology(conf, version, params):
    return NOT_SUPPORTED

def index_topology(conf, version):
    result = mul_intf[version].index_topology(conf)
    return result

@asynchronous
def update_topology(conf, version, name, body):
    return NOT_SUPPORTED

def show_topology(conf, version, name):
    result = mul_intf[version].show_topology(conf, name)
    return result  

def delete_topology(conf, version, name):
    return NOT_SUPPORTED

"""ServiceManager api - From ServiceMgr"""
def index_service(conf, version, name):
    result = mul_intf[version].index_service(conf, name)
    return result   

def create_service(conf, version, name, service_type, params):
    result = mul_intf[version].create_service(conf, name, service_type, params)
    return result

def delete_service(conf, version, name):
    result = mul_intf[version].delete_service(conf, name)
    return result

@asynchronous
def update_service(conf, version, name, body):
    result = mul_intf[version].update_service(conf, name, body)
    return result

def show_service(conf, version, name):
    result = mul_intf[version].show_topology(conf, name)
    return result  
