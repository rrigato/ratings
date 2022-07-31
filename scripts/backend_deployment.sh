#! /bin/bash

#exits program immediately if a command is not sucessful
set -e

LAMBDA_FUNCTION_NAME="prod-ratings-backend-lambda-poll"

secret_scan_results=$(detect-secrets scan | \
python3 -c "import sys, json; print(json.load(sys.stdin)['results'])" )

# static scan for security credentials that terminates if any secrets are found
if [ "${secret_scan_results}" != "{}" ]; then
    echo "detect-secrets scan failed"
    exit 125
fi

python -m unittest -k tests.test_ratings


pip install --target ./deployment requests
pip install --target ./deployment bs4

cp -r ratings deployment
cp scripts/reddit_ratings.py deployment

cd deployment

zip -r9 built_lambda.zip . \
-x *__pycache__* --quiet

cd ..



aws lambda update-function-configuration --region us-east-1 \
--function-name $LAMBDA_FUNCTION_NAME \
--no-cli-pager \
--handler "reddit_ratings.lambda_handler" 

echo "---------------completed handler update---------------------"

aws lambda update-function-code --region us-east-1 \
--function-name $LAMBDA_FUNCTION_NAME \
--no-cli-pager \
--zip-file fileb://deployment/built_lambda.zip

#cleanup
rm -r deployment

git push origin master

echo "---------------deployment complete----------------"