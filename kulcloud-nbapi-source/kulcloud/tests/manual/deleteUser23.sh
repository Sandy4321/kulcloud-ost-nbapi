#!/bin/bash

URL=http://localhost:8181/1.0/servicech/010-2000-3007
curl -X DELETE -H "Content-Type: application/json" $URL
