#!/bin/bash

URL=http://localhost:8181/1.0/flowtable/0x1/flow/d92e2950-ae41-4f3b-9300-225e5319b564
curl -X DELETE -H "Content-Type: application/json" $URL
