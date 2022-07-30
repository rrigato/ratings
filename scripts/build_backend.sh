#! /bin/bash

#exits program immediately if a command is not sucessful
set -e

LAMBDA_FUNCTION_NAME="prod-ratings-backend-lambda-poll"

pip install --target ./deployment requests
pip install --target ./deployment bs4

cp -r ratings deployment
cp scripts/reddit_ratings.py deployment

cd deployment

zip -r9 built_lambda.zip .

cd ..


aws lambda update-function-code --region us-east-1 \
--function-name $LAMBDA_FUNCTION_NAME \
--zip-file fileb://deployment/built_lambda.zip

aws lambda update-function-configuration --region us-east-1 \
--function-name $LAMBDA_FUNCTION_NAME \
--handler "reddit_ratings.lambda_handler" \
--no-cli-pager
