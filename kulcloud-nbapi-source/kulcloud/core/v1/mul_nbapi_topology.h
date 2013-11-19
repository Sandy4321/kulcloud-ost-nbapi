/*
 *  mul_nbapi_topology.h: Mul Northbound Topology API application headers
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
#ifndef __MUL_NBAPI_TOPOLOGY_H__
#define __MUL_NBAPI_TOPOLOGY_H__

#include "mul_app_interface.h"
#include "mul_nbapi_swig_helper.h"



MUL_NBAPI_PYLIST_RETURN(c_ofp_switch_brief, nbapi_switch_brief_list_t)
MUL_NBAPI_PYLIST_RETURN(ofp_phy_port, nbapi_port_list_t)
MUL_NBAPI_PYLIST_RETURN(c_ofp_port_neigh, nbapi_port_neigh_list_t)


#ifdef SWIG
    %newobject get_switch;
    %newobject get_switch_port;

    %include "carrays.i"
    %array_class(struct ofp_phy_port, ofp_phy_port_array);

#endif
uint32_t get_switch_alias_from_switch_info(struct ofp_switch_features *switch_info);
struct ofp_switch_features  *get_switch(uint64_t datapath_id);
nbapi_switch_brief_list_t  get_switch_all(void);

struct ofp_phy_port         *get_switch_port(uint64_t datapath_id, uint16_t port_no);
nbapi_port_list_t   get_switch_port_all(uint64_t datapath_id);

/* TODO: Device not supported by Topology Manager MLAPI Service */
/*
typedef struct {
    uint64_t device_id;
    uint32_t type;
    uint32_t tenant_id;
} Device;

Device *get_device_all();
int add_device(Device *device);
Device get_device(uint64_t datapath_id);
int modify_device(Device *device);
int remove_device(Device *device);
Port *get_device_port_all(uint64_t device_id);
int add_device_port(Port *port);
Port get_device_port(uint64_t device_id, uint16_t port_id);
int modify_device_port(Port *port);
int remove_device_port(Port *port);
*/

nbapi_port_neigh_list_t get_switch_neighbor_all(uint64_t datapath_id);



#endif
