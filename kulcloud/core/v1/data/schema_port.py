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


 
class Port(colander.MappingSchema):
    # TODO: Make more intelligent validator    
    status = colander.SchemaNode(colander.String(),
                                 validator=colander.OneOf(['home']))
    mac_addr = colander.SchemaNode(colander.String())
    port_no = colander.SchemaNode(colander.Int(),
                                validator=colander.Range(0,256))
    name = colander.SchemaNode(colander.String())
    
    
    
    
    

        