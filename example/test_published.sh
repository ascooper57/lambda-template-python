#!/bin/bash

HOSTNAME=r1gzxipb32
curl -H "Content-Type: application/json" -X PUT -d '{"index_key_example": 1,"integer_example": 0,"datetime_example": "2012-07-09T22:27:50+00:00","text_example": "Text","decimal_example": 0.0,"boolean_example": true}' "https://${HOSTNAME}.execute-api.us-east-1.amazonaws.com/v1/generated"
open https://${HOSTNAME}.execute-api.us-east-1.amazonaws.com/v1/generated?index_key_example=1

#!/bin/bash
for i in {1..100}
do
   sleep 1
   curl https://${HOSTNAME}.execute-api.us-east-1.amazonaws.com/v1/health    > /dev/null 2>&1
   curl https://${HOSTNAME}.execute-api.us-east-1.amazonaws.com/v1/generated?index_key_example=1 > /dev/null 2>&1
done
