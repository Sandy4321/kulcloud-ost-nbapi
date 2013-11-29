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

import unittest
import mock
import logging
import kulcloud.exception as exception
from openstack.common import wsgi
from kulcloud.api.v1 import FabricManager
from kulcloud.api.v1 import FlowManager
from kulcloud.api.v1 import FlowtableManager
from kulcloud.api.v1 import HostManager
from kulcloud.api.v1 import LinkManager
from kulcloud.api.v1 import NetworkManager
from kulcloud.api.v1 import PathManager
from kulcloud.api.v1 import PortManager
from kulcloud.api.v1 import SimplepathManager
from kulcloud.api.v1 import SwitchManager
from kulcloud.api.v1 import TenantManager
from kulcloud.api.v1 import TopologyManager
from kulcloud.api.v1 import router

LOG = logging.getLogger()
VERSION = '1.0'
NOT_SUPPORTED = "not supported yet"

"""
class TestFabricManagerController(unittest.TestCase):
    def setUp(self):
        super(TestFabricManagerController, self).setUp()
        self.conf = mock.Mock()
        self.controller = FabricManager.Controller(self.conf)
        self.req = mock.Mock(spec=['headers'])

    def code_assert(self, code, func):
        self.assertTrue(hasattr(func, "wsgi_code"),
                "has not redifined HTTP status code")
        self.assertTrue(func.wsgi_code == code,
                "incorrect HTTP status code")

    @mock.patch('kulcloud.core.api.Fabric_get_index', autospec=True)
    def test_index(self, mock_fabric_get_index):
        mock_fabric_get_index.return_value = 'foo'
        resp = self.controller.index(self.req, VERSION)
        self.assertTrue(mock_fabric_get_index.called)
        mock_fabric_get_index.assert_called_once_with(self.conf, 'fake_tenant')
        self.assertEqual(resp, {'loadkulclouds': 'foo'})

    @mock.patch('kulcloud.core.api.create_lb', autospec=True)
    def test_create(self, mock_create_lb):
        mock_create_lb.return_value = '1'
        resp = self.controller.create(self.req, 'fake_tenant', {})
        self.assertTrue(mock_create_lb.called)
        mock_create_lb.assert_called_once_with(
                    self.conf,
                    {'tenant_id': 'fake_tenant'})
        self.assertEqual(resp, {'loadkulcloud': {'id': '1'}})
        self.code_assert(202, self.controller.create)

    @mock.patch('kulcloud.core.api.delete_lb', autospec=True)
    def test_delete(self, mock_delete_lb):
        resp = self.controller.delete(self.req, 'fake_tenant', 1)
        self.assertTrue(mock_delete_lb.called)
        self.code_assert(204, self.controller.delete)
        mock_delete_lb.assert_called_once_with(self.conf, 'fake_tenant', 1)
        self.assertEqual(resp, None)

    @mock.patch('kulcloud.core.api.lb_get_data', autospec=True)
    def test_show(self, mock_lb_get_data):
        mock_lb_get_data.return_value = 'foo'
        resp = self.controller.show(self.req, 'fake_tenant', 1)
        self.assertTrue(mock_lb_get_data.called)
        mock_lb_get_data.assert_called_once_with(self.conf, 'fake_tenant', 1)
        self.assertEqual(resp, {'loadkulcloud': 'foo'})

    @mock.patch('kulcloud.core.api.lb_show_details', autospec=True)
    def test_details(self, mock_lb_show_details):
        mock_lb_show_details.return_value = 'foo'
        resp = self.controller.details(self.req, 'fake_tenant', 1)
        self.assertTrue(mock_lb_show_details.called)
        mock_lb_show_details.assert_called_once_with(self.conf,
                'fake_tenant', 1)
        self.assertEqual('foo', resp)

    @mock.patch('kulcloud.core.api.update_lb', autospec=True)
    def test_update(self, mock_update_lb):
        resp = self.controller.update(self.req, 'fake_tenant', 1, {})
        self.assertTrue(mock_update_lb.called)
        self.code_assert(202, self.controller.update)
        mock_update_lb.assert_called_once_with(self.conf, 'fake_tenant', 1, {})
        self.assertEquals(resp, {"loadkulcloud": {"id": 1}})
"""

