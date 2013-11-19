import requests
import sys

url = "http://localhost:8181/1.0/SADB/test/vm_map"

r = requests.get(url)

print r
what = r.json()


print what[sys.argv[1]]
