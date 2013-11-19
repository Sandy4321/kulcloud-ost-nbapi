# vim: tabstop=4 shiftwidth=4 softtabstop=4

# Copyright (c) 2011 X.commerce, a business unit of eBay Inc.
# Copyright 2010 United States Government as represented by the
# Administrator of the National Aeronautics and Space Administration.
# Copyright 2011 Piston Cloud Computing, Inc.
# All Rights Reserved.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.
"""Database storage API."""

import functools
import datetime

from kulcloud.db import models
from kulcloud.db.session import get_session
from kulcloud import exception
from kulcloud.core import lb_status


# XXX(akscram): pack_ and unpack_ are helper methods to compatibility
def pack_extra(model, values):
    obj_ref = model()
    pack_update(obj_ref, values)
    return obj_ref


def unpack_extra(obj_ref):
    obj_dict = dict(obj_ref.iteritems())
    obj_dict.update(obj_dict.pop('extra', None) or {})
    return obj_dict


def pack_update(obj_ref, values):
    obj_dict = values.copy()
    for k, v in values.iteritems():
        if k in obj_ref.keys():
            obj_ref[k] = obj_dict.pop(k)
    if obj_dict:
        if obj_ref['extra'] is not None:
            obj_ref['extra'].update(obj_dict)
        else:
            obj_ref['extra'] = obj_dict.copy()


device_pack_extra = functools.partial(pack_extra, models.Device)
loadbalancer_pack_extra = functools.partial(pack_extra, models.LoadBalancer)
serverfarm_pack_extra = functools.partial(pack_extra, models.ServerFarm)
virtualserver_pack_extra = functools.partial(pack_extra, models.VirtualServer)
server_pack_extra = functools.partial(pack_extra, models.Server)
probe_pack_extra = functools.partial(pack_extra, models.Probe)
sticky_pack_extra = functools.partial(pack_extra, models.Sticky)
predictor_pack_extra = functools.partial(pack_extra, models.Predictor)

# Device


def device_get(conf, device_id, session=None):
    session = session or get_session(conf)
    device_ref = session.query(models.Device).\
                         filter_by(id=device_id).first()
    if not device_ref:
        raise exception.DeviceNotFound(device_id=device_id)
    return device_ref


def device_get_all(conf):
    session = get_session(conf)
    query = session.query(models.Device)
    return query.all()


def device_create(conf, values):
    session = get_session(conf)
    with session.begin():
        device_ref = models.Device()
        device_ref.update(values)
        session.add(device_ref)
        return device_ref


def device_update(conf, device_id, values):
    session = get_session(conf)
    with session.begin():
        device_ref = device_get(conf, device_id, session=session)
        device_ref.update(values)
        return device_ref


def device_destroy(conf, device_id):
    session = get_session(conf)
    with session.begin():
        device_ref = device_get(conf, device_id, session=session)
        session.delete(device_ref)

# LoadBalancer


def loadbalancer_get(conf, loadbalancer_id, tenant_id=None, session=None):
    session = session or get_session(conf)
    query = session.query(models.LoadBalancer).filter_by(id=loadbalancer_id)
    if tenant_id:
        query = query.filter_by(tenant_id=tenant_id)
    loadbalancer_ref = query.first()
    if not loadbalancer_ref:
        raise exception.LoadBalancerNotFound(loadbalancer_id=loadbalancer_id)
    return loadbalancer_ref


def loadbalancer_get_all_by_project(conf, tenant_id):
    session = get_session(conf)
    query = session.query(models.LoadBalancer).filter_by(tenant_id=tenant_id)
    return query.all()


def loadbalancer_get_all_by_vm_id(conf, tenant_id, vm_id):
    session = get_session(conf)
    query = session.query(models.LoadBalancer).distinct().\
                    filter_by(tenant_id=tenant_id).\
                    filter(models.LoadBalancer.id ==
                           models.ServerFarm.lb_id).\
                    filter(models.Server.sf_id ==
                           models.ServerFarm.id).\
                    filter(models.Server.vm_id == vm_id)
    return query.all()