class TestFlowManagerController(unittest.TestCase):
    def setUp(self):
        super(TestFlowManagerController, self).setUp()
        self.conf = mock.Mock()
        self.controller = FlowManager.Controller(self.conf)
        self.req = mock.Mock(spec=['headers'])

    def code_assert(self, code, func):
        self.assertTrue(hasattr(func, "wsgi_code"),
                "has not redifined HTTP status code")
        self.assertTrue(func.wsgi_code == code,
                "incorrect HTTP status code")

    @mock.patch('kulcloud.core.api.create_flow', autospec=True)
    def test_create(self, mock_create_flow):
        msg = {'flow_id' : 1} 
        mock_create_flow.return_value = msg 
        body = {'nodes': 'foo'}
        resp = self.controller.create(self.req, VERSION, 1, body)
        self.assertTrue(mock_create_flow.called)
        mock_create_flow.assert_called_once_with(self.conf,
                VERSION, 1, body)
        self.assertEqual(resp, msg)

    @mock.patch('kulcloud.core.api.flow_get_index', autospec=True)
    def test_index(self, mock_flow_get_index):
        flow_list = []
        action_list = []
        action = {'action':'x','value':'x'}
        flow = {'flow_id':'x','priority':'x','in_port':'x','src_mac':'x',
            'dst_mac':'x','src_nw':'x','dst_nw':'x','vlan_id':'x',
            'src_port':'x','dst_port':'x','actions':[]}
        flow['actions'].append(action)
        flow_list.append(flow)
        msg = {'flows':flow_list}
        
        mock_flow_get_index.return_value = msg
        resp = self.controller.index(self.req, VERSION, 1)
        self.assertTrue(mock_flow_get_index.called)
        mock_flow_get_index.assert_called_once_with(self.conf, 
                                                    VERSION, 1)
        self.assertEqual(resp, msg)

    @mock.patch("kulcloud.core.api.flow_get_data", autospec=True)
    def test_show(self, mock_flow_get_data):       
        msg = {'flow_id':'x','priority':'x','in_port':'x','src_mac':'x',
            'dst_mac':'x','src_nw':'x','dst_nw':'x','vlan_id':'x',
            'src_port':'x','dst_port':'x','actions':[]}
        mock_flow_get_data.return_value = msg
        resp = self.controller.show(self.req, VERSION, 1, 1)
        self.assertTrue(mock_flow_get_data.called)
        mock_flow_get_data.assert_called_once_with(self.conf, 
                                                    VERSION, 1,1)
        self.assertEqual(resp, msg)

    @mock.patch('kulcloud.core.api.delete_flow', autospec=True)
    def test_delete(self, mock_delete_flow):
        msg = {'flow_id' : 1} 
        mock_delete_flow.return_value = msg
        resp = self.controller.delete(self.req, VERSION, 1, 1)
        self.assertTrue(mock_delete_flow.called)
        mock_delete_flow.assert_called_once_with(self.conf,
                VERSION, 1, 1)
        self.assertEqual(resp, msg)
        self.code_assert(204, self.controller.delete)

    @mock.patch('kulcloud.core.api.update_flow', autospec=True)
    def test_update(self, mock_update_flow):
        msg = {'nodeID': '1'}
        body = {'flow_id':'x','priority':'x','in_port':'x','src_mac':'x',
            'dst_mac':'x','src_nw':'x','dst_nw':'x','vlan_id':'x',
            'src_port':'x','dst_port':'x','actions':[]}        
        mock_update_flow.return_value = msg
        resp = self.controller.update(self.req, VERSION, 1, 1, body )
        self.assertTrue(mock_update_flow.called)
        mock_update_flow.assert_called_once_with(self.conf,
                VERSION, 1, 1, body)
        self.assertEqual(resp, msg)

class TestFlowtableManagerController(unittest.TestCase):
    def setUp(self):
        super(TestFlowtableManagerController, self).setUp()
        self.conf = mock.Mock()
        self.controller = FlowtableManager.Controller(self.conf)
        self.req = mock.Mock(spec=['headers'])

    def code_assert(self, code, func):
        self.assertTrue(hasattr(func, "wsgi_code"),
                "has not redifined HTTP status code")
        self.assertTrue(func.wsgi_code == code,
                "incorrect HTTP status code")

    @mock.patch('kulcloud.core.api.create_flowtable', autospec=True)
    def test_create(self, mock_create_flowtable):
        msg = {'message' : NOT_SUPPORTED} 
        mock_create_flowtable.return_value = msg 
        body = {'nodes': 'foo'}
        resp = self.controller.create(self.req, VERSION, body)
        self.assertTrue(mock_create_flowtable.called)
        mock_create_flowtable.assert_called_once_with(self.conf,
                VERSION, body)
        self.assertEqual(resp, msg)

    @mock.patch('kulcloud.core.api.flowtable_get_index', autospec=True)
    def test_index(self, mock_flowtable_get_index):
        msg = {'message' : NOT_SUPPORTED}         
        mock_flowtable_get_index.return_value = msg
        resp = self.controller.index(self.req, VERSION)
        self.assertTrue(mock_flowtable_get_index.called)
        mock_flowtable_get_index.assert_called_once_with(self.conf, 
                                                    VERSION)
        self.assertEqual(resp, msg)

    @mock.patch("kulcloud.core.api.flowtable_get_data", autospec=True)
    def test_show(self, mock_flowtable_get_data):       
        msg = {'message' : NOT_SUPPORTED}
        mock_flowtable_get_data.return_value = msg
        resp = self.controller.show(self.req, VERSION, 1)
        self.assertTrue(mock_flowtable_get_data.called)
        mock_flowtable_get_data.assert_called_once_with(self.conf, 
                                                    VERSION, 1)
        self.assertEqual(resp, msg)

    @mock.patch('kulcloud.core.api.delete_flowtable', autospec=True)
    def test_delete(self, mock_delete_flowtable):
        msg = {'message' : NOT_SUPPORTED} 
        mock_delete_flowtable.return_value = msg
        resp = self.controller.delete(self.req, VERSION, 1)
        self.assertTrue(mock_delete_flowtable.called)
        mock_delete_flowtable.assert_called_once_with(self.conf,
                VERSION, 1)
        self.assertEqual(resp, msg)
        self.code_assert(204, self.controller.delete)

    @mock.patch('kulcloud.core.api.update_flowtable', autospec=True)
    def test_update(self, mock_update_flowtable):
        msg = {'message' : NOT_SUPPORTED} 
        body = {'flow_id':'x','priority':'x','in_port':'x','src_mac':'x',
            'dst_mac':'x','src_nw':'x','dst_nw':'x','vlan_id':'x',
            'src_port':'x','dst_port':'x','actions':[]}        
        mock_update_flowtable.return_value = msg
        resp = self.controller.update(self.req, VERSION, 1, body )
        self.assertTrue(mock_update_flowtable.called)
        mock_update_flowtable.assert_called_once_with(self.conf,
                VERSION, 1, body)
        self.assertEqual(resp, msg)
   
