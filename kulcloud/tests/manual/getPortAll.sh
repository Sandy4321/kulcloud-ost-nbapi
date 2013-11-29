#!/bin/bash

URL=http://localhost:8181/1.0/topology/switch/0x01/port
curl -X GET -H "Content-Type: application/json" $URL
