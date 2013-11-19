from kulcloud.core.v1.mlapi import mlapi

api = mlapi()
dpid = "0xac162dbbd378"

print api.get_stat_port(0, dpid, 1)
