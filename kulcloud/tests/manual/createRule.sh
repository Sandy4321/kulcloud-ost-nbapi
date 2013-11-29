#!/bin/bash

URL=http://localhost:8181/1.0/servicech/010-0000-0151/services/$1
curl -v -H "Content-Type: application/json" -X POST -d@createRulecommand $URL