def loadbalancer_get_all_by_device_id(conf, device_id):
    session = get_session(conf)
    query = session.query(models.LoadBalancer).filter_by(device_id=device_id)
    lb_refs = query.all()
    if not lb_refs:
        raise exception.LoadBalancerNotFound('No loadbalancer '
                                             'for the device %s found'
                                             % device_id)
    return lb_refs


def loadbalancer_create(conf, values):
    session = get_session(conf)
    with session.begin():
        lb_ref = models.LoadBalancer()
        lb_ref.update(values)
        session.add(lb_ref)
        return lb_ref


def loadbalancer_update(conf, lb_id, values):
    session = get_session(conf)
    with session.begin():
        lb_ref = loadbalancer_get(conf, lb_id, session=session)
        lb_ref.update(values)
        lb_ref['updated_at'] = datetime.datetime.utcnow()
        return lb_ref


def loadbalancer_destroy(conf, lb_id):
    session = get_session(conf)
    with session.begin():
        lb_ref = loadbalancer_get(conf, lb_id, session=session)
        session.delete(lb_ref)


def lb_count_active_by_device(conf, device_id):
    session = get_session(conf)
    with session.begin():
        lbs_count = session.query(models.LoadBalancer).\
                                  filter_by(device_id=device_id).\
                                  filter_by(status=lb_status.ACTIVE).\
                                  count()
        return lbs_count


# Probe


def probe_get(conf, probe_id, tenant_id=None, session=None):
    session = session or get_session(conf)
    query = session.query(models.Probe).filter_by(id=probe_id)
    if tenant_id:
        query = query.filter(models.Probe.sf_id == models.ServerFarm.id).\
                  filter(models.LoadBalancer.id == models.ServerFarm.lb_id).\
                  filter(models.LoadBalancer.tenant_id == tenant_id)
    probe_ref = query.first()
    if not probe_ref:
        raise exception.ProbeNotFound(probe_id=probe_id)
    return probe_ref


def probe_get_all(conf):
    session = get_session(conf)
    query = session.query(models.Probe)
    return query.all()


def probe_get_all_by_sf_id(conf, sf_id):
    session = get_session(conf)
    query = session.query(models.Probe).filter_by(sf_id=sf_id)
    return query.all()


def probe_create(conf, values):
    session = get_session(conf)
    with session.begin():
        probe_ref = models.Probe()
        probe_ref.update(values)
        session.add(probe_ref)
        return probe_ref


def probe_update(conf, probe_id, values):
    session = get_session(conf)
    with session.begin():
        probe_ref = probe_get(conf, probe_id, session=session)
        probe_ref.update(values)
        return probe_ref


def probe_destroy(conf, probe_id):
    session = get_session(conf)
    with session.begin():
        probe_ref = probe_get(conf, probe_id, session=session)
        session.delete(probe_ref)


def probe_destroy_by_sf_id(conf, sf_id, session=None):
    session = session or get_session(conf)
    with session.begin():
        session.query(models.Probe).filter_by(sf_id=sf_id).delete()

# Sticky


def sticky_get(conf, sticky_id, tenant_id=None, session=None):
    session = session or get_session(conf)
    query = session.query(models.Sticky).filter_by(id=sticky_id)
    if tenant_id:
        query = query.filter(models.Sticky.sf_id == models.ServerFarm.id).\
                  filter(models.LoadBalancer.id == models.ServerFarm.lb_id).\
                  filter(models.LoadBalancer.tenant_id == tenant_id)
    sticky_ref = query.first()
    if not sticky_ref:
        raise exception.StickyNotFound(sticky_id=sticky_id)
    return sticky_ref


def sticky_get_all(conf):
    session = get_session(conf)
    query = session.query(models.Sticky)
    return query.all()


def sticky_get_all_by_sf_id(conf, sf_id):
    session = get_session(conf)
    query = session.query(models.Sticky).filter_by(sf_id=sf_id)
    return query.all()


def sticky_create(conf, values):
    session = get_session(conf)
    with session.begin():
        sticky_ref = models.Sticky()
        sticky_ref.update(values)
        session.add(sticky_ref)
        return sticky_ref


def sticky_update(conf, sticky_id, values):
    session = get_session(conf)
    with session.begin():
        sticky_ref = sticky_get(conf, sticky_id, session=session)
        sticky_ref.update(values)
        return sticky_ref