class TestHostManagerController(unittest.TestCase):
    def setUp(self):
        super(TestHostManagerController, self).setUp()
        self.conf = mock.Mock()
        self.controller = HostManager.Controller(self.conf)
        self.req = mock.Mock(spec=['headers'])

    def code_assert(self, code, func):
        self.assertTrue(hasattr(func, "wsgi_code"),
                "has not redifined HTTP status code")
        self.assertTrue(func.wsgi_code == code,
                "incorrect HTTP status code")

    @mock.patch('kulcloud.core.api.create_host', autospec=True)
    def test_create(self, mock_create_host):
        msg = {'host_id' : 1} 
        mock_create_host.return_value = msg 
        body = {'nodes': 'foo'}
        resp = self.controller.create(self.req, VERSION, 1, 1, body)
        self.assertTrue(mock_create_host.called)
        mock_create_host.assert_called_once_with(self.conf,
                VERSION, 1, 1, body)
        self.assertEqual(resp, msg)

    @mock.patch('kulcloud.core.api.host_get_index', autospec=True)
    def test_index(self, mock_host_get_index):
        host_list = []
        host = {}
        host['host_id'] = 1
        host['dpid'] = 1
        host['port'] = 1
        host['host_ip'] = 1
        host['host_mac'] = 1
        host_list.append(host) 
        msg = {'hosts':host_list}
        
        mock_host_get_index.return_value = msg
        resp = self.controller.index(self.req, VERSION, 1, 1)
        self.assertTrue(mock_host_get_index.called)
        mock_host_get_index.assert_called_once_with(self.conf, 
                                                    VERSION, 1, 1)
        self.assertEqual(resp, msg)

    @mock.patch("kulcloud.core.api.host_get_data", autospec=True)
    def test_show(self, mock_host_get_data): 
             
        host = {}
        host['host_id'] = 1
        host['dpid'] = 1
        host['port'] = 1
        host['host_ip'] = 1
        host['host_mac'] = 1
        mock_host_get_data.return_value = host
        resp = self.controller.show(self.req, VERSION, 1, 1, 1)
        self.assertTrue(mock_host_get_data.called)
        mock_host_get_data.assert_called_once_with(self.conf, 
                                                    VERSION, 1, 1, 1)
        self.assertEqual(resp, host)

    @mock.patch('kulcloud.core.api.delete_host', autospec=True)
    def test_delete(self, mock_delete_host):
        msg = {'host_id' : 1} 
        mock_delete_host.return_value = msg
        resp = self.controller.delete(self.req, VERSION, 1, 1, 1)
        self.assertTrue(mock_delete_host.called)
        mock_delete_host.assert_called_once_with(self.conf,
                VERSION, 1, 1, 1)
        self.assertEqual(resp, msg)
        self.code_assert(204, self.controller.delete)

    @mock.patch('kulcloud.core.api.update_host', autospec=True)
    def test_update(self, mock_update_host):
        msg = {'host_id': '1'}
        body = {'flow_id':'x','priority':'x','in_port':'x','src_mac':'x',
            'dst_mac':'x','src_nw':'x','dst_nw':'x','vlan_id':'x',
            'src_port':'x','dst_port':'x','actions':[]}        
        mock_update_host.return_value = msg
        resp = self.controller.update(self.req, VERSION, 1, 1, 1, body )
        self.assertTrue(mock_update_host.called)
        mock_update_host.assert_called_once_with(self.conf,
                VERSION, 1, 1, 1, body)
        self.assertEqual(resp, msg)
   


class TestLinkManagerController(unittest.TestCase):
    def setUp(self):
        super(TestLinkManagerController, self).setUp()
        self.conf = mock.Mock()
        self.controller = LinkManager.Controller(self.conf)
        self.req = mock.Mock(spec=['headers'])

    def code_assert(self, code, func):
        self.assertTrue(hasattr(func, "wsgi_code"),
                "has not redifined HTTP status code")
        self.assertTrue(func.wsgi_code == code,
                "incorrect HTTP status code")

    @mock.patch('kulcloud.core.api.create_link', autospec=True)
    def test_create(self, mock_create_link):
        msg = {'message' : NOT_SUPPORTED} 
        mock_create_link.return_value = msg 
        body = {'nodes': 'foo'}
        resp = self.controller.create(self.req, VERSION, body)
        self.assertTrue(mock_create_link.called)
        mock_create_link.assert_called_once_with(self.conf,
                VERSION, body)
        self.assertEqual(resp, msg)

    @mock.patch('kulcloud.core.api.link_get_index', autospec=True)
    def test_index(self, mock_link_get_index):
        sw_list=[]
        sw={'dpid':'xxx'}
        link={'ports':[{'port_no':'x','neighbor':'neighbor_dpid',
                    'neighbor_port':'neighbor_port'}]}    
        sw['links']=link    
        sw_list.append(sw)
        msg = {'switches':sw_list}
        
        mock_link_get_index.return_value = msg
        resp = self.controller.index(self.req, VERSION)
        self.assertTrue(mock_link_get_index.called)
        mock_link_get_index.assert_called_once_with(self.conf, 
                                                    VERSION)
        self.assertEqual(resp, msg)

    @mock.patch("kulcloud.core.api.link_get_data", autospec=True)
    def test_show(self, mock_link_get_data):       
        sw={'dpid':'xxx'}
        link={'ports':[{'port_no':'x','neighbor':'neighbor_dpid',
                    'neighbor_port':'neighbor_port'}]}    
        sw['links']=link 
        mock_link_get_data.return_value = sw
        resp = self.controller.show(self.req, VERSION, 1)
        self.assertTrue(mock_link_get_data.called)
        mock_link_get_data.assert_called_once_with(self.conf, 
                                                    VERSION, 1)
        self.assertEqual(resp, sw)

    @mock.patch('kulcloud.core.api.delete_link', autospec=True)
    def test_delete(self, mock_delete_link):
        msg = {'message' : NOT_SUPPORTED} 
        mock_delete_link.return_value = msg
        resp = self.controller.delete(self.req, VERSION, 1)
        self.assertTrue(mock_delete_link.called)
        mock_delete_link.assert_called_once_with(self.conf,
                VERSION, 1)
        self.assertEqual(resp, msg)
        self.code_assert(204, self.controller.delete)

    @mock.patch('kulcloud.core.api.update_link', autospec=True)
    def test_update(self, mock_update_link):
        msg = {'message': NOT_SUPPORTED}
        body = {'flow_id':'x','priority':'x','in_port':'x','src_mac':'x',
            'dst_mac':'x','src_nw':'x','dst_nw':'x','vlan_id':'x',
            'src_port':'x','dst_port':'x','actions':[]}       
        mock_update_link.return_value = msg        
        resp = self.controller.update(self.req, VERSION, 1, body )
        self.assertTrue(mock_update_link.called)
        mock_update_link.assert_called_once_with(self.conf,
                VERSION, 1, body)
        self.assertEqual(resp, msg)
    


