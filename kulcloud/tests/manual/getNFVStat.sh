#!/bin/bash

URL=http://localhost:8181/1.0/NFVDB/stats/ALL
curl -X GET -H "Content-Type: application/json" $URL
