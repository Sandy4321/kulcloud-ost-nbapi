from kulcloud.core.v1.mlapi import check_pps
import MySQLdb as mdb
import MySQLdb.cursors
import time
import pdb


interval_time = 3
pps_type = 0

try:
    con = mdb.connect("localhost", "root", "of#123", "skdemo2")
    cur = con.cursor(mdb.cursors.DictCursor)
except:
    exit(1)

inport_duration = dict()
outport_duration = dict()
prev_pps = dict()
prev_bps = dict()
module = check_pps()
#pdb.set_trace()
cur.execute("SELECT * FROM nfvvm")
nfvvm_list = cur.fetchall()

for nfvvm in nfvvm_list:
    key = nfvvm["nfv_vm_id"]
    inport_duration[key] = 0
    outport_duration[key] = 0
    prev_pps[key] = 0.0
    prev_bps[key] = 0.0

#try:
if True:
    while True:
        cur.execute("SELECT * FROM nfvvm WHERE active = 1")
        nfv_list = cur.fetchall()

        for nfv in nfv_list:
            cur.execute("SELECT * FROM logicswitch WHERE logical_dpid = %s", nfv["dpid"])

            dpid = cur.fetchone()
            #pdb.set_trace()
            port = list()
            port = module.get_switch_statistics_port(str(dpid["dpid"]), nfv["in_port"], pps_type )
            #print pps
            #print bps
            
            print time.strftime("%Y-%m-%d %X", time.localtime()), nfv["nfv_vm_id"], ":", port[0], port[1]

            key = nfv["nfv_vm_id"]

            if port[0] <= 0.0:
                if prev_pps[key] != port[0]:
                    if inport_duration[key] > interval_time * 3:
                        inport_duration[key] = 0
                        prev_pps[key] = port[0]
                    else:
                        inport_duration[key] += interval_time
                        pps = prev_pps[key]
            else:
                prev_pps[key] = port[0]
                inport_duration[key] = 0

            if port[1] <= 0.0:
                if prev_bps[key] != port[1]:
                    if outport_duration[key] > interval_time * 3:
                        outport_duration[key] = 0
                        prev_bps[key] = port[1]
                    else:
                        outport_duration[key] += interval_time
                        port[1] = prev_bps[key]
            else:
                prev_bps[key] = port[1]
                outport_duration[key] = 0


            cur.execute("UPDATE nfvvmStatus SET in_port_pps = %s, out_port_pps = %s WHERE nfv_vm_id = %s", ((port[0] * 8), (port[1] * 8 * 1.08), nfv["nfv_vm_id"]) )
            con.commit()

            cur.execute("SELECT * FROM nfvvmThreshold WHERE nfv_id = %s", nfv["nfv_id"])
            threshold = cur.fetchone()
            if port[1] * 8 >= threshold["inport_pps_threshold"] and nfv["active_threshold"] == 0:
                cur.execute("UPDATE nfvvm SET active_threshold = 1 WHERE nfv_vm_id = %s", key)
                con.commit()
            elif port[1] * 8 < threshold["inport_pps_threshold"] and nfv["active_threshold"] == 1:
                cur.execute("UPDATE nfvvm SET active_threshold = 0 WHERE nfv_vm_id = %s", key)
                con.commit()
        
        time.sleep(interval_time)
        

#except Exception as err: #KeyboardInterrupt:
else:
    print "The End", err
    exit(1)
#finally:
    con.close()