class TestNetworkManagerController(unittest.TestCase):
    def setUp(self):
        super(TestNetworkManagerController, self).setUp()
        self.conf = mock.Mock()
        self.controller = NetworkManager.Controller(self.conf)
        self.req = mock.Mock(spec=['headers'])

    def code_assert(self, code, func):
        self.assertTrue(hasattr(func, "wsgi_code"),
                "has not redifined HTTP status code")
        self.assertTrue(func.wsgi_code == code,
                "incorrect HTTP status code")

    @mock.patch('kulcloud.core.api.create_network', autospec=True)
    def test_create(self, mock_create_network):
        msg = {'flow_id' : 1} 
        mock_create_network.return_value = msg 
        body = {'nodes': 'foo'}
        resp = self.controller.create(self.req, VERSION, 1, body)
        self.assertTrue(mock_create_network.called)
        mock_create_network.assert_called_once_with(self.conf,
                VERSION, 1, body)
        self.assertEqual(resp, msg)

    @mock.patch('kulcloud.core.api.network_get_index', autospec=True)
    def test_index(self, mock_network_get_index):        
        msg = {'message':NOT_SUPPORTED}        
        mock_network_get_index.return_value = msg
        resp = self.controller.index(self.req, VERSION, 1)
        self.assertTrue(mock_network_get_index.called)
        mock_network_get_index.assert_called_once_with(self.conf, 
                                                    VERSION, 1)
        self.assertEqual(resp, msg)

    @mock.patch("kulcloud.core.api.network_get_data", autospec=True)
    def test_show(self, mock_network_get_data):       
        msg = {'message':NOT_SUPPORTED}   
        mock_network_get_data.return_value = msg
        resp = self.controller.show(self.req, VERSION, 1, 1)
        self.assertTrue(mock_network_get_data.called)
        mock_network_get_data.assert_called_once_with(self.conf, 
                                                    VERSION, 1,1)
        self.assertEqual(resp, msg)

    @mock.patch('kulcloud.core.api.delete_network', autospec=True)
    def test_delete(self, mock_delete_network):
        msg = {'message':NOT_SUPPORTED}    
        mock_delete_network.return_value = msg
        resp = self.controller.delete(self.req, VERSION, 1, 1)
        self.assertTrue(mock_delete_network.called)
        mock_delete_network.assert_called_once_with(self.conf,
                VERSION, 1, 1)
        self.assertEqual(resp, msg)
        self.code_assert(204, self.controller.delete)

    @mock.patch('kulcloud.core.api.update_network', autospec=True)
    def test_update(self, mock_update_network):
        msg = {'message':NOT_SUPPORTED}  
        body = {'nodes': 'foo'}        
        mock_update_network.return_value = msg
        resp = self.controller.update(self.req, VERSION, 1, 1, body )
        self.assertTrue(mock_update_network.called)
        mock_update_network.assert_called_once_with(self.conf,
                VERSION, 1, 1, body)
        self.assertEqual(resp, msg)
    

