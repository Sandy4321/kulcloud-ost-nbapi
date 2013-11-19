import kulcloud.core.v1.mul_nbapi as mul_nbapi
import MySQLdb as mdb

con = mdb.connect("localhost", "root", "of#123", "skdemo")
cur = con.cursor(mdb.cursors.DictCursor)

port_no = 5
dpid = "0xac162dbbc2fe"
cur.execute("SELECT * FROM servicechainrule WHERE dpid = %s AND inport = %s", (dpid, port_no))
inport_list = cur.fetchall()

print inport_list

for row in inport_list:
    flow = mul_nbapi.nbapi_flow_make_flow(row['sip'], row['dip'], int(port_no), int(row['vlan']), 0x0800, 0, 0, None, None, 0, 0, 0)
    stats = mul_nbapi.get_flow_statistics(int(str(dpid), 0), flow, row['wildcard'], row['outport'], int(row['prior']))

    #print stats
    if stats is None:
        print None
    else:
        print mul_nbapi.nbapi_parse_pps_to_str(stats.pps)

    
