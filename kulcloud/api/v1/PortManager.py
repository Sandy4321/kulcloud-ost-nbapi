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

from openstack.common import wsgi
import webob.exc

from kulcloud import utils
from kulcloud.core import api as core_api
from kulcloud.db import api as db_api

LOG = logging.getLogger(__name__)


class Controller(object):
    def __init__(self, conf):
        LOG.debug("[Topology api] Creating Port Manager controller with config:"
                                                "loadkulclouds.py %s", conf)
        self.conf = conf

    @utils.verify_version
    def index(self, req, version, dpid):
        LOG.debug("[Topology api] Got index request. Request: %s", req)
        result = core_api.port_get_index(self.conf, version, dpid)
        return result

    @utils.http_success_code(202)
    @utils.verify_version_argument
    def create(self, req, version, dpid, body):
        LOG.debug("[Topology api] Got create request. Request: %s", req)
        #here we need to decide which device should be used
        params = body.copy()
        LOG.debug("Headers: %s", req.headers)
        # We need to create LB object and return its id
        result = core_api.create_port(self.conf, version, dpid, params)
        return result

    @utils.http_success_code(204)
    @utils.verify_version
    def delete(self, req, version, dpid, port_id):
        LOG.debug("[Topology api] Got delete request. Request: %s", req)
        result = core_api.delete_port(self.conf, version, dpid, port_id)
        return result
    
    @utils.verify_version
    def show(self, req, version, dpid, port_id):
        LOG.debug("[Topology api] Got info request. Request: %s", req)
        try:
            result = core_api.port_get_data(self.conf, version, dpid, port_id)
        except Exception as e:
            raise webob.exc.HTTPBadRequest(content_type='application_json',body='There is no target switch')
        return result
    
    @utils.verify_version
    def details(self, req, version, dpid, port_id):
        LOG.debug("[Topology api] Got loadkulcloudr info request. Request: %s", req)
        result = core_api.port_show_details(self.conf, version, dpid, port_id)
        return result

    @utils.http_success_code(202)
    @utils.verify_version_argument
    def update(self, req, version, dpid, port_id, body):
        LOG.debug("[Topology api] Got update request. Request: %s", req)
        result = core_api.update_port(self.conf, version, dpid, port_id, body)
        return result


def create_resource(conf):
    """portManager resource factory method"""
    deserializer = wsgi.JSONRequestDeserializer()
    serializer = wsgi.JSONResponseSerializer()
    return wsgi.Resource(Controller(conf), deserializer, serializer)
