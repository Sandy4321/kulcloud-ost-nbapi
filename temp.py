import sys
sys.path.append("/usr/src/kulcloud-nbapi/lib/python2.7/site-packages/sqlalchemy/dialects/mysql")
import mysqldb as mdb
def create_default_rule(conf, body):
    result = {}

    try:
        con = mdb.connect('localhost', 'root', 'z2028757', 'skdemo')
        cur = con.cursor(mdb.cursors.DictCursor)
    except:
        print "[ERROR] DB Connection Fail"

    try:
        #Delete Past All Default Rule
        cur.execute("SELECT nfv FROM defaultRule LIMIT 1")
        row = cur.fetchone()
        if not row:
            pass
        else:
            cur.execute("DELETE FROM defaultRule")
        
        #Update defaultRule Table at DataBase
        rule_list = body['nfv_list']
        nfv_num = 1
        for rule in rule_list:
            cur.execute("SELECT nfv FROM nfv WHERE nfv = %s", rule)
            row = cur.fetchone()
            if not row:
                print "[ERROR] : bad input - There is no nfv name"
                result['message'] = "FAIL"
                return result

            cur.execute("INSERT INTO defaultRule (nfv_order, nfv) VALUES (%s, %s)", (nfv_num, row['nfv']))
            nfv_num = nfv_num + 1

        con.commit()
        result['message'] = "SUCCESS"
    except Exception as err:
        print "rollback : "
        print err
        con.rollback()
        result['message'] = "FAIL"

    con.close()
    return result

def apply_default_rule_for_user(conf):
    
    result = dict()
    try:
        con = mdb.connect('localhost', 'root', 'z2028757', 'skdemo')
        cur = con.cursor(mdb.cursors.DictCursor)
    except:
        print "[ERROR] DB connect Fail"
        result['message'] = "FAIL"
        return result

    cur.execute("SELECT a.nfv, nfvvm.dpid, nfvvm.in_port, nfvvm.out_port, nfvvm.vlan FROM defaultRult as a, nfv, nfvvm WHERE a.nfv = nfv.nfv AND nfv.nfv_id = nfvvm.nfv_id")
    defaultRule_list = cur.fetchall()
    cur.execute("SELECT * FROM sa")
    service_list = cur.fetchall()

    dRule_iter = defaultRule_list.__iter__()
    path_list = list()
    for service in service_list:
        start_path = dict()







result = apply_default_rule_for_user(0)
print result
