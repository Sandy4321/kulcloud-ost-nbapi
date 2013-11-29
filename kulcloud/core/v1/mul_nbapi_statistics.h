/*
 *  mul_nbapi_statistics.h: Mul Northbound Statistics API application headers
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
#ifndef __MUL_NBAPI_STATISTICS_H__
#define __MUL_NBAPI_STATISTICS_H__

#include "mul_app_interface.h"
#include "mul_nbapi_swig_helper.h"

#ifdef SWIG
  %newobject nbapi_parse_bps_to_str;
  %newobject nbapi_parse_pps_to_str;
#endif

MUL_NBAPI_PYLIST_RETURN(c_ofp_flow_info, nbapi_switch_flow_list_t)

nbapi_switch_flow_list_t  get_switch_statistics_all(uint64_t datapath_id);


char *nbapi_parse_bps_to_str(uint8_t *bps);
char *nbapi_parse_pps_to_str(uint8_t *pps);
#endif
