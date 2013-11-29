import kulcloud.core.v1.mul_nbapi as mul_nbapi
import MySQLdb as mdb
import MySQLdb.cursors
import time
import pdb
import random

interval_time = 1
pps_type = 0

try:
    con = mdb.connect("localhost", "root", "of#123", "skdemo2")
    cur = con.cursor(mdb.cursors.DictCursor)
except:
    exit(1)

    inport_duration = 0
    outport_duration = 0
try:
    prev_pps = 0.0
    while True:
        cur.execute("SELECT * FROM nfvvm WHERE active = 1")
        nfv_list = cur.fetchall()

        for nfv in nfv_list:
            cur.execute("SELECT * FROM logicswitch WHERE logical_dpid = %s", nfv["dpid"])

            dpid = cur.fetchone()
            port = mul_nbapi.get_switch_statistics_port(int(str(dpid["dpid"]), 0), int(nfv["in_port"]), pps_type )
            print nfv["nfv_vm_id"], ":", port.pps, port.bps

            #if nfv["nfv_vm_id"] == 1 or nfv["nfv_vm_id"] == 2 or nfv["nfv_vm_id"] == 9:
            #    port.pps = 600000
            #    port.bps = 700000
            #out_port_pps = mul_nbapi.get_switch_statistics_port(int(str(dpid["dpid"]), 0), int(nfv["out_port"]), pps_type )
            #if nfv["nfv_vm_id"] == 10 or nfv["nfv_vm_id"] == 18 or nfv["nfv_vm_id"] == 19:#port.pps > 0.0 or port.bps > 0.0:
                #print nfv["nfv_vm_id"], ":", port.pps, port.bps
                #print nfv["nfv_vm_id"], ":", in_port_pps, out_port_pps
            """
            if nfv["nfv_vm_id"] >=9 and nfv["nfv_vm_id"] <= 16:
                #port.pps = random.uniform(1000000, 7000000)
                #port.bps = random.uniform(500000, 9000000)
                port.pps = 1024 * 1024 * 8
                port.bps = 1024 * 1024 * 7
            if nfv["nfv_vm_id"] >= 1 and nfv["nfv_vm_id"] <= 8:
                port.pps = 1024 * 1024 * 4
                port.bps = 1024 * 1024 * 10
            """
            if port.pps <= 0.0:
                if prev_pps != port.pps:
                    if inport_duration > 4:
                        inport_duration = 0
                        prev_pps = 0
                    else:
                        inport_duration += interval_time
                        port.pps = prev_pps
            cur.execute("UPDATE nfvvmStatus SET in_port_pps = %s, out_port_pps = %s WHERE nfv_vm_id = %s", ((port.pps * 8), (port.bps * 8), nfv["nfv_vm_id"]) )
            con.commit()
        time.sleep(interval_time)
        

except Exception as err: #KeyboardInterrupt:
    print "The End", err
    exit(1)
finally:
    con.close()