class TestPathManagerController(unittest.TestCase):
    def setUp(self):
        super(TestPathManagerController, self).setUp()
        self.conf = mock.Mock()
        self.controller = PathManager.Controller(self.conf)
        self.req = mock.Mock(spec=['headers'])

    def code_assert(self, code, func):
        self.assertTrue(hasattr(func, "wsgi_code"),
                "has not redifined HTTP status code")
        self.assertTrue(func.wsgi_code == code,
                "incorrect HTTP status code")

    @mock.patch('kulcloud.core.api.create_path', autospec=True)
    def test_create(self, mock_create_path):
        msg = {'message' : NOT_SUPPORTED} 
        mock_create_path.return_value = msg 
        body = {'nodes': 'foo'}
        resp = self.controller.create(self.req, VERSION, body)
        self.assertTrue(mock_create_path.called)
        mock_create_path.assert_called_once_with(self.conf,
                VERSION, body)
        self.assertEqual(resp, msg)

    @mock.patch('kulcloud.core.api.path_get_index', autospec=True)
    def test_index(self, mock_path_get_index):
        msg = {'message':NOT_SUPPORTED}        
        mock_path_get_index.return_value = msg
        resp = self.controller.index(self.req, VERSION)
        self.assertTrue(mock_path_get_index.called)
        mock_path_get_index.assert_called_once_with(self.conf, 
                                                    VERSION)
        self.assertEqual(resp, msg)

    @mock.patch("kulcloud.core.api.path_get_data", autospec=True)
    def test_show(self, mock_path_get_data):       
        msg = {'message':NOT_SUPPORTED} 
        mock_path_get_data.return_value = msg
        resp = self.controller.show(self.req, VERSION, 1)
        self.assertTrue(mock_path_get_data.called)
        mock_path_get_data.assert_called_once_with(self.conf, 
                                                    VERSION, 1)
        self.assertEqual(resp, msg)

    @mock.patch('kulcloud.core.api.delete_path', autospec=True)
    def test_delete(self, mock_delete_path):
        msg = {'message':NOT_SUPPORTED} 
        mock_delete_path.return_value = msg
        resp = self.controller.delete(self.req, VERSION, 1)
        self.assertTrue(mock_delete_path.called)
        mock_delete_path.assert_called_once_with(self.conf,
                VERSION, 1)
        self.assertEqual(resp, msg)
        self.code_assert(204, self.controller.delete)

    @mock.patch('kulcloud.core.api.update_path', autospec=True)
    def test_update(self, mock_update_path):
        msg = {'message':NOT_SUPPORTED} 
        body = {'flow_id':'x','priority':'x','in_port':'x','src_mac':'x',
            'dst_mac':'x','src_nw':'x','dst_nw':'x','vlan_id':'x',
            'src_port':'x','dst_port':'x','actions':[]}        
        mock_update_path.return_value = msg
        resp = self.controller.update(self.req, VERSION, 1, body )
        self.assertTrue(mock_update_path.called)
        mock_update_path.assert_called_once_with(self.conf,
                VERSION, 1, body)
        self.assertEqual(resp, msg)
   

class TestPortManagerController(unittest.TestCase):
    def setUp(self):
        super(TestPortManagerController, self).setUp()
        self.conf = mock.Mock()
        self.controller = PortManager.Controller(self.conf)
        self.req = mock.Mock(spec=['headers'])

    def code_assert(self, code, func):
        self.assertTrue(hasattr(func, "wsgi_code"),
                "has not redifined HTTP status code")
        self.assertTrue(func.wsgi_code == code,
                "incorrect HTTP status code")

    @mock.patch('kulcloud.core.api.create_port', autospec=True)
    def test_create(self, mock_create_port):
        msg = {'message':NOT_SUPPORTED} 
        mock_create_port.return_value = msg 
        body = {'nodes': 'foo'}
        resp = self.controller.create(self.req, VERSION, 1, body)
        self.assertTrue(mock_create_port.called)
        mock_create_port.assert_called_once_with(self.conf,
                VERSION, 1, body)
        self.assertEqual(resp, msg)

    @mock.patch('kulcloud.core.api.port_get_index', autospec=True)
    def test_index(self, mock_port_get_index):
        msg = {'message':NOT_SUPPORTED} 
        
        mock_port_get_index.return_value = msg
        resp = self.controller.index(self.req, VERSION, 1)
        self.assertTrue(mock_port_get_index.called)
        mock_port_get_index.assert_called_once_with(self.conf, 
                                                    VERSION, 1)
        self.assertEqual(resp, msg)

    @mock.patch("kulcloud.core.api.port_get_data", autospec=True)
    def test_show(self, mock_port_get_data):       
        msg = {'message':NOT_SUPPORTED} 
        mock_port_get_data.return_value = msg
        resp = self.controller.show(self.req, VERSION, 1, 1)
        self.assertTrue(mock_port_get_data.called)
        mock_port_get_data.assert_called_once_with(self.conf, 
                                                    VERSION, 1,1)
        self.assertEqual(resp, msg)

    @mock.patch('kulcloud.core.api.delete_port', autospec=True)
    def test_delete(self, mock_delete_port):
        msg = {'message':NOT_SUPPORTED} 
        mock_delete_port.return_value = msg
        resp = self.controller.delete(self.req, VERSION, 1, 1)
        self.assertTrue(mock_delete_port.called)
        mock_delete_port.assert_called_once_with(self.conf,
                VERSION, 1, 1)
        self.assertEqual(resp, msg)
        self.code_assert(204, self.controller.delete)

    @mock.patch('kulcloud.core.api.update_port', autospec=True)
    def test_update(self, mock_update_port):
        msg = {'message':NOT_SUPPORTED} 
        body = {'flow_id':'x','priority':'x','in_port':'x','src_mac':'x',
            'dst_mac':'x','src_nw':'x','dst_nw':'x','vlan_id':'x',
            'src_port':'x','dst_port':'x','actions':[]}        
        mock_update_port.return_value = msg
        resp = self.controller.update(self.req, VERSION, 1, 1, body )
        self.assertTrue(mock_update_port.called)
        mock_update_port.assert_called_once_with(self.conf,
                VERSION, 1, 1, body)
        self.assertEqual(resp, msg)
    
