import kulcloud.core.v1.mul_nbapi as mul_nbapi
import MySQLdb as mdb
import MySQLdb.cursors
import time
import pdb


interval_time = 2
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

cur.execute("SELECT * FROM nfvvm")
nfvvm_list = cur.fetchall()

for nfvvm in nfvvm_list:
    key = nfvvm["nfv_vm_id"]
    inport_duration[key] = 0
    outport_duration[key] = 0
    prev_pps[key] = 0.0
    prev_bps[key] = 0.0

try:
    while True:
        cur.execute("SELECT * FROM nfvvm WHERE active = 1")
        nfv_list = cur.fetchall()

        for nfv in nfv_list:
            cur.execute("SELECT * FROM logicswitch WHERE logical_dpid = %s", nfv["dpid"])

            dpid = cur.fetchone()
            port = mul_nbapi.get_switch_statistics_port(int(str(dpid["dpid"]), 0), int(nfv["in_port"]), pps_type )
            #out_port = mul_nbapi.get_switch_statistics_port(int(str(dpid["dpid"]), 0), int(nfv["out_port"]), pps_type )
            #out_port_pps = mul_nbapi.get_switch_statistics_port(int(str(dpid["dpid"]), 0), int(nfv["out_port"]), pps_type )

            print time.strftime("%Y-%m-%d %X", time.localtime()), nfv["nfv_vm_id"], ":", port.pps*8, port.bps*8

            #if port.pps > 0.0 or port.bps > 0.0:
                #print nfv["nfv_vm_id"], ":", port.pps*8, port.bps*8
                #print nfv["nfv_vm_id"], ":", in_port_pps, out_port_pps

            key = nfv["nfv_vm_id"]

            if port.pps <= 0.0:
                if prev_pps[key] != port.pps:
                    if inport_duration[key] > interval_time * 3:
                        inport_duration[key] = 0
                        prev_pps[key] = port.pps
                    else:
                        inport_duration[key] += interval_time
                        port.pps = prev_pps[key]
            else:
                prev_pps[key] = port.pps
                inport_duration[key] = 0

            if port.bps <= 0.0:
                if prev_bps[key] != port.bps:
                    if outport_duration[key] > interval_time * 3:
                        outport_duration[key] = 0
                        prev_bps[key] = port.bps
                    else:
                        outport_duration[key] += interval_time
                        port.bps = prev_bps[key]
            else:
                prev_bps[key] = port.bps
                outport_duration[key] = 0


            cur.execute("UPDATE nfvvmStatus SET in_port_pps = %s, out_port_pps = %s WHERE nfv_vm_id = %s", ((port.pps * 8), (port.bps * 8 * 1.08), nfv["nfv_vm_id"]) )
            con.commit()

            #cur.execute("SELECT * FROM nfvvmThreshold WHERE nfv_id = %s", nfv["nfv_id"])
            #threshold = cur.fetchone()
            #if port.bps * 8 >= threshold["inport_pps_threshold"] and nfv["active_threshold"] == 0:
            #    cur.execute("UPDATE nfvvm SET active_threshold = 1 WHERE nfv_vm_id = %s", key)
            #    con.commit()
            #elif port.bps * 8 < threshold["inport_pps_threshold"] and nfv["active_threshold"] == 1:
            #    cur.execute("UPDATE nfvvm SET active_threshold = 0 WHERE nfv_vm_id = %s", key)
            #    con.commit()
            del port
            #del threshold
        
        del nfv_list
        time.sleep(interval_time)
        

except Exception as err: #KeyboardInterrupt:
    print "The End", err
    exit(1)
finally:
    con.close()
