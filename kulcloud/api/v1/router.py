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

import logging

import routes

from . import FabricManager
from . import TenantManager
from . import NetworkManager
from . import HostManager
from . import FlowtableManager
from . import FlowManager
from . import StatsManager
from . import StatsFlowManager
from . import SwitchManager
from . import PortManager
from . import LinkManager
from . import RouteManager
from . import PathManager
from . import SADBManager
from . import NFVDBManager

""" Kulcloud NFV Solution Manager """
from . import ServiceManager
from . import ServiceChainManager
from . import TopologyManager
from . import NFVTopologyManager
from . import NFVGroupManager
from . import ServiceChainDefaultRuleManager

from kulcloud.core import api as core_api

#from . import tasks


from openstack.common import wsgi


logger = logging.getLogger(__name__)


class API(wsgi.Router):

    """WSGI router for Kulcloud NBAPI v1 API requests."""
    """URI: /{version}/function/{args}. """

    def __init__(self, conf, **local_conf):
        self.conf = conf
        #core_api.make_client(conf['version'])
        core_api.make_client()
        mapper = routes.Mapper()

        version_mapper = mapper.submapper(path_prefix="/{version}")

        Fabric_resource = FabricManager.create_resource(self.conf)
        Tenant_resource = TenantManager.create_resource(self.conf)
        Network_resource = NetworkManager.create_resource(self.conf)
        Host_resource = HostManager.create_resource(self.conf)        
        Flowtable_resource = FlowtableManager.create_resource(self.conf)
        Flow_resource = FlowManager.create_resource(self.conf)
        Stats_resource = StatsManager.create_resource(self.conf)
        Stats_flow_resource = StatsFlowManager.create_resource(self.conf)        
        Switch_resource = SwitchManager.create_resource(self.conf)
        Port_resource = PortManager.create_resource(self.conf)
        Link_resource = LinkManager.create_resource(self.conf)
        Route_resource = RouteManager.create_resource(self.conf)
        Path_resource = PathManager.create_resource(self.conf)       
        SADB_resource = SADBManager.create_resource(self.conf)
        NFVDB_resource = NFVDBManager.create_resource(self.conf)
        
        
        """ Kulcloud NFV Solution Manager """
        Topology_resource = TopologyManager.create_resource(self.conf)
        ServiceChain_resource = ServiceChainManager.create_resource(self.conf)        
        Service_resource = ServiceManager.create_resource(self.conf)
        NFVTopology_resource = NFVTopologyManager.create_resource(self.conf)
        NFVGroup_resource = NFVGroupManager.create_resource(self.conf)
        ServiceChainDefaultRule_resource = ServiceChainDefaultRuleManager.create_resource(self.conf)


        """ Fabric API """
        Fabric_collection = version_mapper.collection('fabric', 'fabric',
                controller=Fabric_resource, member_prefix="/",
                formatted=False)
        
        Tenant_collection = Fabric_collection.collection('tenant', 'tenant',
                controller=Tenant_resource, member_prefix="/{tenant_id}",
                formatted=False)
        
        Network_collection = Tenant_collection.member.collection('network', 'network',
                controller=Network_resource, member_prefix="/{network_id}",
                formatted=False)
        
        Host_collection = Network_collection.member.collection('host', 'host',
                controller=Host_resource, member_prefix="/{host_id}",
                formatted=False)
        
        
        
        
        """ Flow Table API """
        FlowTable_collection = version_mapper.collection('flowtable', 'flowtable',
                controller=Flowtable_resource, member_prefix="/{dpid}",
                formatted=False)
                
        Flow_collection = FlowTable_collection.member.collection('flow', 'flow',
                controller=Flow_resource, member_prefix="/{flow_id}",
                formatted=False)
        
        """ Stat API """
        Stats_collection = version_mapper.collection('stats/switch', 'stats/switch',
                controller=Stats_resource, member_prefix="/{dpid}",
                formatted=False)
        Stats_flow_collection = Stats_collection.member.collection('flow', 'flow',
                controller=Stats_flow_resource, member_prefix="/{flow_id}",
                formatted=False)
        
        Stats_port_collection = Stats_collection.connect('/port/{port_no}',
                controller=Stats_flow_resource, 
                action="show_stats_port",
                conditions={'method' : ["GET"]})   
        
        """ Topology API """
        Topology_collection = version_mapper.collection('topology', 'topology',
                controller=Topology_resource, member_prefix="/",
                formatted=False)
        
        Switch_collection = Topology_collection.collection('switch', 'switch',
                controller=Switch_resource, member_prefix="/{dpid}",
                formatted=False)
        
        Port_collection = Switch_collection.member.collection('port', 'port',
                controller=Port_resource, member_prefix="/{port_id}",
                formatted=False)
        
        Link_collection = Topology_collection.collection('link', 'link',
                controller=Link_resource, member_prefix="/{dpid}",
                formatted=False)
        
        
        """ Route API """
        Route_collection = version_mapper.collection('route', 'route',
                controller=Route_resource, member_prefix="/", formatted=False)
        
        Path_collection = Route_collection.collection('path', 'path',
                controller=Path_resource, member_prefix="/", formatted=False)

    	Path_collection.connect("/{src_dpid}/{src_port}/{dst_dpid}/{dst_port}",
							controller=Path_resource,
							action="show_route_path",
							conditions={'method' : ["GET"]})  
    
        """ Service Chaining API """
        ServiceChain_collection = version_mapper.collection('servicech', 'servicech',
                controller=ServiceChain_resource, member_prefix="/{phone_num}",
                formatted=False) 
        
        """ Service API """
        Service_collection = ServiceChain_collection.member.collection('services', 'services',
                controller=Service_resource, member_prefix="/{service_type}",
                formatted=False)   
        
        """ SA-DB API """
        SADB_collection = version_mapper.collection('SADB', 'SADB',
                controller=SADB_resource, member_prefix="/{service_type}", formatted=False)       
        
        """ NFV-DB API """
        NFVDB_collection = version_mapper.collection('NFVDB', 'NFVDB',
                controller=NFVDB_resource, member_prefix="/{name}", formatted=False)  

        version_mapper.connect("/NFVDB/mdn/{mdn}",
                            controller=NFVDB_resource,
                            action="get_nfvdb_bymdn",
                            conditions={'method' : ["GET"]})          
        
        version_mapper.connect("/NFVDB/group/all",
                            controller=NFVDB_resource,
                            action="get_nfvdb_vm",
                            conditions={'method' : ["GET"]})

        version_mapper.connect("/NFVDB/vm",
                            controller=NFVDB_resource,
                            action="create_nfv_vm_db",
                            conditions={'method' : ["POST"]})          

        version_mapper.connect("/servicech/rule/{service_chain_id}",
                            controller=ServiceChain_resource,
                            action="delete_service_chain_list",
                            conditions={'method' : ["DELETE"]})          

        version_mapper.connect("/servicech/rule/{service_chain_id}",
                            controller=ServiceChain_resource,
                            action="show_service_chain_list",
                            conditions={'method' : ["GET"]})          
        
        version_mapper.connect("/servicech/{phone_num}/services/{service_type}",
                            controller=Service_resource,
                            action="create_user_service",
                            conditions={'method' : ["POST"]})          

        version_mapper.connect("/servicech/stats/{service_chain_id}",
                            controller=ServiceChain_resource,
                            action="show_stats_by_servicechain",
                            conditions={'method' : ["GET"]})          

        version_mapper.connect("/SWDB",
                            controller=Service_resource,
                            action="show_switch_list",
                            conditions={'method' : ["GET"]})          

        version_mapper.connect("/SWDB/stats/{dpid}",
                            controller=Service_resource,
                            action="show_switch_statistic",
                            conditions={'method' : ["GET"]})

        version_mapper.connect("/NFVDB/stats/{nfv_name}",
                            controller=NFVDB_resource,
                            action="get_nfv_vm_statistic",
                            conditions={'method' : ["GET"]})

        version_mapper.connect("/NFVDB/stats/group/{nfv_groupname}",
                            controller=NFVDB_resource,
                            action="get_nfv_group_statistic",
                            conditions={'method' : ["GET"]})

        version_mapper.connect("/NFVDB/LB/{nfv_groupname}",
                            controller=NFVDB_resource,
                            action="update_nfv_vm_threshold_db",
                            conditions={'method' : ["POST"]})

        version_mapper.connect("/NFVDB/LB/stats/{nfvid}",
                            controller=NFVDB_resource,
                            action="get_nfv_vm_threshold",
                            conditions={'method' : ["GET"]})

        version_mapper.connect("/NFVDB/stats/{dpid}/{port_num}",
                            controller=NFVDB_resource,
                            action="get_stat_port",
                            conditions={'method':["GET"]})

        """Default Rule Create"""
        version_mapper.connect("/servicech/default/rule",
                            controller=ServiceChain_resource,
                            action="create_default_rule",
                            conditions={'method' : ["POST"]})

        version_mapper.connect("/servicech/default/rule",
                            controller=ServiceChain_resource,
                            action="get_default_rule",
                            conditions={'method' : ["GET"]})


        version_mapper.connect("/servicech/log",
                            controller=Service_resource,
                            action="create_service_by_chain_log",
                            conditions={"method" : ["POST"]})

        version_mapper.connect("/servicech/log/{dpid}/{port}/{ip}",
                            controller=Service_resource,
                            action="delete_service_by_chain_log",
                            conditions={"method" : ["DELETE"]})

        version_mapper.connect("/servicech/legacy",
                            controller=Service_resource,
                            action="create_legacy_service",
                            conditions={"method" : ["POST"]})

        version_mapper.connect("/servicech/sdn",
                            controller=Service_resource,
                            action="change_sdn_mode",
                            conditions={"method" : ["POST"]})
        
        version_mapper.connect("/servicech/sdn/mode",
                            controller=Service_resource,
                            action="get_current_sdn_mode",
                            conditions={"method" : ["GET"]})

        version_mapper.connect("/servicech/legacy/chain",
                            controller=Service_resource,
                            action="create_service_wrapper",
                            conditions={"method" : ["POST"]})

        version_mapper.connect("/SADB/test/vm_map",
                            controller=SADB_resource,
                            action="get_vm_map",
                            conditions={"method" : ["GET"]})

        version_mapper.connect("/SADB/test/vm_threshold",
                            controller=SADB_resource,
                            action="get_vm_threshold",
                            conditions={"method" : ["GET"]})
        
        
        
        # TODO : Define NFVTopologyManager API URI 

        super(API, self).__init__(mapper)
