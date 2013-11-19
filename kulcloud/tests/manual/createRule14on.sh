#!/bin/bash
#URL=http://localhost:8181/1.0/servicech/010-2000-3003/services/VIDEO
#curl -v -H "Content-Type: application/json" -X POST -d@createRulecommand $URL
URL=http://localhost:8181/1.0/servicech/010-2000-3003/services/NAVER
curl -v -H "Content-Type: application/json" -X POST -d@createRulecommandon $URL
URL=http://localhost:8181/1.0/servicech/010-2000-3003/services/DAUM
curl -v -H "Content-Type: application/json" -X POST -d@createRulecommandon $URL
