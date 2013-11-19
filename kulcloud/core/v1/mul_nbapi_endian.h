/*
 *  mul_nbapi_endian.h: Mul Northbound Endian convert application headers
 *  Copyright (C) 2013, Jun Woo Park <johnpa@gmail.com>
 * 
 * This program is free software; you can redistribute it and/or
 * modify it under the terms of the GNU General Public License
 * as published by the Free Software Foundation; either version 2
 * of the License, or (at your option) any later version.
 *
 * This program is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with this program; if not, write to the Free Software
 * Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.
 */


#ifndef __MUL_NBAPI_ENDIAN_H__
#define __MUL_NBAPI_ENDIAN_H__

#include "openflow.h"
#include "mul_app_interface.h"


static inline void nbapi_endian_convert_ofp_phy_port(struct ofp_phy_port *port, uint16_t (*convs)(uint16_t), uint32_t (*convl)(uint32_t)) {
    port->port_no = convs(port->port_no);
    port->config = convl(port->config);
    port->state = convl(port->state);
    port->curr = convl(port->curr);
    port->advertised = convl(port->advertised);
    port->supported = convl(port->supported);
    port->peer = convl(port->peer);
}
static inline void ntoh_ofp_phy_port(struct ofp_phy_port *port) {
    nbapi_endian_convert_ofp_phy_port(port,ntohs,ntohl);
}
static inline void hton_ofp_phy_port(struct ofp_phy_port *port) {
    nbapi_endian_convert_ofp_phy_port(port,htons,htonl);
}

static inline void nbapi_endian_convert_ofp_header(struct ofp_header *header, uint16_t (*convs)(uint16_t), uint32_t (*convl)(uint32_t)) {
    header->length = convs(header->length);
    header->xid = convl(header->xid);
}
static inline void ntoh_ofp_header(struct ofp_header *header) {
    nbapi_endian_convert_ofp_header(header,ntohs,ntohl);
}
static inline void hton_ofp_header(struct ofp_header *header) {
    nbapi_endian_convert_ofp_header(header,htons,htonl);
}

static inline void nbapi_endian_convert_ofp_switch_features(struct ofp_switch_features *switch_info, uint16_t (*convs)(uint16_t), uint32_t (*convl)(uint32_t), uint64_t (*convll)(uint64_t)) {
    int i, n_ports = ((ntohs(switch_info->header.length)
                - offsetof(struct ofp_switch_features, ports))
            / sizeof *switch_info->ports);
    nbapi_endian_convert_ofp_header(&switch_info->header,convs,convl);
    switch_info->datapath_id = convll(switch_info->datapath_id);
    switch_info->n_buffers = convl(switch_info->n_buffers);
    switch_info->capabilities = convl(switch_info->capabilities);
    switch_info->actions = convl(switch_info->actions);
    for (i = 0; i < n_ports; i ++) {
        nbapi_endian_convert_ofp_phy_port(&switch_info->ports[i],convs,convl);
    }
}
static inline void ntoh_ofp_switch_features(struct ofp_switch_features *switch_info) {
    nbapi_endian_convert_ofp_switch_features(switch_info,ntohs,ntohl,ntohll);
}
static inline void hton_ofp_switch_features(struct ofp_switch_features *switch_info) {
    nbapi_endian_convert_ofp_switch_features(switch_info,htons,htonl,htonll);
}

static inline void nbapi_endian_convert_c_ofp_req_dpid_attr(struct c_ofp_req_dpid_attr *dpid_attr, uint64_t (*convll)(uint64_t)) {
    dpid_attr->datapath_id = convll(dpid_attr->datapath_id);
}
static inline void ntoh_c_ofp_req_dpid_attr(struct c_ofp_req_dpid_attr *dpid_attr) {
    nbapi_endian_convert_c_ofp_req_dpid_attr(dpid_attr,ntohll);
}
static inline void hton_c_ofp_req_dpid_attr(struct c_ofp_req_dpid_attr *dpid_attr) {
    nbapi_endian_convert_c_ofp_req_dpid_attr(dpid_attr,htonll);
}
static inline void nbapi_endian_convert_c_ofp_switch_brief(struct c_ofp_switch_brief *switch_brief, uint32_t (*convl)(uint32_t), uint64_t (*convll)(uint64_t)) {
    nbapi_endian_convert_c_ofp_req_dpid_attr(&switch_brief->switch_id,convll);
    switch_brief->n_ports = convl(switch_brief->n_ports);
    switch_brief->state = convl(switch_brief->state);
}
static inline void ntoh_c_ofp_switch_brief(struct c_ofp_switch_brief *switch_brief) {
    nbapi_endian_convert_c_ofp_switch_brief(switch_brief,ntohl,ntohll);
}
static inline void hton_c_ofp_switch_brief(struct c_ofp_switch_brief *switch_brief) {
    nbapi_endian_convert_c_ofp_switch_brief(switch_brief,htonl,htonll);
}
static inline void nbapi_endian_convert_flow(struct flow *fl, uint16_t (*convs)(uint16_t), uint32_t (*convl)(uint32_t)) {
    fl->nw_src = convl(fl->nw_src);
    fl->nw_dst = convl(fl->nw_dst);
    fl->in_port = convs(fl->in_port);
    fl->dl_vlan = convs(fl->dl_vlan);
    fl->dl_type = convs(fl->dl_type);
    fl->tp_src = convs(fl->tp_src);
    fl->tp_dst = convs(fl->tp_dst);
}
static inline void ntoh_flow(struct flow *fl) {
    nbapi_endian_convert_flow(fl, ntohs, ntohl);
}
static inline void hton_flow(struct flow *fl) {
    nbapi_endian_convert_flow(fl, htons, htonl);
}
static inline void nbapi_endian_convert_c_ofp_port_neigh(struct c_ofp_port_neigh *port, uint16_t (*convs)(uint16_t), uint64_t (*convll)(uint64_t)) {
    port->port_no = convs(port->port_no);
    port->neigh_present = convs(port->neigh_present);
    port->neigh_port = convs(port->neigh_port);
    port->neigh_dpid = convll(port->neigh_dpid);
}
static inline void ntoh_c_ofp_port_neigh(struct c_ofp_port_neigh *port) {
    nbapi_endian_convert_c_ofp_port_neigh(port, ntohs, ntohll);
}
static inline void hton_c_ofp_port_neigh(struct c_ofp_port_neigh *port) {
    nbapi_endian_convert_c_ofp_port_neigh(port, htons, htonll);
}
#endif
