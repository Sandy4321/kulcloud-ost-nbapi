#!/bin/bash

URL=http://localhost:8181/1.0/flowtable/0x1/flow
curl -v -H "Content-Type: application/json" -X POST -d@createFlowcommand$1 $URL
