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
#from kulcloud.core.v1.data.schema_service import Service as Service_schema

LOG = logging.getLogger(__name__)


class Controller(object):
    def __init__(self, conf):
        LOG.debug("[Service api] Creating Service Chain Manager controller with config:"
                                                "loadkulclouds.py %s", conf)
        self.conf = conf
        #self.create_schema = Service_schema()

    @utils.verify_version
    def index(self, req, version, phone_num):
        LOG.debug("[Service api] Show list of switches. Request: %s", req)
        result = core_api.service_get_index(self.conf, version, phone_num)
        return result

    @utils.http_success_code(202)
    @utils.verify_version_argument
    def create(self, req, version, phone_num, service_type, body):
        LOG.debug("[Service api] Got create request. Request: %s", req)
        #here we need to decide which device should be used
        #params = self.create_schema.deserialize(body)
        LOG.debug("Headers: %s", req.headers)
        # We need to create LB object and return its id
        #result = core_api.create_service(self.conf, version, phone_num, params)
        result = core_api.create_service(self.conf, version, phone_num, service_type, body)
        return result

    @utils.http_success_code(204)
    @utils.verify_version
    def delete(self, req, version, phone_num, service_type):
        pdb.set_trace()
        LOG.debug("[Service api] Got delete request. Request: %s", req)
        result=core_api.delete_service(self.conf, version, phone_num, service_type)
        return result

    @utils.verify_version
    def show(self, req, version, phone_num, service_type):
        LOG.debug("[Service api] Got info request. Request: %s", req)
	try:
        	result = core_api.service_get_data(self.conf, version, phone_num, service_type)
	except Exception as e:
		raise webob.exc.HTTPBadRequest(content_type='application_json',body='There is no target switch')
        return result

    @utils.verify_version
    def details(self, req, version, phone_num, service_type):
        LOG.debug("[Service api] Got info request. Request: %s", req)
        result = core_api.service_show_details(self.conf, version, phone_num, service_type)
        return result

    @utils.http_success_code(202)
    @utils.verify_version_argument
    def update(self, req, version, phone_num, service_type, body):
        LOG.debug("[Service api] Got update request. Request: %s", req)
        params = self.create_schema.deserialize(body)
        result = core_api.update_service(self.conf, version, phone_num, service_type, params)
        return result

    def create_user_service(self, req, version, phone_num, service_type, body):
        LOG.debug("[Service api] Got create request. Request: %s", req)
        result = core_api.create_service(self.conf, version, phone_num, service_type, body)
        return result

    def create_service_by_chain_log(self, req, version, body):
        LOG.debug("[Service api] Got create request. Request: %s", req)
        result = core_api.create_service_by_chain_log(self.conf, version, body)
        return result

    def delete_service_by_chain_log(self, req, version, dpid, port, ip):
        LOG.debug("[Service api] Got delete request. Request: %s", req)
        result = core_api.delete_service_by_chain_log(self.conf, version, dpid, port, ip)
        return result

    def create_legacy_service(self, req, version, body):
        LOG.debug("[Service api] Got Create request. Request: %s", req)
        result = core_api.create_legacy_service(self.conf, version, body)
        return result

    def create_service_wrapper(self, req, version, body):
        LOG.debug("[Service api] Got Create request. Request: %s", req)
        result = core_api.create_service_wrapper(self.conf, version, body)
        return result

    def change_sdn_mode(self, req, version):
        LOG.debug("[Service api] Got Create request. Request: %s", req)
        result = core_api.change_sdn_mode(self.conf, version)
        return result

    def get_current_sdn_mode(self, req, version):
        LOG.debug("[Service api] Get show sdn mode request. Request: %s", req)
        result = core_api.get_current_sdn_mode(self.conf, version)
        return result

    def show_switch_list(self, req, version):
        LOG.debug("[Service api] Got show switch request. Request: %s", req)
        result = core_api.show_switch_list(self.conf, version)
        return result

    def show_switch_statistic(self, req, version, dpid):
        LOG.debug("[Service api] Got show switch stats request. Request: %s", req)
        result = core_api.show_switch_statistic(self.conf, version, dpid)
        return result

def create_resource(conf):
    """ServiceManager resource factory method"""
    deserializer = wsgi.JSONRequestDeserializer()
    serializer = wsgi.JSONResponseSerializer()
    return wsgi.Resource(Controller(conf), deserializer, serializer)
