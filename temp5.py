import MySQLdb as mdb
import MySQLdb.cursors
import kulcloud.core.v1.mul_nbapi as mul_nbapi

with mdb.connect("localhost", "root", "of#123", "test", cursorclass=MySQLdb.cursors.DictCursor) as cur:
    cur.execute("SELECT * FROM nfvvm")
    rows = cur.fetchall()

for row in rows:
    print row
    str_dpid = str(row['dpid'])
    switch_stat = mul_nbapi.get_switch_statistics_port(int(str_dpid, 0), 0, 1)

    print switch_stat

    if switch_stat is None:
        print "what"
    if not switch_stat: 
        print "the"
    break
