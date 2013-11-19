#!/usr/bin/env python

import libvirt
import sys
import os
import libxml2
import pdb
import time
import json
import kulcloud.core.v1.mul_nbapi as mul_nbapi
import kulcloud.core.v1.mlapi as mlapi
import MySQLdb as mdb

def usage():
    print 'Usage: %s' % sys.argv[0]

def print_section(title):
    print "\n%s" % title
    print "=" * 60

def print_entry(key, value):
    print "%-10s %-10s" % (key, value)

def get_domains(conn):
    try:
        domainIDs = conn.listDomainsID()
        domains = len(domainIDs) * [None]
        for i in range(len(domainIDs)):
            domains[i] = conn.lookupByID(domainIDs[i])
            
        # Annoyiingly, libvirt prints its own error message here
    except libvirt.libvirtError:
        print "Error reading libvirt Domains"
        sys.exit(0)
    return domains

def collect_stats(domains):
    system_times = len(domains) * [0.0]
    cpu_times = len(domains) * [0.0]
    for i in range(len(domains)):
        system_times[i] = time.time()
        try:
            cpu_times[i] = domains[i].info()[4]
        except libvirt.libvirtError:
            cpu_times[i] = -1
    return system_times, cpu_times



filepath = "/var/www/vm_stats.json"
# Connect to libvirt
conn = libvirt.openReadOnly(None)
if conn == None:
    print 'Failed to open connection to the hypervisor'
    sys.exit(1)

update_interval = 1.0
measure_interval = 1.0
nr_cores = 8
#pdb.set_trace()
output = {}
mlapi_instance = mlapi.mlapi()

try:
    con = mdb.connect('localhost', 'root', 'z2028757', 'skdemo')
    cur = con.cursor(mdb.cursors.DictCursor)
except:
    print "[ERROR] failed connecting to DB"
    exit(1)

# Main loop
while True :
    domains = get_domains(conn)
    system_times_prev, cpu_times_prev = collect_stats(domains)
    time.sleep(measure_interval)
    system_times_new, cpu_times_new = collect_stats(domains)
    
    """cpu_usage check"""
    cpu_stat_list = []
    output = {}
    for i in range(len(domains)):
        cpu_stat = {}
        if (cpu_times_new[i] > 0.0):
            cpu_stat['name'] = domains[i].name()
            cpu_stat['cpuusage'] =  100 * (cpu_times_new[i] - cpu_times_prev[i]) / ( (system_times_new[i] - system_times_prev[i]) * nr_cores * 1000000000)
        name = cpu_stat['name']
        cpu_stat_list.append(cpu_stat)
    output['cpu_usage'] = cpu_stat_list

    for stat in cpu_stat_list:
        cur.execute("SELECT nfv_vm_id,dpid,in_port,out_port FROM nfvvm WHERE nfv_name = %s", (stat['name']))
        row = cur.fetchone()
        
        if not row:
            print "[WARING] : This vm_name (%s)  is not found - libvirt" % stat['name']
            exit(1)
        
        inport_traffic = mlapi_instance.get_stat_port(0, row['dpid'], row['in_port'])
        outport_traffic = mlapi_instance.get_stat_port(0, row['dpid'], row['out_port'])

        curr_time = time.strftime("%Y-%m-%d %X", time.localtime() )
        try:
            in_port_pps = inport_traffic['ingress']['avg_pps']
            out_port_pps = outport_traffic['egress']['avg_pps']
            cpu_usage = int( round(stat['cpuusage']) )
            curr_time = time.strftime("%Y-%m-%d %X", time.localtime() )
        except Exception as err:
            #print ("[ERROR] : " + str(err) + curr_time)
            print ("[ERROR] : Failed to get the switch statistics -- " + curr_time)
            print ("Fail update db... retry...")
            continue
        
        try:
            cur.execute("UPDATE nfvvmStatus SET in_port_pps = %s, out_port_pps = %s, cpu_usage = %s, time = %s WHERE nfv_vm_id = %s", (in_port_pps, out_port_pps, cpu_usage, curr_time, row['nfv_vm_id']))
            #debug = {'nfv_vm_id':row['nfv_vm_id'], 'cpu_usage':cpu_usage}
            #print debug
            con.commit()
        except:    
            print "[WARNING] : DB nfvvmStatus Update fail - libvirt"
            con.rollback()


#    for stat in cpu_stat_list:
#        cur.execute("SELECT * FROM nfvvm WHERE nfv_name = %s", stat["name"])
#        row = cur.fetchone()
#
#        if not row:
#            print "[ERROR] cannot find service name from DB"
#            exit(1)

    
    #file = open(filepath,"w")
    #file.write(json.dumps(output))
    #file.close()
    time.sleep(update_interval)
    
