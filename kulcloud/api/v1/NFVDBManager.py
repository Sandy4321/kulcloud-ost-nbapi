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
#from kulcloud.core.v1.data.schema_nfvdb import NFVDB as NFVDB_schema

LOG = logging.getLogger(__name__)

class Controller(object):
    def __init__(self, conf):
        LOG.debug("[ServiceChain api] Creating Service Chain Manager controller with config:"
                                                "loadkulclouds.py %s", conf)
        self.conf = conf
        #self.count = 0
        #self.create_schema = NFVDB_schema()

    @utils.verify_version
    def index(self, req, version):
        LOG.debug("[ServiceChain api] Show list of switches. Request: %s", req)
        result = core_api.nfvdb_get_index(self.conf, version)
        return result

    @utils.http_success_code(202)
#    @utils.verify_version_argument
    def create(self, req, version, body):
        LOG.debug("[ServiceChain api] Got create request. Request: %s", req)
        #here we need to decide which device should be used
        #params = self.create_schema.deserialize(body)
        LOG.debug("Headers: %s", req.headers)
        # We need to create LB object and return its id
        #result = core_api.create_servicech(self.conf, version, params)
        result = core_api.create_nfvdb(self.conf, version, body)
        return result

    @utils.http_success_code(202)
    @utils.verify_version
    def delete(self, req, version, name):
        LOG.debug("[ServiceChain api] Got delete request. Request: %s", req)
        result=core_api.delete_nfvdb(self.conf, version, name)
        return result

    @utils.http_success_code(202)
    @utils.verify_version_argument
    def update(self, req, version, name, body):
        LOG.debug("[ServiceChain api] Got update request. Request: %s", req)
        params = self.create_schema.deserialize(body)
        result = core_api.update_nfvdb(self.conf, version, name, params)
        return result

    def create_nfv_vm_db(self, req, version, body):
        LOG.debug("[ServiceChain api] Create NFV VM DB. Request: %s", req)
        result = core_api.create_nfvvmdb(self.conf, version, body)
        return result

    def get_nfvdb_bymdn(self, req, version, mdn):
        LOG.debug("[ServiceChain api] Get NFVDB by MDN. Request: %s", req)
        result = core_api.nfvdb_get_index_bymdn(self.conf, version, mdn)
        return result

    def get_nfv_vm_statistic(self, req, version, nfv_name):
        #sec = time.time()
        LOG.debug("[ServiceChain api] Get NFV VM Statistic. Request: %s", req)
        result = core_api.get_nfvvmStatistic(self.conf, version, nfv_name)
        #print time.time() - sec
        #print self.count
        #self.count += 1
        return result

    def get_nfv_group_statistic(self, req, version, nfv_groupname):
        LOG.debug("[ServiceChain api] Get NFV Group Statistic. Request: %s", req)
        result = core_api.get_nfvGroupStatistic(self.conf, version, nfv_groupname)
        return result

    def update_nfv_vm_threshold_db(self, req, version, nfv_groupname, body):
        LOG.debug("[ServiceChain api] Update NFV VM THRESHOLD DB. Request: %s", req)
        result = core_api.update_nfvvmThresholddb(self.conf, version, nfv_groupname, body)
        return result

    def get_nfv_vm_threshold(self, req, version, nfvid):
        LOG.debug("[ServiceChain api] Get NFV Threshold. Request: %s", req)
        result = core_api.get_nfv_vm_threshold(self.conf, version, nfvid)
        return result
    
    def get_stat_port(self, req, version, dpid, port_num):
        result = core_api.get_stat_port(self.conf, version, dpid, port_num)
        return result

    def get_nfvdb_vm(self, req, version):
        LOG.debug("[ServiceChain api] Get NFVDB all. Request: %s", req)
        result = core_api.nfvdb_get_vm(self.conf, version)
        return result



def create_resource(conf):
    """ServiceChManager resource factory method"""
    deserializer = wsgi.JSONRequestDeserializer()
    serializer = wsgi.JSONResponseSerializer()
    return wsgi.Resource(Controller(conf), deserializer, serializer)
