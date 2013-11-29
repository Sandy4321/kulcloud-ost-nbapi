#!/usr/bin/env python

import sys
import libxml2
import pdb
import time
import json
import MySQLdb as mdb
import MySQLdb.cursors

update_interval = 2.0
duration_interval = int(update_interval)
#cpu_check_duration = dict()
#pps_check_duration = dict()
non_used_duration = dict()

try:
    con = mdb.connect("localhost", "root", "of#123", "skdemo2", cursorclass=MySQLdb.cursors.DictCursor)
except:
    print "[ERROR] Failed connecting to DB :"
    exit(1)

with con as cur:
    cur.execute("SELECT nfv_vm_id FROM nfvvm")
    nfvvm_list = cur.fetchall()

for nfvvm in nfvvm_list:
    #cpu_check_duration[nfvvm["nfv_vm_id"]] = 0
    #pps_check_duration[nfvvm["nfv_vm_id"]] = 0
    non_used_duration[nfvvm["nfv_vm_id"]] = 0
vm1_key_list = [1,3,5,7]

while True:
    with con as cur:
        cur.execute("SELECT c.nfv_id, b.nfv_vm_id, a.cpu_usage_threshold, a.cpu_usage_duration, a.inport_pps_threshold, a.inport_pps_duration, d.in_port_pps, d.out_port_pps, d.cpu_usage, b.active_threshold FROM nfvvmThreshold as a, nfvvm as b, nfv as c, nfvvmStatus as d WHERE a.nfv_id = b.nfv_id AND b.nfv_id = c.nfv_id AND c.type = 'virtual' AND d.nfv_vm_id = b.nfv_vm_id AND b.active = 1")
        threshold_list = cur.fetchall()
    
    active_on_threshold_list = [threshold for threshold in threshold_list if threshold["active_threshold"] == 0]
    active_off_threshold_list = [threshold for threshold in threshold_list if threshold["active_threshold"] == 1]
   
    over_threshold = 0
    for threshold in active_on_threshold_list:
        key = threshold["nfv_vm_id"]
        print key, " : ", threshold["out_port_pps"], " : ", threshold["inport_pps_threshold"], " : ", non_used_duration[key]
        
        cur.execute("SELECT nfv_vm_id FROM nfvvm WHERE nfv_id = %s AND active = 1", threshold["nfv_id"])
        rows = cur.fetchall()

        #if non_used_duration[key] >= threshold["inport_pps_duration"]:
            #print "[EVENT] nfv_vm_id : %s = This vm is disable, because not used"
        """
            with con as cur:
                cur.execute("UPDATE nfvvm SET active = 0 WHERE nfv_vm_id = %s", key)
                con.commit()
            non_used_duration[key] = 0
        """
        if threshold["out_port_pps"] >= threshold["inport_pps_threshold"]:
            over_threshold += 1
            if over_threshold == len(rows):
            
                with con as cur:
                    cur.execute("SELECT nfv_vm_id FROM nfvvm WHERE active = 0 AND nfv_id = %s ORDER BY nfv_vm_id LIMIT 1", threshold["nfv_id"])
                    nfvvm = cur.fetchone()
            
                """ enable virtual machine one more """
                if not nfvvm:
                    pass
                else:
                    print "[EVENT] nfvvm_id : %s = will enable" % nfvvm["nfv_vm_id"]
                    with con as cur:
                        cur.execute("UPDATE nfvvm SET active = 1 WHERE nfv_vm_id = %s", nfvvm["nfv_vm_id"])
                        con.commit()
            
            """ threshold disable """
            print "[EVENT] nfvvm_id : %s = will deselectable when cpu usage drop to normal" % (threshold["nfv_vm_id"])
            with con as cur:
                cur.execute("UPDATE nfvvm SET active_threshold = 1 WHERE nfv_vm_id = %s", key)
                con.commit()
            
            continue

        if key in vm1_key_list:
            pass
        else:
            if threshold["out_port_pps"] == 0:
                non_used_duration[key] += 1
            else:
                if non_used_duration[key] > 0:
                    non_used_duration[key] -= 1


    for threshold in active_off_threshold_list:
        key = threshold["nfv_vm_id"]

        print key, " : ", threshold["out_port_pps"], " : ", threshold["inport_pps_threshold"], " : ", non_used_duration[key]

        if threshold["out_port_pps"] <= threshold["inport_pps_threshold"]:
            print "[EVENT] %s nfvvm now selectable because cpu usage droped to normal" % (key)
            with con as cur:
                cur.execute("UPDATE nfvvm SET active_threshold = 0 WHERE nfv_vm_id = %s", key)
                con.commit()

        #if threshold["out_port_pps"] > threshold["inport_pps_threshold"]:
            
    print ""  
    time.sleep(update_interval)

con.close()            
