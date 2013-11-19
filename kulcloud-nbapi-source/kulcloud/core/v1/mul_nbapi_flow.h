/*
 *  mul_nbapi_topology.h: Mul Northbound Static Flow API application headers
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
#ifndef __MUL_NBAPI_FLOW_H__
#define __MUL_NBAPI_FLOW_H__

#include "mul_app_interface.h"
#include "glib.h"

enum nbapi_flow_struct_type {
    NBAPI_FLOW_STRUCT_TYPE_OUTPUT,
    NBAPI_FLOW_STRUCT_TYPE_VLAN_VID,
    NBAPI_FLOW_STRUCT_TYPE_HEADER,
    NBAPI_FLOW_STRUCT_TYPE_DL_ADDR,
    NBAPI_FLOW_STRUCT_TYPE_NW_ADDR,
    NBAPI_FLOW_STRUCT_TYPE_VLAN_PCP,
    NBAPI_FLOW_STRUCT_TYPE_NW_TOS,
    NBAPI_FLOW_STRUCT_TYPE_TP_PORT
};

/* Note: 
 *      When passing action list from python, we are expecting following data format:
 *          [(ofp_action* objects, type of such object),
 *           (struct ofp_aciton_ *, NBAPI_FLOW_STRUCT_TYPE constant)
 *           ...]
 *
 *      where ofp_action* object is return values from nbapi_make_action functions
 *
 * Remark: I added NBAPI_FLOW_STRUCT_TYPE constant since I needed type information to 
 *         convert objects from list. 
 */

#ifdef SWIG
    %{
        static GSList *__nbapi_typemap_glist_actions(PyObject *list) {
            if (PyList_Check(list)) {
                int size = PyList_Size(list);
                int i = 0;
                GSList *ret_val = NULL;
                for (i = 0; i < size; i++) {
                    PyObject *tuple = PyList_GetItem(list,i);
                    if (PyTuple_Check(tuple)) {
                        PyObject *proxy = PyTuple_GetItem(tuple, 0);
                        int type = PyInt_AsLong(PyTuple_GetItem(tuple, 1));
                        swig_type_info *type_info;
                        void *struct_ptr;

                        switch (type) {
                            case NBAPI_FLOW_STRUCT_TYPE_OUTPUT:
                                type_info = SWIGTYPE_p_ofp_action_output;
                                break;
                            case NBAPI_FLOW_STRUCT_TYPE_VLAN_VID:
                                type_info = SWIGTYPE_p_ofp_action_vlan_vid;
                                break;
                            case NBAPI_FLOW_STRUCT_TYPE_HEADER:
                                type_info = SWIGTYPE_p_ofp_action_header;
                                break;
                            case NBAPI_FLOW_STRUCT_TYPE_DL_ADDR:
                                type_info = SWIGTYPE_p_ofp_action_dl_addr;
                                break;
                            case NBAPI_FLOW_STRUCT_TYPE_NW_ADDR:
                                type_info = SWIGTYPE_p_ofp_action_nw_addr;
                                break;
                            case NBAPI_FLOW_STRUCT_TYPE_VLAN_PCP:
                                type_info = SWIGTYPE_p_ofp_action_vlan_pcp;   
                                break;
                            case NBAPI_FLOW_STRUCT_TYPE_NW_TOS:
                                type_info = SWIGTYPE_p_ofp_action_nw_tos;
                                break;
                            case NBAPI_FLOW_STRUCT_TYPE_TP_PORT:
                                type_info = SWIGTYPE_p_ofp_action_tp_port;
                                break;
                            default:
                                PyErr_SetString(PyExc_TypeError, "invalid type const detected");
                                return NULL;
                        }

                        if ((SWIG_ConvertPtr(proxy, &struct_ptr, type_info, 
                                           SWIG_POINTER_EXCEPTION)) == -1) {
                            return NULL;
                        }
                        ret_val = g_slist_prepend(ret_val, struct_ptr);

                    } else {
                        PyErr_SetString(PyExc_TypeError,"not a list");
                        return NULL;
                    }
                }
                ret_val = g_slist_reverse(ret_val);
                return ret_val;
            } 
            PyErr_SetString(PyExc_TypeError,"not a list");
            return NULL;
            
        }
        static PyObject *__nbapi_wrap_ofp_action_struct(void *obj, swig_type_info *type_info, int type_no) {
            PyObject *tuple = PyTuple_New(2);
            PyObject *proxy, *type;
            if (!tuple) return NULL;
            
            proxy = SWIG_NewPointerObj(obj, type_info, SWIG_POINTER_OWN);
            type = PyInt_FromLong(type_no);
            if (!proxy || !type) {
                return NULL;
            }
            PyTuple_SetItem(tuple, 0, proxy);
            PyTuple_SetItem(tuple, 1, type);
            return tuple;
        }
    %}

    %newobject nbapi_parse_mac_to_str;
    %newobject nbapi_parse_nw_addr_to_str;
    %newobject nbapi_parse_cidr_to_str;
    %newobject nbapi_flow_make_flow;


    %typemap(in) GSList *actions {
        $1 = __nbapi_typemap_glist_actions($input);
        if (!$1) {
            return NULL;
        }

        
    }
    #define NBAPI_FLOW_WRAP_OFP_ACTION_TYPEMAP(Type, Const)     \
        %typemap(out) ##Type## * {                                           \
        PyObject *tuple = __nbapi_wrap_ofp_action_struct($1, $1_descriptor   \
                                            , ##Const##);                    \
        if (!tuple) {                                                        \
            PyErr_SetString(PyExc_TypeError,                                 \
                            "Error converting Type * to PyObject"); \
        }                                                                    \
        return tuple;                                                        \
    }
    NBAPI_FLOW_WRAP_OFP_ACTION_TYPEMAP(struct ofp_action_output,
                                        NBAPI_FLOW_STRUCT_TYPE_OUTPUT)
    NBAPI_FLOW_WRAP_OFP_ACTION_TYPEMAP(struct ofp_action_vlan_vid,
                                        NBAPI_FLOW_STRUCT_TYPE_VLAN_VID)
    NBAPI_FLOW_WRAP_OFP_ACTION_TYPEMAP(struct ofp_action_dl_addr,
                                        NBAPI_FLOW_STRUCT_TYPE_DL_ADDR)
    NBAPI_FLOW_WRAP_OFP_ACTION_TYPEMAP(struct ofp_action_nw_addr,
                                        NBAPI_FLOW_STRUCT_TYPE_NW_ADDR)
    NBAPI_FLOW_WRAP_OFP_ACTION_TYPEMAP(struct ofp_action_vlan_pcp,
                                        NBAPI_FLOW_STRUCT_TYPE_VLAN_PCP)
    NBAPI_FLOW_WRAP_OFP_ACTION_TYPEMAP(struct ofp_action_nw_tos,
                                        NBAPI_FLOW_STRUCT_TYPE_NW_TOS)
    NBAPI_FLOW_WRAP_OFP_ACTION_TYPEMAP(struct ofp_action_tp_port,
                                        NBAPI_FLOW_STRUCT_TYPE_TP_PORT)


