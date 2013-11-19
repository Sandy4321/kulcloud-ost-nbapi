import logging
import sys
import MySQLdb as mdb
import kulcloud.core.v1.mlapi as mlapi

class what():
    def __init__(self):
        self.vm_map = dict()
        self.threshold_map = list()
        self.the()

    def the(self):
        con = mdb.connect("localhost", "root", "of#123", "skdemo2")
        cur = con.cursor(mdb.cursors.DictCursor)

        cur.execute("SELECT nfv_id, nfv_vm_id, nfv_name, dpid, in_port, out_port FROM nfvvm ORDER BY nfv_id, nfv_vm_id")
        row = cur.fetchall()

        self.vm_map = row

        cur.execute("SELECT * FROM nfvvmThreshold ORDER BY nfv_id")
        threshold_list = cur.fetchall()

        for i in range(threshold_list[-1]["nfv_id"]):
            self.threshold_map.append(dict())

        for threshold in threshold_list:
            self.threshold_map[threshold["nfv_id"] - 1] = threshold
            #print threshold

        return True


con = mdb.connect("localhost", "root", "of#123", "skdemo2")
cur = con.cursor(mdb.cursors.DictCursor)

hell = what()

#nfvvm = [vm for vm in hell.vm_map if vm["nfv_id"] == 1]
c_dpid = '0x05'
in_port = 1
out_port = 2
nfvvm = [vm for vm in hell.vm_map if vm["dpid"] == c_dpid and (vm["in_port"] == in_port or vm["in_port"] == out_port or vm["out_port"] == in_port or vm["out_port"] == out_port)]

if not nfvvm:
    print "what"
for nfv in nfvvm:
    print nfv
"""
cur.execute("SELECT b.nfv_name, b.nfv_id, b.index, a.nfv_vm_id, a.out_port_pps as inport_pps, a.cpu_usage, c.cpu_usage_threshold, c.cpu_usage_duration as cpu_duration, c.inport_pps_threshold, c.inport_pps_duration FROM nfvvmStatus as a, nfvvm as b, nfvvmThreshold as c WHERE a.nfv_vm_id = b.nfv_vm_id AND b.nfv_id = c.nfv_id AND b.active = 1 ORDER BY b.nfv_id, b.nfv_vm_id")
rows = cur.fetchall()

result = {"message" : "SUCCESS", "flow" : rows}
print result
"""
"""
cur.execute("SELECT SUM(a.out_port_pps) as avg_inport_pps FROM nfvvmStatus as a, nfvvm as b WHERE b.nfv_id = 10 AND b.nfv_vm_id = a.nfv_vm_id")
stat = cur.fetchone()

print stat
print float(stat["avg_inport_pps"])
print float(None)
"""

"""
con = mdb.connect("localhost", "root", "of#123", "skdemo2")
cur = con.cursor(mdb.cursors.DictCursor)

cur.execute("SELECT nfv_id FROM nfv")
nfv_list = cur.fetchall()

for nfv in nfv_list:
    #print nfv["nfv_id"]
    cur.execute("SELECT SUM(a.out_port_pps) as avg_inport_pps, AVG(a.cpu_usage) as avg_cpuusage FROM nfvvmStatus as a, nfvvm as b WHERE b.nfv_id = %s AND a.nfv_vm_id = b.nfv_vm_id", nfv["nfv_id"])
    stat = cur.fetchone()

    avg = float(stat["avg_inport_pps"])
    #print stat
    #print avg
    #cur.execute("SELECT SUM(a.out_port_pps) as avg_inport_pps, AVG(a.cpu_usage) as avg_cpuusage FROM nfvvmStatus as a, nfvvm as b WHERE b.nfv_id = 1 AND a.nfv_vm_id = b.nfv_vm_id", nfv["nfv_id"])
    #stat = cur.fetchone()

    #print stat
"""
"""
cur.execute("SELECT * FROM servicechainrule WHERE chain_id IN (SELECT DISTINCT chain_id FROM servicechainlog WHERE nfv_name IN (SELECT nfv_name FROM servicechainlog WHERE chain_id = 100008) ) GROUP BY chain_id")
#cur.execute("SELECT * FROM servicechainlog WHERE chain_id IN (SELECT chain_id FROM ippool WHERE user_id = 86) GROUP BY chain_id, nfv_name")
what = cur.fetchall()


print what
"""
#print the
"""
con = mdb.connect("localhost", "root", "of#123", "skdemo2")
cur = con.cursor(mdb.cursors.DictCursor)

cur.execute("SELECT * FROM servicechainlog")
chainlog_list = cur.fetchall()

what = [nfv["nfv_name"] for nfv in chainlog_list if nfv["service_id"] == 1]
print what
"""

#cur.close()
#con.close()
