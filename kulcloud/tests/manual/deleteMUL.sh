#!/bin/bash

URL=http://localhost:8182/1.0/servicech/log/0x00237d2948f4/4/50.1.19.12
curl -X DELETE -H "Content-Type: application/json" $URL