#endif

int add_static_flow(uint64_t datapath_id, 
                struct flow *fl, uint32_t wildcards, 
                uint16_t priority, 
                GSList *actions);
int delete_static_flow(uint64_t datapath_id, 
                struct flow *fl, uint32_t wildcards, 
                uint16_t out_port_no, 
                uint16_t priority);

/* helpers to access data */
char *nbapi_parse_mac_to_str(uint8_t *mac);
char *nbapi_parse_nw_addr_to_str(uint32_t nw_addr);
char *nbapi_parse_cidr_to_str(uint32_t nw_addr, uint8_t prefix_len);

/* helpers to create arguments */
struct flow *nbapi_flow_make_flow(char *nw_src, char *nw_dst,
                                    uint16_t in_port, 
                                    uint16_t dl_vlan, uint16_t dl_type,
                                    uint16_t tp_src, uint16_t tp_dst,
                                    char *dl_src, char *dl_dst,
                                    uint8_t dl_vlan_pcp,
                                    uint8_t nw_tos,
                                    uint8_t nw_proto);

/* helpers to make action structs */
struct ofp_action_output *nbapi_make_action_output(uint16_t oport);
struct ofp_action_vlan_vid *nbapi_make_action_set_vid(uint16_t vid);
struct ofp_action_header *nbapi_make_action_strip_vlan(void);
struct ofp_action_dl_addr *nbapi_make_action_set_dmac(char *dmac_str);
struct ofp_action_dl_addr *nbapi_make_action_set_smac(char *smac_str);
struct ofp_action_nw_addr *nbapi_make_action_set_nw_saddr(char * nw_saddr_str);
struct ofp_action_nw_addr *nbapi_make_action_set_nw_daddr(char * nw_daddr_str);
struct ofp_action_vlan_pcp *nbapi_make_action_set_vlan_pcp(uint8_t vlan_pcp);
struct ofp_action_nw_tos *nbapi_make_action_set_nw_tos(uint8_t tos);
struct ofp_action_tp_port *nbapi_make_action_set_tp_dport(uint16_t port);
struct ofp_action_tp_port *nbapi_make_action_set_tp_sport(uint16_t port);



/* FIXME: Not needed for now */
/*
typedef struct {
    struct flow fl;
    uint32_t wildcards
    uint16_t priority;
    tuple action_list;
} flow_info_t
*/



#endif
