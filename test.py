import json
import requests
import MySQLdb as mdb
import time
#import sys

#url = "http://localhost:8181/1.0/NFVDB/stats/0x1000082e5f626200/4"
#url = "http://localhost:8181/1.0/servicech/rule/%s" % sys.argv[1]
#url = "http://localhost:8181/1.0/servicech/default/rule"
#url = "http://localhost:8181/1.0/servicech/ALL/services/Video"
#url = "http://localhost:8181/1.0/servicech/010-2096-0220"
#url = "http://localhost:8181/1.0/servicech/log/0x00237d2948f4/5/50.1.19.12"
#url = "http://localhost:8181/1.0/servicech/111-1111-1111"
#url = "http://localhost:8181/1.0/servicech/rule/999999"
#url = "http://localhost:8181/1.0/servicech/stats/200005"
#url = "http://localhost:8181/1.0/servicech/sdn/mode"
#url = "http://localhost:8181/1.0/servicech/legacy/chain"
url = "http://localhost:8181/1.0/NFVDB/stats/ALL"
#url = "http://localhost:8181/1.0/NFVDB/LB/vWTCP"

#message = {"cpu_threshold":30, "cpu_duration":1000, "pps_threshold":3400000, "pps_duration":1001}
#message = {"dpid":"0x00237d2948f4", "port":6, "ip":"1.2.3.4"}
#message = {"ip" : "111.111.111.111", "mdn" : "111-1111-1111", "service_level" : 1}
#message = {"chain_id" : 200005, "index":1}
#message = {"mdn" : "ALL"}
#message = {"nfv_list":"NAT"}
#message = {"mdn" : "010-2000-3003"}
message = {"type":"virtual", "name":"AA", "nfv_name":"VWTCP_VM5", "dpid":"0x05", "in_port":66, "out_port":67, "index":6}

sec = time.time()
#r = requests.post(url)
#r = requests.post(url, json.dumps(message))
r = requests.get(url)
#r = requests.delete(url)

print r
print r.text
#print r.json()
#print r.json()
print time.time() - sec
"""
con = mdb.connect("localhost", "root", "of#123", "skdemo2")
cur = con.cursor(mdb.cursors.DictCursor)

chain_id = 100001
user_ip = "192.168.0."
index = 0
service_id = 1
user_id = 0
for i in range(130,254):
    if ( i-128 ) % ((254-130)/9) == 0 and (i != 128):
        chain_id += 100000
        service_id += 1
        index=0
    ip = user_ip + str(i)
    cur.execute("INSERT INTO ippool (chain_id,ip, user_id, service_id) VALUES (%s, %s, %s, %s)", (chain_id+index, ip, user_id, service_id))
    index=index+1


nfv_groupname = "vWTCP"
cur.execute("SELECT a.nfv, b.nfv_id, SUM(c.out_port_pps) as avg_inport_pps, SUM(c.cpu_usage) as avg_cpu_usage FROM nfv as a, nfvvm as b, nfvvmStatus as c WHERE a.nfv_id = b.nfv_id AND b.nfv_vm_id = c.nfv_vm_id AND a.nfv = %s AND b.active = 1", nfv_groupname)
row = cur.fetchone()

con.commit()
con.close()

print row
print row["avg_inport_pps"]
"""
