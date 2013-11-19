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
import colander
import webob.exc
import pdb

from openstack.common import wsgi

from kulcloud import utils
from kulcloud.core import api as core_api
from kulcloud.db import api as db_api
from kulcloud.core.v1.data.schema_servicech import ServiceChain as ServiceChain_schema

LOG = logging.getLogger(__name__)


class Controller(object):
    def __init__(self, conf):
        LOG.debug("[ServiceChain api] Creating Service Chain Manager controller with config:"
                                                "loadkulclouds.py %s", conf)
        self.conf = conf
        self.create_schema = ServiceChain_schema()

    @utils.verify_version
    def index(self, req, version):
        LOG.debug("[ServiceChain api] Show list of switches. Request: %s", req)
        result = core_api.servicech_get_index(self.conf, version)
        return result

    @utils.http_success_code(202)
#    @utils.verify_version_argument
    def create(self, req, version, body):
        LOG.debug("[ServiceChain api] Got create request. Request: %s", req)
        #here we need to decide which device should be used
        params = self.create_schema.deserialize(body)
        LOG.debug("Headers: %s", req.headers)
        # We need to create LB object and return its id
        result = core_api.create_servicech(self.conf, version, params)
        return result

    @utils.http_success_code(204)
    @utils.verify_version
    def delete(self, req, version, phone_num):
        LOG.debug("[ServiceChain api] Got delete request. Request: %s", req)
        result = core_api.delete_servicech(self.conf, version, phone_num)
        return result

    @utils.verify_version
    def show(self, req, version, phone_num):
        LOG.debug("[ServiceChain api] Got info request. Request: %s", req)
	try:
       	    result = core_api.servicech_get_data(self.conf, version, phone_num)
	except Exception as e:
	    raise webob.exc.HTTPBadRequest(content_type='application_json',body='There is no target switch')
        return result

    """
    @utils.verify_version
    def details(self, req, version, phone_num):
        LOG.debug("[ServiceChain api] Got info request. Request: %s", req)
        result = core_api.servicech_show_details(self.conf, version, phone_num)
        return result
    """

    @utils.http_success_code(202)
    @utils.verify_version_argument
    def update(self, req, version, phone_num, body):
        LOG.debug("[ServiceChain api] Got update request. Request: %s", req)
        params = self.create_schema.deserialize(body)
        result = core_api.update_servicech(self.conf, version, phone_num, params)
        return result
    
    
    def show_service_chain_list(self, req, version, service_chain_id):
        LOG.debug("[ServiceChain api] Show list of service chains. Request: %s", req)
        result = core_api.servicech_show_service_chain_list(self.conf, version, service_chain_id)
        return result
        
    def delete_service_chain_list(self, req, version, service_chain_id):
        LOG.debug("[ServiceChain api] DELETE list of service chain. Request: %s", req)
        result = core_api.delete_service(self.conf, version, service_chain_id)
        return result

    def show_stats_by_servicechain(self, req, version, service_chain_id):
        LOG.debug("[ServiceChain api] Show stats of service chains. Request: %s", req)
        result = core_api.servicech_show_statistic_service_chain(self.conf, version, service_chain_id)
        return result

    """Default rule function"""
    """Work by Backguyn"""
    def create_default_rule(self, req, version, body):
        LOG.debug("[ServiceChain Default rule api] Create Default rule. Request: %s", req)
        result = core_api.create_default_rule(self.conf, version, body)
        return result

    def get_default_rule(self, req, version):
        LOG.debug("[ServiceChain Default rule api] Get Default rule. Request: %s", req)
        result = core_api.get_default_rule(self.conf, version)
        return result

def create_resource(conf):
    """ServiceChManager resource factory method"""
    deserializer = wsgi.JSONRequestDeserializer()
    serializer = wsgi.JSONResponseSerializer()
    return wsgi.Resource(Controller(conf), deserializer, serializer)
