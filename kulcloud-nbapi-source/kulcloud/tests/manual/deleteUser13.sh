#!/bin/bash

URL=http://localhost:8182/1.0/servicech/010-2000-3002
curl -X DELETE -H "Content-Type: application/json" $URL
