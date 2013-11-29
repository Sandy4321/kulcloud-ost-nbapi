import kulcloud.core.v1.mul_nbapi as mul_nbapi
import MySQLdb as mdb
import MySQLdb.cursors
import time
import pdb
import requests
import json


def call_create_service(nfv_vm_id, index):
    url_front = "http://localhost:8181/1.0"
    url_back = "/servicech/sdn/mode"
    url = url_front + url_back
    response = requests.get(url)
    r = response.json()
    try:
        if r["message"] == "FAIL" or r["mode"] == "ON":
            return False
    except:
        return False
 
    try:
        con = mdb.connect("localhost", "root", "of#123", "skdemo2")
        cur = con.cursor(mdb.cursors.DictCursor)
    except:
        print "[ERROR] Fail to connect DB"
        return False

    cur.execute("SELECT nfv_id, dpid, in_port, out_port FROM nfvvm WHERE nfv_vm_id = %s", nfv_vm_id)
    nfvvm = cur.fetchone()

    cur.execute("SELECT active_threshold FROM nfvvm WHERE nfv_id = %s AND active_threshold = 0", nfvvm["nfv_id"])
    active_list = cur.fetchall()

    if not active_list:
        return False

    cur.execute("SELECT * FROM servicechainrule WHERE dpid = %s AND inport = %s AND chain_id IN (SELECT chain_id FROM servicechainrule WHERE sip = '50.1.19.14')", (nfvvm["dpid"], nfvvm["out_port"]))
    chain_list = cur.fetchall()

    url_back = "/servicech/legacy/chain"
    url = url_front + url_back
    body = dict()

    count = 0
    for chain in chain_list:
        count += 1
        if count >= len(chain_list) / 2:
            break

        body["chain_id"] = chain["chain_id"]
        body["index"] = index
        #pdb.set_trace()
        response = requests.post(url, json.dumps(body))

    cur.close()
    con.close()
    return True


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

index = 1 
change_vm = False
try:
    while True:
        cur.execute("SELECT * FROM nfvvm WHERE active = 1 ORDER BY rand()")
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

            cur.execute("SELECT * FROM nfvvmThreshold WHERE nfv_id = %s", nfv["nfv_id"])
            threshold = cur.fetchone()
            if port.bps * 8 >= threshold["inport_pps_threshold"]:
                if nfv["active_threshold"] == 0:
                    cur.execute("UPDATE nfvvm SET active_threshold = 1 WHERE nfv_vm_id = %s", key)
                    con.commit()

                if change_vm == False:
                    #pdb.set_trace()
                    if call_create_service(key, index % 4) == True:
                        index += 1
                        change_vm = True
                
            elif port.bps * 8 < threshold["inport_pps_threshold"] and nfv["active_threshold"] == 1:
                cur.execute("UPDATE nfvvm SET active_threshold = 0 WHERE nfv_vm_id = %s", key)
                con.commit()
            del port
            del threshold
        
        change_vm = False
        del nfv_list
        time.sleep(interval_time)
        

except Exception as err: #KeyboardInterrupt:
    print "The End", err
    exit(1)
finally:
    con.close()


