#!/bin/bash

URL=http://localhost:8181/1.0/servicech/ALL
curl -X DELETE -H "Content-Type: application/json" $URL
