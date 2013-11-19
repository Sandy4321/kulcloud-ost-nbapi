#!/bin/bash

URL=http://localhost:8181/1.0/servicech/$1
curl -X GET -H "Content-Type: application/json" $URL
