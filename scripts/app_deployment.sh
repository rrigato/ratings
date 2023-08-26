#! /bin/bash

#exits program immediately if a command is not sucessful
set -e


secret_scan_results=$(detect-secrets scan | \
python3 -c "import sys, json; print(json.load(sys.stdin)['results'])" )

# static scan for security credentials that terminates if any secrets are found
if [ "${secret_scan_results}" != "{}" ]; then
    echo "detect-secrets scan failed"
    exit 125
fi

python -m unittest


pip install --target ./deployment \
-r requirements/requirements-bundle.txt


cp -r ratings deployment
cp scripts/reddit_ratings.py deployment

cd deployment

zip -r9 built_lambda.zip . \
-x *__pycache__* --quiet

cd ..


echo "---------------completed handler update---------------------"

#cleanup
rm -r deployment

git push origin dev

echo "---------------deployment complete----------------"