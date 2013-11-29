#!/bin/bash

URL=http://localhost:8181/1.0/NFVDB/stats/$1/$2
curl -X GET -H "Content-Type: application/json" $URL