def sticky_destroy(conf, sticky_id):
    session = get_session(conf)
    with session.begin():
        sticky_ref = sticky_get(conf, sticky_id, session=session)
        session.delete(sticky_ref)


def sticky_destroy_by_sf_id(conf, sf_id, session=None):
    session = session or get_session(conf)
    with session.begin():
        session.query(models.Sticky).filter_by(sf_id=sf_id).delete()

# Server


def server_get(conf, server_id, lb_id=None, tenant_id=None, session=None):
    session = session or get_session(conf)
    query = session.query(models.Server).filter_by(id=server_id)
    if lb_id:
        query = query.filter(models.ServerFarm.lb_id == lb_id).\
                      filter(models.Server.sf_id == models.ServerFarm.id)
        if tenant_id:
            query = query.filter(models.LoadBalancer.id == lb_id).\
                          filter(models.LoadBalancer.tenant_id == tenant_id)
    elif tenant_id:
        query = query.filter(models.Server.sf_id == models.ServerFarm.id).\
                  filter(models.LoadBalancer.id == models.ServerFarm.lb_id).\
                  filter(models.LoadBalancer.tenant_id == tenant_id)
    server_ref = query.first()
    if not server_ref:
        raise exception.ServerNotFound(server_id=server_id)
    return server_ref


def server_get_all(conf):
    session = get_session(conf)
    query = session.query(models.Server)
    return query.all()


def server_get_by_address(conf, server_address):
    session = get_session(conf)
    server_ref = session.query(models.Server).\
                         filter_by(address=server_address).\
                         filter_by(deployed='True').first()
    if not server_ref:
        raise exception.ServerNotFound(server_address=server_address)
    return server_ref


def server_get_by_address_on_device(conf, server_address, device_id):
    session = get_session(conf)
    server_refs = session.query(models.Server).\
                         filter_by(address=server_address).\
                         filter_by(deployed='True')
    for server_ref in server_refs:
        sf = serverfarm_get(conf, server_ref['sf_id'], session=session)
        lb = loadbalancer_get(conf, sf['lb_id'])
        if device_id == lb['device_id']:
            return server_ref
    raise exception.ServerNotFound(server_address=server_address,
                                   device_id=device_id)


def server_get_all_by_parent_id(conf, parent_id):
    session = get_session(conf)
    query = session.query(models.Server).filter_by(parent_id=parent_id)
    return query.all()


def server_get_all_by_sf_id(conf, sf_id):
    session = get_session(conf)
    query = session.query(models.Server).filter_by(sf_id=sf_id)
    return query.all()


def server_create(conf, values):
    session = get_session(conf)
    with session.begin():
        server_ref = models.Server()
        server_ref.update(values)
        session.add(server_ref)
        return server_ref


def server_update(conf, server_id, values):
    session = get_session(conf)
    with session.begin():
        server_ref = server_get(conf, server_id, session=session)
        server_ref.update(values)
        return server_ref


def server_destroy(conf, server_id):
    session = get_session(conf)
    with session.begin():
        server_ref = server_get(conf, server_id, session=session)
        session.delete(server_ref)


def server_destroy_by_sf_id(conf, sf_id, session=None):
    session = session or get_session(conf)
    with session.begin():
        session.query(models.Server).filter_by(sf_id=sf_id).delete()

# ServerFarm


def serverfarm_get(conf, serverfarm_id, session=None):
    session = session or get_session(conf)
    serverfarm_ref = session.query(models.ServerFarm).\
                             filter_by(id=serverfarm_id).first()
    if not serverfarm_ref:
        raise exception.ServerFarmNotFound(serverfarm_id=serverfarm_id)
    return serverfarm_ref


def serverfarm_get_all_by_lb_id(conf, lb_id, tenant_id=None):
    session = get_session(conf)
    query = session.query(models.ServerFarm).filter_by(lb_id=lb_id)
    if tenant_id:
        query = query.filter(models.LoadBalancer.id == lb_id).\
                      filter(models.LoadBalancer.tenant_id == tenant_id)
    return query.all()


def serverfarm_create(conf, values):
    session = get_session(conf)
    with session.begin():
        serverfarm_ref = models.ServerFarm()
        serverfarm_ref.update(values)
        session.add(serverfarm_ref)
        return serverfarm_ref


