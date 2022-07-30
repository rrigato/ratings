#! /bin/bash

#exits program immediately if a command is not sucessful
set -e

pip install --target ./deployment requests
pip install --target ./deployment bs4

cp -r ratings deploypkg
cp scripts/reddit_ratings.py deploypkg

cd deployment

zip -r9 built_lambda.zip .

cd ..
