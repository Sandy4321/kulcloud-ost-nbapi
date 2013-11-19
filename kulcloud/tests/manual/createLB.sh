#!/bin/bash

URL=http://localhost:8181/1.0/NFVDB/LB/$1
curl -v -H "Content-Type: application/json" -X POST -d@createLBcommand $URL
