import MySQLdb as mdb
import time

con = mdb.connect("localhost", "root", "of#123", "skdemo2")
cur = con.cursor(mdb.cursors.DictCursor)

cur.execute("SELECT nfv_id, nfv_vm_id, nfvvm.index, dpid, in_port, out_port FROM nfvvm ORDER BY nfv_id, nfv_vm_id")
rows = cur.fetchall()

vm_map = dict()
for row in rows:
    vm_map[row["nfv_vm_id"]] = row
nfvvm_list = [vm_map[vm] for vm in vm_map if vm_map[vm]["nfv_id"] == 1]

print nfvvm_list
