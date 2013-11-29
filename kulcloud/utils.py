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
import pdb
import colander
import contextlib
import functools
import logging
import sys

import webob.exc
from kulcloud.core.v1.data.schema_flow import Flow as Flow_schema
from kulcloud.core.v1.data.schema_host import Host as Host_schema
from kulcloud.core.v1.data.schema_nfvtopology import NFVTopologyMgr as NFVTopologyMgr_schema
from kulcloud.core.v1.data.schema_servicech import ServiceChainMgr as ServiceChainMgr_schema
from kulcloud.core.v1.data.schema_service import ServiceMgr as ServiceMgr_schema
from kulcloud.core.v1.data.schema_nfvgroup import NFVGroupMgr as NFVGroupMgr_schema


LOG = logging.getLogger(__name__)

schema_pool = {}
schema_pool['FlowManager'] = Flow_schema()
schema_pool['HostManager'] = Host_schema()
schema_pool['NFVTopologyMgr'] = NFVTopologyMgr_schema()
schema_pool['ServiceChainMgr'] = ServiceChainMgr_schema()
schema_pool['ServiceMgr'] = ServiceMgr_schema()
schema_pool['NFVGroupMgr'] = NFVGroupMgr_schema()



def http_success_code(code):
    """Attaches response code to a method.

    This decorator associates a response code with a method.  Note
    that the function attributes are directly manipulated; the method
    is not wrapped.
    200 : OK
    201 : Created
    202 : Accepted
    203 : Non-Authoritative Information
    204 : No Content
    205 : Reset Content    
    """

    def decorator(func):
        func.wsgi_code = code
        return func
    return decorator


def verify_version(func):
    @functools.wraps(func)
    def __inner(self, req, version, *args, **kwargs):
        if hasattr(req, 'context') and version != req.context.version:
            LOG.info('Version is not supported.')
            raise webob.exc. HTTPUnauthorized
        return func(self, req, version, *args, **kwargs)
    return __inner

def verify_version_argument(func):
    @functools.wraps(func)
    def __inner(self, req, version, *args, **kwargs):
        if self.name in schema_pool.keys():
	    try:
		conv = schema_pool[self.name].deserialize(kwargs['body'])
	    except colander.Invalid, e:
		raise webob.exc.HTTPBadRequest(content_type='application/jon', body=str(e.asdict()))		
            kwargs['body'] = conv
        if hasattr(req, 'context') and version != req.context.version:
            LOG.info('Version is not supported.')
            raise webob.exc. HTTPUnauthorized
        return func(self, req, version, *args, **kwargs)
    return __inner


def require_admin(func):
    @functools.wraps(func)
    def __inner(self, req, *args, **kwargs):
        if hasattr(req, 'context') and not req.context.is_admin:
            LOG.info('User has no admin priviledges.')
            raise webob.exc.HTTPUnauthorized
        return func(self, req, *args, **kwargs)
    return __inner


@contextlib.contextmanager
def save_and_reraise_exception():
    """Save current exception, run some code and then re-raise.

    In some cases the exception context can be cleared, resulting in None
    being attempted to be reraised after an exception handler is run. This
    can happen when eventlet switches greenthreads or when running an
    exception handler, code raises and catches an exception. In both
    cases the exception context will be cleared.

    To work around this, we save the exception state, run handler code, and
    then re-raise the original exception. If another exception occurs, the
    saved exception is logged and the new exception is reraised.
    """
    type_, value, traceback = sys.exc_info()
    try:
        yield
    except Exception:
        LOG.error('Original exception being dropped',
                  exc_info=(type_, value, traceback))
        raise
    raise type_, value, traceback
