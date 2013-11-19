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
import colander
from kulcloud.core.v1.data.schema_action import Action_list as Action_list

class Flow(colander.MappingSchema):
    nw_src = colander.SchemaNode(colander.String(), missing=None)
    nw_dst = colander.SchemaNode(colander.String(), missing=None)
    dl_src = colander.SchemaNode(colander.String(), missing=None)
    dl_dst = colander.SchemaNode(colander.String(), missing=None)
    dl_vlan = colander.SchemaNode(colander.Int(), missing=0)
    dl_type = colander.SchemaNode(colander.Int(), missing=0) 
    tp_src = colander.SchemaNode(colander.Int(), missing=0)
    tp_dst = colander.SchemaNode(colander.Int(), missing=0)
    dl_vlan_pcp = colander.SchemaNode(colander.Int(), missing=0)
    nw_tos = colander.SchemaNode(colander.Int(), missing=0)
    nw_proto = colander.SchemaNode(colander.Int(), missing=0)
    in_port = colander.SchemaNode(colander.Int(), missing=0)
    actions = Action_list()



    
    
    
    
    

        