class TestSimplepathManagerController(unittest.TestCase):
    def setUp(self):
        super(TestSimplepathManagerController, self).setUp()
        self.conf = mock.Mock()
        self.controller = SimplepathManager.Controller(self.conf)
        self.req = mock.Mock(spec=['headers'])

    def code_assert(self, code, func):
        self.assertTrue(hasattr(func, "wsgi_code"),
                "has not redifined HTTP status code")
        self.assertTrue(func.wsgi_code == code,
                "incorrect HTTP status code")

    @mock.patch('kulcloud.core.api.create_simplepath', autospec=True)
    def test_create(self, mock_create_simplepath):
        msg = {'message' : NOT_SUPPORTED} 
        mock_create_simplepath.return_value = msg 
        body = {'nodes': 'foo'}
        resp = self.controller.create(self.req, VERSION, body)
        self.assertTrue(mock_create_simplepath.called)
        mock_create_simplepath.assert_called_once_with(self.conf,
                VERSION, body)
        self.assertEqual(resp, msg)

    @mock.patch('kulcloud.core.api.simplepath_get_index', autospec=True)
    def test_index(self, mock_simplepath_get_index):
        path_list = []
        path = {}
        hops = []
        hop_1 = {}
        hop_2 = {}
        
        path['path_id'] = 1
        hop_1['hop_count'] = 0
        hop_1['dpid'] = 1
        hop_1['outgress_port'] = 1
        hop_1['neighbor'] = 2
        hop_1['neighbor_port'] = 3
        
        hop_2['hop_count'] = 1
        hop_2['dpid'] = 2 
        hop_2['outgress_port'] = 3
        hop_2['neighbor'] = 3
        hop_2['neighbor_port'] = 4
        
        hops.append(hop_1)
        hops.append(hop_2)
        path['hops'] = hops
        path_list.append(path) 
        msg = {'paths':path_list}
        
        mock_simplepath_get_index.return_value = msg
        resp = self.controller.index(self.req, VERSION)
        self.assertTrue(mock_simplepath_get_index.called)
        mock_simplepath_get_index.assert_called_once_with(self.conf, 
                                                    VERSION)
        self.assertEqual(resp, msg)

    @mock.patch("kulcloud.core.api.simplepath_get_data", autospec=True)
    def test_show(self, mock_simplepath_get_data):       
        path = {}
        hops = []
        hop_1 = {}
        hop_2 = {}
        
        path['path_id'] = 1
        hop_1['hop_count'] = 0
        hop_1['dpid'] = 1
        hop_1['outgress_port'] = 1
        hop_1['neighbor'] = 2
        hop_1['neighbor_port'] = 3
        
        hop_2['hop_count'] = 1
        hop_2['dpid'] = 2 
        hop_2['outgress_port'] = 3
        hop_2['neighbor'] = 3
        hop_2['neighbor_port'] = 4
        
        hops.append(hop_1)
        hops.append(hop_2)
        path['hops'] = hops
        
        mock_simplepath_get_data.return_value = path
        resp = self.controller.show(self.req, VERSION, 1)
        self.assertTrue(mock_simplepath_get_data.called)
        mock_simplepath_get_data.assert_called_once_with(self.conf, 
                                                    VERSION, 1)
        self.assertEqual(resp, path)

    @mock.patch('kulcloud.core.api.delete_simplepath', autospec=True)
    def test_delete(self, mock_delete_simplepath):
        msg = {'message' : NOT_SUPPORTED} 
        mock_delete_simplepath.return_value = msg
        resp = self.controller.delete(self.req, VERSION, 1)
        self.assertTrue(mock_delete_simplepath.called)
        mock_delete_simplepath.assert_called_once_with(self.conf,
                VERSION, 1)
        self.assertEqual(resp, msg)
        self.code_assert(204, self.controller.delete)

    @mock.patch('kulcloud.core.api.update_simplepath', autospec=True)
    def test_update(self, mock_update_simplepath):
        msg = {'message' : NOT_SUPPORTED} 
        body = {'flow_id':'x','priority':'x','in_port':'x','src_mac':'x',
            'dst_mac':'x','src_nw':'x','dst_nw':'x','vlan_id':'x',
            'src_port':'x','dst_port':'x','actions':[]}        
        mock_update_simplepath.return_value = msg
        resp = self.controller.update(self.req, VERSION, 1, body )
        self.assertTrue(mock_update_simplepath.called)
        mock_update_simplepath.assert_called_once_with(self.conf,
                VERSION, 1, body)
        self.assertEqual(resp, msg)
   
        

class TestSwitchManagerController(unittest.TestCase):
    def setUp(self):
        super(TestSwitchManagerController, self).setUp()
        self.conf = mock.Mock()
        self.controller = SwitchManager.Controller(self.conf)
        self.req = mock.Mock(spec=['headers'])

    def code_assert(self, code, func):
        self.assertTrue(hasattr(func, "wsgi_code"),
                "has not redifined HTTP status code")
        self.assertTrue(func.wsgi_code == code,
                "incorrect HTTP status code")

    @mock.patch('kulcloud.core.api.create_switch', autospec=True)
    def test_create(self, mock_create_switch):               
        msg = {'message' : NOT_SUPPORTED} 
        mock_create_switch.return_value = msg 
        body = {'nodes': 'foo'}
        resp = self.controller.create(self.req, VERSION, body)
        self.assertTrue(mock_create_switch.called)
        mock_create_switch.assert_called_once_with(self.conf,
                VERSION, body)
        self.assertEqual(resp, msg)

    @mock.patch('kulcloud.core.api.switch_get_index', autospec=True)
    def test_index(self, mock_switch_get_index):
        sw_list=[]
        sw={'dpid':'xx:xx:xx:xx:xx:xx:xx:xx',
            'state':'registerd','peer':'127.0.0.1:6633','ports':'x'}
        sw_list.append(sw);        
        msg = {'switches' : sw_list} 
        
        mock_switch_get_index.return_value = msg
        resp = self.controller.index(self.req, VERSION)
        self.assertTrue(mock_switch_get_index.called)
        mock_switch_get_index.assert_called_once_with(self.conf, 
                                                    VERSION)
        self.assertEqual(resp, msg)

    @mock.patch("kulcloud.core.api.switch_get_data", autospec=True)
    def test_show(self, mock_switch_get_data):       
        msg = {'dpid':'xx:xx:xx:xx:xx:xx:xx:xx',
        'state':'registerd','peer':'127.0.0.1:6633','ports':'x'}
        mock_switch_get_data.return_value = msg
        resp = self.controller.show(self.req, VERSION, 1)
        self.assertTrue(mock_switch_get_data.called)
        mock_switch_get_data.assert_called_once_with(self.conf, 
                                                    VERSION, 1)
        self.assertEqual(resp, msg)

    @mock.patch('kulcloud.core.api.delete_switch', autospec=True)
    def test_delete(self, mock_delete_switch):
        msg = {'message' : NOT_SUPPORTED} 
        mock_delete_switch.return_value = msg
        resp = self.controller.delete(self.req, VERSION, 1)
        self.assertTrue(mock_delete_switch.called)
        mock_delete_switch.assert_called_once_with(self.conf,
                VERSION, 1)
        self.assertEqual(resp, msg)
        self.code_assert(204, self.controller.delete)

    @mock.patch('kulcloud.core.api.update_switch', autospec=True)
    def test_update(self, mock_update_switch):
        msg = {'message' : NOT_SUPPORTED} 
        body = {'flow_id':'x','priority':'x','in_port':'x','src_mac':'x',
            'dst_mac':'x','src_nw':'x','dst_nw':'x','vlan_id':'x',
            'src_port':'x','dst_port':'x','actions':[]}        
        mock_update_switch.return_value = msg
        resp = self.controller.update(self.req, VERSION, 1, body )
        self.assertTrue(mock_update_switch.called)
        mock_update_switch.assert_called_once_with(self.conf,
                VERSION, 1, body)
        self.assertEqual(resp, msg)
    

