#!/bin/bash

URL=http://localhost:8181/1.0/servicech
curl -v -H "Content-Type: application/json" -X POST -d@createUsercommand20 $URL
