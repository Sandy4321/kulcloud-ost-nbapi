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

"""
def luhnok(node, value):
    sum = 0
    num_digits = len(value)
    oddeven = num_digits & 1

    for count in range(0, num_digits):
        digit = int(value[count])

        if not (( count & 1 ) ^ oddeven ):
            digit = digit * 2
        if digit > 9:
            digit = digit - 9

        sum = sum + digit

    if not (sum % 10) == 0:
        raise Invalid(node,
                      '%r is not a valid credit card number' % value)
                      
class Schema(colander.MappingSchema):
    cc_number = colander.SchemaNode(colander.String(), validator=lunhnok)

"""



class validator(object):
	'''
	classdocs
	POST argument validation chacek library		
	'''


	def __init__(self, params):
		'''
		Constructor
		'''
		
	def mac_addr_validator(self, node, value):
		pass
	
	def ip_addr_validator(self, node, value):
		pass
	
	def dpid_validator(self, node, value):
		pass
	
	
		
	
		
		
		
	
