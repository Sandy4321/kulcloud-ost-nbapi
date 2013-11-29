#!/bin/bash

URL=http://localhost:8181/1.0/servicech/default/rule
curl -v -H "Content-Type: application/json" -X POST -d@createDefaultRulecommand $URL
