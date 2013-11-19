#!/bin/bash

URL=http://localhost:8181/1.0/topology/switch/0x02/port/1
curl -X GET -H "Content-Type: application/json" $URL