class TestTenantManagerController(unittest.TestCase):
    def setUp(self):
        super(TestTenantManagerController, self).setUp()
        self.conf = mock.Mock()
        self.controller = TenantManager.Controller(self.conf)
        self.req = mock.Mock(spec=['headers'])

    def code_assert(self, code, func):
        self.assertTrue(hasattr(func, "wsgi_code"),
                "has not redifined HTTP status code")
        self.assertTrue(func.wsgi_code == code,
                "incorrect HTTP status code")

    @mock.patch('kulcloud.core.api.create_tenant', autospec=True)
    def test_create(self, mock_create_tenant):
        msg = {'message' : NOT_SUPPORTED} 
        mock_create_tenant.return_value = msg 
        body = {'nodes': 'foo'}
        resp = self.controller.create(self.req, VERSION, body)
        self.assertTrue(mock_create_tenant.called)
        mock_create_tenant.assert_called_once_with(self.conf,
                VERSION, body)
        self.assertEqual(resp, msg)

    @mock.patch('kulcloud.core.api.tenant_get_index', autospec=True)
    def test_index(self, mock_tenant_get_index):
        msg = {'message' : NOT_SUPPORTED}         
        mock_tenant_get_index.return_value = msg
        resp = self.controller.index(self.req, VERSION)
        self.assertTrue(mock_tenant_get_index.called)
        mock_tenant_get_index.assert_called_once_with(self.conf, 
                                                    VERSION)
        self.assertEqual(resp, msg)

    @mock.patch("kulcloud.core.api.tenant_get_data", autospec=True)
    def test_show(self, mock_tenant_get_data):       
        msg = {'message' : NOT_SUPPORTED} 
        mock_tenant_get_data.return_value = msg
        resp = self.controller.show(self.req, VERSION, 1)
        self.assertTrue(mock_tenant_get_data.called)
        mock_tenant_get_data.assert_called_once_with(self.conf, 
                                                    VERSION, 1)
        self.assertEqual(resp, msg)

    @mock.patch('kulcloud.core.api.delete_tenant', autospec=True)
    def test_delete(self, mock_delete_tenant):
        msg = {'message' : NOT_SUPPORTED} 
        mock_delete_tenant.return_value = msg
        resp = self.controller.delete(self.req, VERSION, 1)
        self.assertTrue(mock_delete_tenant.called)
        mock_delete_tenant.assert_called_once_with(self.conf,
                VERSION, 1)
        self.assertEqual(resp, msg)
        self.code_assert(204, self.controller.delete)

    @mock.patch('kulcloud.core.api.update_tenant', autospec=True)
    def test_update(self, mock_update_tenant):
        msg = {'message' : NOT_SUPPORTED} 
        body = {'flow_id':'x','priority':'x','in_port':'x','src_mac':'x',
            'dst_mac':'x','src_nw':'x','dst_nw':'x','vlan_id':'x',
            'src_port':'x','dst_port':'x','actions':[]}        
        mock_update_tenant.return_value = msg
        resp = self.controller.update(self.req, VERSION, 1, body )
        self.assertTrue(mock_update_tenant.called)
        mock_update_tenant.assert_called_once_with(self.conf,
                VERSION, 1, body)
        self.assertEqual(resp, msg)
    
        
