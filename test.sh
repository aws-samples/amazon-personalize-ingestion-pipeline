#!/bin/bash

INTERACTION_URL=$(aws cloudformation describe-stacks --stack-name personalize-retail-ingest-solution \
 		--query 'Stacks[0].Outputs[?OutputKey==`InteractionApiURL`].OutputValue' \
 		--output text \
 		--region eu-west-1)


http POST  $INTERACTION_URL userId=123 itemId=441231 type=impression


API_URL=$(aws cloudformation describe-stacks --stack-name personalize-retail-ingest-solution \
 		--query 'Stacks[0].Outputs[?OutputKey==`PersonalizationApiURL`].OutputValue' \
 		--output text \
 		--region eu-west-1)

USER_ID=123
RECOMMENDATION_SUFFIX=recommendation/

http $API_URL$RECOMMENDATION_SUFFIX$USER_ID

HISTORY_SUFFIX=history/

http $API_URL$HISTORY_SUFFIX$USER_ID