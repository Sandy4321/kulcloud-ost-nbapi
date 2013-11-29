

"""
v1 Kulcloud ML(Middle Le API specification.

MlapiBasev1 provides the definition of minimum set of
methods that needs to be implemented by MUL controller ML API version1
"""
from abc import ABCMeta, abstractmethod

class MlapiBaseV1(object):
	
	__metaclass__ = ABCMeta

	@abstractmethod
	def get_all_flow(self, conf, dpid):
		"""
		Create a subnet, which represents a range of IP addresses
		that can be allocated to devices
		: param context: quantum api request context
		: param subnet: dictionary describing the subnet, with keys
			as listed in the RESOURCE_ATTRIBUTE_MAP object in
			quantum/api/v2/attributes.py.  All keys will be populated.
		"""
		pass
	
	@abstractmethod
	def get_flow(self, conf, dpid, flow_id):
		"""
		Create a subnet, which represents a range of IP addresses
		that can be allocated to devices
		: param context: quantum api request context
		: param subnet: dictionary describing the subnet, with keys
			as listed in the RESOURCE_ATTRIBUTE_MAP object in
			quantum/api/v2/attributes.py.  All keys will be populated.
		"""
		pass
	
	@abstractmethod
	def create_flow(self, conf, dpid, params):
		"""
		Create a subnet, which represents a range of IP addresses
		that can be allocated to devices
		: param context: quantum api request context
		: param subnet: dictionary describing the subnet, with keys
			as listed in the RESOURCE_ATTRIBUTE_MAP object in
			quantum/api/v2/attributes.py.  All keys will be populated.
		"""
		pass
	
	@abstractmethod
	def update_flow(self, conf, dpid, flow_id, params):
		"""
		Create a subnet, which represents a range of IP addresses
		that can be allocated to devices
		: param context: quantum api request context
		: param subnet: dictionary describing the subnet, with keys
			as listed in the RESOURCE_ATTRIBUTE_MAP object in
			quantum/api/v2/attributes.py.  All keys will be populated.
		"""
		pass
	
	@abstractmethod
	def delete_flow(self, conf, dpid, flow_id):
		"""
		Create a subnet, which represents a range of IP addresses
		that can be allocated to devices
		: param context: quantum api request context
		: param subnet: dictionary describing the subnet, with keys
			as listed in the RESOURCE_ATTRIBUTE_MAP object in
			quantum/api/v2/attributes.py.  All keys will be populated.
		"""
		pass
	
	@abstractmethod
	def get_all_switch(self, conf):
		"""
		Create a subnet, which represents a range of IP addresses
		that can be allocated to devices
		: param context: quantum api request context
		: param subnet: dictionary describing the subnet, with keys
			as listed in the RESOURCE_ATTRIBUTE_MAP object in
			quantum/api/v2/attributes.py.  All keys will be populated.
		"""
		pass		
	
	@abstractmethod
	def get_switch(self, conf, dpid):
		"""
		Create a subnet, which represents a range of IP addresses
		that can be allocated to devices
		: param context: quantum api request context
		: param subnet: dictionary describing the subnet, with keys
			as listed in the RESOURCE_ATTRIBUTE_MAP object in
			quantum/api/v2/attributes.py.  All keys will be populated.
		"""
		pass
	
	
	@abstractmethod
	def get_all_port(self, conf, dpid):
		"""
		Create a subnet, which represents a range of IP addresses
		that can be allocated to devices
		: param context: quantum api request context
		: param subnet: dictionary describing the subnet, with keys
			as listed in the RESOURCE_ATTRIBUTE_MAP object in
			quantum/api/v2/attributes.py.  All keys will be populated.
		"""
		pass
	
	@abstractmethod
	def get_port(self, conf, dpid, port_id):
		"""
		Create a subnet, which represents a range of IP addresses
		that can be allocated to devices
		: param context: quantum api request context
		: param subnet: dictionary describing the subnet, with keys
			as listed in the RESOURCE_ATTRIBUTE_MAP object in
			quantum/api/v2/attributes.py.  All keys will be populated.
		"""
		pass
	
	@abstractmethod
	def get_all_link(self, dpid):
		"""
		Create a subnet, which represents a range of IP addresses
		that can be allocated to devices
		: param context: quantum api request context
		: param subnet: dictionary describing the subnet, with keys
			as listed in the RESOURCE_ATTRIBUTE_MAP object in
			quantum/api/v2/attributes.py.  All keys will be populated.
		"""
		pass
	
	@abstractmethod
	def get_link(self, conf, link_id):
		"""
		Create a subnet, which represents a range of IP addresses
		that can be allocated to devices
		: param context: quantum api request context
		: param subnet: dictionary describing the subnet, with keys
			as listed in the RESOURCE_ATTRIBUTE_MAP object in
			quantum/api/v2/attributes.py.  All keys will be populated.
		"""
		pass
	
	@abstractmethod
	def get_all_path(self, conf):
		"""
		Create a subnet, which represents a range of IP addresses
		that can be allocated to devices
		: param context: quantum api request context
		: param subnet: dictionary describing the subnet, with keys
			as listed in the RESOURCE_ATTRIBUTE_MAP object in
			quantum/api/v2/attributes.py.  All keys will be populated.
		"""
		pass
	
	@abstractmethod
	def get_path(self, path_id):
		"""
		Create a subnet, which represents a range of IP addresses
		that can be allocated to devices
		: param context: quantum api request context
		: param subnet: dictionary describing the subnet, with keys
			as listed in the RESOURCE_ATTRIBUTE_MAP object in
			quantum/api/v2/attributes.py.  All keys will be populated.
		"""
		pass
	
	@abstractmethod
	def get_all_host(self, conf, tenant_id, network_id):
		"""
		Create a subnet, which represents a range of IP addresses
		that can be allocated to devices
		: param context: quantum api request context
		: param subnet: dictionary describing the subnet, with keys
			as listed in the RESOURCE_ATTRIBUTE_MAP object in
			quantum/api/v2/attributes.py.  All keys will be populated.
		"""
		pass
	
	@abstractmethod
	def create_host(self, conf, tenant_id, network_id, params):
		"""
		Create a subnet, which represents a range of IP addresses
		that can be allocated to devices
		: param context: quantum api request context
		: param subnet: dictionary describing the subnet, with keys
			as listed in the RESOURCE_ATTRIBUTE_MAP object in
			quantum/api/v2/attributes.py.  All keys will be populated.
		"""
		pass
	
	@abstractmethod
	def delete_host(self, conf, tenant_id, network_id, host_id):
		"""
		Create a subnet, which represents a range of IP addresses
		that can be allocated to devices
		: param context: quantum api request context
		: param subnet: dictionary describing the subnet, with keys
			as listed in the RESOURCE_ATTRIBUTE_MAP object in
			quantum/api/v2/attributes.py.  All keys will be populated.
		"""
		pass
	
	@abstractmethod
	def get_host(self, conf, tenant_id, network_id, host_id):
		"""
		Create a subnet, which represents a range of IP addresses
		that can be allocated to devices
		: param context: quantum api request context
		: param subnet: dictionary describing the subnet, with keys
			as listed in the RESOURCE_ATTRIBUTE_MAP object in
			quantum/api/v2/attributes.py.  All keys will be populated.
		"""
		pass
	
	@abstractmethod
	def update_host(self, conf, tenant_id, network_id, host_id, body):
		"""
		Create a subnet, which represents a range of IP addresses
		that can be allocated to devices
		: param context: quantum api request context
		: param subnet: dictionary describing the subnet, with keys
			as listed in the RESOURCE_ATTRIBUTE_MAP object in
			quantum/api/v2/attributes.py.  All keys will be populated.
		"""
		pass
	
	
	@abstractmethod
	def get_all_servicech(self, conf):
		"""
		Create a subnet, which represents a range of IP addresses
		that can be allocated to devices
		: param context: quantum api request context
		: param subnet: dictionary describing the subnet, with keys
			as listed in the RESOURCE_ATTRIBUTE_MAP object in
			quantum/api/v2/attributes.py.  All keys will be populated.
		"""
		pass
	
	@abstractmethod
	def create_servicech(self, conf, params):
		"""
		Create a subnet, which represents a range of IP addresses
		that can be allocated to devices
		: param context: quantum api request context
		: param subnet: dictionary describing the subnet, with keys
			as listed in the RESOURCE_ATTRIBUTE_MAP object in
			quantum/api/v2/attributes.py.  All keys will be populated.
		"""
		pass
	
	@abstractmethod
	def delete_servicech(self, conf, phone_num):
		"""
		Create a subnet, which represents a range of IP addresses
		that can be allocated to devices
		: param context: quantum api request context
		: param subnet: dictionary describing the subnet, with keys
			as listed in the RESOURCE_ATTRIBUTE_MAP object in
			quantum/api/v2/attributes.py.  All keys will be populated.
		"""
		pass
	
	@abstractmethod
	def get_servicech(self, conf, phone_num):
		"""
		Create a subnet, which represents a range of IP addresses
		that can be allocated to devices
		: param context: quantum api request context
		: param subnet: dictionary describing the subnet, with keys
			as listed in the RESOURCE_ATTRIBUTE_MAP object in
			quantum/api/v2/attributes.py.  All keys will be populated.
		"""
		pass
	
	@abstractmethod
	def update_servicech(self, conf, phone_num, body):
		"""
		Create a subnet, which represents a range of IP addresses
		that can be allocated to devices
		: param context: quantum api request context
		: param subnet: dictionary describing the subnet, with keys
			as listed in the RESOURCE_ATTRIBUTE_MAP object in
			quantum/api/v2/attributes.py.  All keys will be populated.
		"""
		pass
	
	
	
	
	