def serverfarm_update(conf, serverfarm_id, values):
    session = get_session(conf)
    with session.begin():
        serverfarm_ref = serverfarm_get(conf, serverfarm_id, session=session)
        serverfarm_ref.update(values)
        return serverfarm_ref


def serverfarm_destroy(conf, serverfarm_id):
    session = get_session(conf)
    with session.begin():
        serverfarm_ref = serverfarm_get(conf, serverfarm_id, session=session)
        session.delete(serverfarm_ref)

# Predictor


def predictor_get(conf, predictor_id, session=None):
    session = session or get_session(conf)
    predictor_ref = session.query(models.Predictor).\
                            filter_by(id=predictor_id).first()
    if not predictor_ref:
        raise exception.PredictorNotFound(predictor_id=predictor_id)
    return predictor_ref


def predictor_get_by_sf_id(conf, sf_id):
    session = get_session(conf)
    predictor_ref = session.query(models.Predictor).\
                            filter_by(sf_id=sf_id).\
                            first()
    if not predictor_ref:
        raise exception.PredictorNotFound(sf_id=sf_id)
    return predictor_ref


def predictor_create(conf, values):
    session = get_session(conf)
    with session.begin():
        predictor_ref = models.Predictor()
        predictor_ref.update(values)
        session.add(predictor_ref)
        return predictor_ref


def predictor_update(conf, predictor_id, values):
    session = get_session(conf)
    with session.begin():
        predictor_ref = predictor_get(conf, predictor_id, session=session)
        predictor_ref.update(values)
        return predictor_ref


def predictor_destroy(conf, predictor_id):
    session = get_session(conf)
    with session.begin():
        predictor_ref = predictor_get(conf, predictor_id, session=session)
        session.delete(predictor_ref)


def predictor_destroy_by_sf_id(conf, sf_id, session=None):
    session = session or get_session(conf)
    with session.begin():
        session.query(models.Predictor).filter_by(sf_id=sf_id).delete()

# VirtualServer


def virtualserver_get(conf, vserver_id, tenant_id=None, session=None):
    session = session or get_session(conf)
    query = session.query(models.VirtualServer).filter_by(id=vserver_id)
    if tenant_id:
        query = query.\
                  filter(models.VirtualServer.sf_id == models.ServerFarm.id).\
                  filter(models.LoadBalancer.id == models.ServerFarm.lb_id).\
                  filter(models.LoadBalancer.tenant_id == tenant_id)
    vserver_ref = query.first()
    if not vserver_ref:
        raise exception.VirtualServerNotFound(virtualserver_id=vserver_id)
    return vserver_ref


def virtualserver_get_all_by_sf_id(conf, sf_id):
    session = get_session(conf)
    query = session.query(models.VirtualServer).filter_by(sf_id=sf_id)
    return query.all()


def virtualserver_get_all_by_lb_id(conf, lb_id, tenant_id=None):
    session = get_session(conf)
    query = session.query(models.VirtualServer).\
                  filter(models.ServerFarm.lb_id == lb_id).\
                  filter_by(sf_id=models.ServerFarm.id)
    if tenant_id:
        query = query.\
                  filter(models.LoadBalancer.id == models.ServerFarm.lb_id).\
                  filter(models.LoadBalancer.tenant_id == tenant_id)
    vips = query.all()
    return vips


def virtualserver_create(conf, values):
    session = get_session(conf)
    with session.begin():
        vserver_ref = models.VirtualServer()
        vserver_ref.update(values)
        session.add(vserver_ref)
        return vserver_ref


def virtualserver_update(conf, vserver_id, values):
    session = get_session(conf)
    with session.begin():
        vserver_ref = virtualserver_get(conf, vserver_id, session=session)
        vserver_ref.update(values)
        return vserver_ref


def virtualserver_destroy(conf, vserver_id):
    session = get_session(conf)
    with session.begin():
        vserver_ref = virtualserver_get(conf, vserver_id, session=session)
        session.delete(vserver_ref)


def virtualserver_destroy_by_sf_id(conf, sf_id, session=None):
    session = session or get_session(conf)
    with session.begin():
        session.query(models.VirtualServer).filter_by(sf_id=sf_id).delete()
