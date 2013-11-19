#!/bin/bash

URL=http://localhost:8181/1.0/NFVDB
curl -X GET -H "Content-Type: application/json" $URL