class TestTopologyManagerController(unittest.TestCase):
    def setUp(self):
        super(TestTopologyManagerController, self).setUp()
        self.conf = mock.Mock()
        self.controller = TopologyManager.Controller(self.conf)
        self.req = mock.Mock(spec=['headers'])

    def code_assert(self, code, func):
        self.assertTrue(hasattr(func, "wsgi_code"),
                "has not redifined HTTP status code")
        self.assertTrue(func.wsgi_code == code,
                "incorrect HTTP status code")

    @mock.patch('kulcloud.core.api.create_topology', autospec=True)
    def test_create(self, mock_create_topology):
        msg = {'message' : NOT_SUPPORTED} 
        mock_create_topology.return_value = msg 
        body = {'nodes': 'foo'}
        resp = self.controller.create(self.req, VERSION, body)
        self.assertTrue(mock_create_topology.called)
        mock_create_topology.assert_called_once_with(self.conf,
                VERSION, body)
        self.assertEqual(resp, msg)

    @mock.patch('kulcloud.core.api.topology_get_index', autospec=True)
    def test_index(self, mock_topology_get_index):
        msg = {'message' : NOT_SUPPORTED}         
        mock_topology_get_index.return_value = msg
        resp = self.controller.index(self.req, VERSION)
        self.assertTrue(mock_topology_get_index.called)
        mock_topology_get_index.assert_called_once_with(self.conf, 
                                                    VERSION)
        self.assertEqual(resp, msg)

    @mock.patch("kulcloud.core.api.topology_get_data", autospec=True)
    def test_show(self, mock_topology_get_data):       
        msg = {'message' : NOT_SUPPORTED} 
        mock_topology_get_data.return_value = msg
        resp = self.controller.show(self.req, VERSION, 1)
        self.assertTrue(mock_topology_get_data.called)
        mock_topology_get_data.assert_called_once_with(self.conf, 
                                                    VERSION, 1)
        self.assertEqual(resp, msg)

    @mock.patch('kulcloud.core.api.delete_topology', autospec=True)
    def test_delete(self, mock_delete_topology):
        msg = {'message' : NOT_SUPPORTED} 
        mock_delete_topology.return_value = msg
        resp = self.controller.delete(self.req, VERSION, 1)
        self.assertTrue(mock_delete_topology.called)
        mock_delete_topology.assert_called_once_with(self.conf,
                VERSION, 1)
        self.assertEqual(resp, msg)
        self.code_assert(204, self.controller.delete)

    @mock.patch('kulcloud.core.api.update_topology', autospec=True)
    def test_update(self, mock_update_topology):
        msg = {'message' : NOT_SUPPORTED} 
        body = {'flow_id':'x','priority':'x','in_port':'x','src_mac':'x',
            'dst_mac':'x','src_nw':'x','dst_nw':'x','vlan_id':'x',
            'src_port':'x','dst_port':'x','actions':[]}        
        mock_update_topology.return_value = msg
        resp = self.controller.update(self.req, VERSION, 1, body )
        self.assertTrue(mock_update_topology.called)
        mock_update_topology.assert_called_once_with(self.conf,
                VERSION, 1, body)
        self.assertEqual(resp, msg)        

class TestRouter(unittest.TestCase):
    def setUp(self):
        config = mock.MagicMock(spec=dict)
        self.obj = router.API(config)

    def test_mapper(self):
        list_of_methods = (
            # TOPOLOGY API
            ("/{version}/topology/switch", "GET",
                SwitchManager.Controller, "index"),
            ("/{version}/topology/switch/{dpid}", "GET",
                SwitchManager.Controller, "show"),
            ("/{version}/topology/switch/{dpid}/port", "GET",
                PortManager.Controller, "index"),
            ("/{version}/topology/switch/{dpid}/port/{port_id}", "GET",
                PortManager.Controller, "show"),
            ("/{version}/topology/link", "GET",
                LinkManager.Controller, "index"),            
            ("/{version}/topology/link/{link_id}", "GET",
                LinkManager.Controller, "show"),
            # Flow Talbe API
            ("/{version}/flowtable/{dpid}/flow", "GET",
                FlowManager.Controller, "index"),
            ("/{version}/flowtable/{dpid}/flow", "POST",
                FlowManager.Controller, "create"),
            ("/{version}/flowtable/{dpid}/flow/{flow_id}", "GET",
                FlowManager.Controller, "show"),
            ("/{version}/flowtable/{dpid}/flow/{flow_id}", "PUT",
                FlowManager.Controller, "update"),
            ("/{version}/flowtable/{dpid}/flow/{flow_id}", "DELETE",
                FlowManager.Controller, "delete"),
            # Path API
            ("/{version}/path/simplepath", "GET",
                SimplepathManager.Controller, "index"),
            ("/{version}/path/simplepath/{path_id}", "GET",
                SimplepathManager.Controller, "show"),            
            # Fabric API
            ("/{version}/fabric/tenant/{tenant_id}/network/{network_id}/host", "GET",
                HostManager.Controller, "index"),
            ("/{version}/fabric/tenant/{tenant_id}/network/{network_id}/host/{host_id}", "GET",
                HostManager.Controller, "show"),
            ("/{version}/fabric/tenant/{tenant_id}/network/{network_id}/host", "POST",
                HostManager.Controller, "create"),
            ("/{version}/fabric/tenant/{tenant_id}/network/{network_id}/host/{host_id}", "PUT",
                HostManager.Controller, "update"),
            ("/{version}/fabric/tenant/{tenant_id}/network/{network_id}/host/{host_id}", "DELETE",
                HostManager.Controller, "delete"),            
        )
        
        for url, method, controller, action in list_of_methods:
            LOG.info('Verifying %s to %s', method, url)
            m = self.obj.map.match(url, {"REQUEST_METHOD": method})
            self.assertTrue(m is not None, "Route not found for %s %s" % (
                    method, url))
            controller0 = m.pop('controller')
            action0 = m.pop('action')
            self.assertTrue(isinstance(controller0, wsgi.Resource),
                    "Controller for %s %s is not wshi.Resource instance." % (
                    method, url))
            self.assertTrue(isinstance(controller0.controller, controller),
                    "Inner controller for %s %s is not %s.%s instance." % (
                    method, url, controller.__module__, controller.__name__))
            self.assertEquals(action0, action)
            mok = mock.mocksignature(getattr(controller, action))
            if method == "POST" or method == "PUT":
                m['body'] = {}
            try:
                mok('SELF', 'REQUEST', **m)
            except TypeError:
                self.fail('Arguments in route "%s %s" does not match %s.%s.%s '
                          'signature: %s' % (method, url,
                    controller.__module__, controller.__name__, action, m))

