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
import time
import logging
import colander
import webob.exc


from openstack.common import wsgi

from kulcloud import utils
from kulcloud.core import api as core_api
from kulcloud.db import api as db_api
from kulcloud.core.v1.data.schema_nfvgroup import NFVGroupMgr as NFVGroup_schema

LOG = logging.getLogger(__name__)

class Controller(object):
    # TODO: NFVGroupMgr Controller define
    def __init__(self, conf):
        LOG.debug("[NFVGroup api] NFVGroup Manager controller with config:"
                                                "loadkulclouds.py %s", conf)
        self.conf = conf
        self.create_schema = NFVGroup_schema() 
        self.name = 'NFVGroupMgr'    
        
    @utils.verify_version
    def show(self, req, version, name):
        LOG.debug("[NFVGroup api] info request. Request: %s", req)
        result = core_api.show_nfvgroup(self.conf, version, name)
        return result

    @utils.verify_version
    def index(self, req, version):
        LOG.debug("[NFVGroup api] Show list of switches. Request: %s", req)
        result = core_api.index_nfvgroup(self.conf, version)
        return result

    @utils.http_success_code(202)
    @utils.verify_version_argument
    def create(self, req, version, body):
        LOG.debug("[NFVGroup api] Got create request. Request: %s", req)
        params = self.create_schema.deserialize(body)
        LOG.debug("Headers: %s", req.headers)
        # We need to create LB object and return its id
        #result = core_api.create_servicech(self.conf, version, params)
        result = core_api.create_nfvgroup(self.conf, version, body)
        return result

    @utils.http_success_code(202)
    @utils.verify_version
    def delete(self, req, version, name):
        LOG.debug("[NFVGroup api] Got delete request. Request: %s", req)
        result=core_api.delete_nfvgroup(self.conf, version, name)
        return result

    @utils.http_success_code(202)
    @utils.verify_version_argument
    def update(self, req, version, name, body):
        LOG.debug("[NFVGroup api] Got update request. Request: %s", req)
        params = self.create_schema.deserialize(body)
        result = core_api.update_nfvgroup(self.conf, version, name, params)
        return result
    
    def get_nfvgroup_sync(self, req, version):
        LOG.debug("[NFVGroup api] Makdi synchronization request. Request: %s", req)
        result = core_api.sync_nfvgroup(self.conf, version)
        return result    

def create_resource(conf):
    """NFVGroup Manager resource factory method"""
    deserializer = wsgi.JSONRequestDeserializer()
    serializer = wsgi.JSONResponseSerializer()
    return wsgi.Resource(Controller(conf), deserializer, serializer)
