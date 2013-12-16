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

        """ Kulcloud Core Manager API"""
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
        
        """ Route API """
        Service_collection = version_mapper.collection('service', 'service',
                controller=Service_resource , member_prefix="/{name}", formatted=False)
        
        Nfvgroup_collection = version_mapper.collection('nfvgroup', 'nfvgroup',
                controller=NFVGroup_resource , member_prefix="/{name}", formatted=False)
        
        Servicechain_default_collection = version_mapper.collection('servicechdefault', 'servicechdefault',
                controller=Service_resource , member_prefix="/{name}", formatted=False)

        Servicechain_collection = version_mapper.collection('servicech', 'servicech',
                controller=Service_resource , member_prefix="/{dpid}/{name}/{ip}", formatted=False)
 
        Nfvtopology_collection = version_mapper.collection('nfvtopology', 'nfvtopology',
                controller=Service_resource , 
                member_prefix="/{name}", formatted=False)
 
         
        """ Synchronization API """
        version_mapper.connect("/servicech/sync",
                            controller=ServiceChain_resource,
                            action="get_servicechain_sync",
                            conditions={'method' : ["GET"]})     

        version_mapper.connect("/nfvtopology/sync",
                            controller=NFVTopology_resource,
                            action="get_nfvtopology_sync",
                            conditions={'method' : ["GET"]})
        
        version_mapper.connect("/nfvgroup/sync",
                            controller=NFVGroup_resource,
                            action="get_nfvgroup_sync",
                            conditions={'method' : ["GET"]})     

        version_mapper.connect("/service/sync",
                            controller=Service_resource,
                            action="get_service_sync",
                            conditions={'method' : ["GET"]})

        version_mapper.connect("/servicechdefault/sync",
                            controller=ServiceChainDefaultRule_resource,
                            action="get_servicechaindefaultrule_sync",
                            conditions={'method' : ["GET"]})   
        

        super(API, self).__init__(mapper)
