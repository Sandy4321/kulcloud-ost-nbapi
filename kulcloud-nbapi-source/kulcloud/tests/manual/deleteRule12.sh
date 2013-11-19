#!/bin/bash

URL=http://localhost:8181/1.0/servicech/log/0x00237d2948f4/3/50.1.19.21
curl -X DELETE -H "Content-Type: application/json" $URL
