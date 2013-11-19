import MySQLdb as mdb

def what(conf):
    con = mdb.connect('localhost', 'root', 'z2028757', 'skdemo')
    cur = con.cursor(mdb.cursors.DictCursor)

    con.close()

what(0)
print "what"
