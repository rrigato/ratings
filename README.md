![Build Status](https://codebuild.us-east-1.amazonaws.com/badges?uuid=eyJlbmNyeXB0ZWREYXRhIjoiNWRzcDRZemNOTTZVM1F1ZVNZb2J6UG1ZMFdPWnRobytweG9aOE81RTgyTXlEeFg1RDcvQWFlWm96OXpQSTBBZ0VQNTFDeEJweWdtcU9ORTBYSVRGTmQ4PSIsIml2UGFyYW1ldGVyU3BlYyI6IjRIRExOZk5ZRnFZdFdRVE0iLCJtYXRlcmlhbFNldFNlcmlhbCI6MX0%3D&branch=master) ![Python 3.7](https://img.shields.io/badge/python-3.7-blue.svg)

# ratings

This application creates a lambda function that polls the reddit api to retrieve television ratings. The ratings are then parsed from an html table element and inserted into dynamodb. 


## table_of_contents


- [ratings](#ratings)
  - [table_of_contents](#table_of_contents)
    - [dev_tools](#dev_tools)
      - [detect_secrets](#detect_secrets)
      - [git_secrets](#git_secrets)
    - [project_directory_overview](#project_directory_overview)
      - [builds](#builds)
      - [devops](#devops)
      - [historical](#historical)
      - [scripts](#scripts)
      - [integration-tests](#integration-tests)
        - [util](#util)
  - [run_locally](#run_locally)
  - [unit-tests](#unit-tests)





### dev_tools

The goal of these dev tools is to build security checks into the CI/CD pipeline so that controls are put into place without manual intervention by the developer.

Follow [this aws example](https://forums.aws.amazon.com/thread.jspa?threadID=228206) on how to have multiple rsa key pairs in the same local machine being used with different accounts.


#### detect_secrets
[detect-secrets](https://github.com/Yelp/detect-secrets) is a python library that performs static code analysis to ensure no secrets have entered your code base.

A detect-secrets scan is run as part of the dev CI build to ensure no secrets are promoted to prod. 

```bash
#creates/updates baseline of vulnerabilities 
# to review false positives

detect-secrets scan > .secrets.baseline
```

```bash
detect-secrets scan

detect-secrets scan | \
python3 -c "import sys, json; print(json.load(sys.stdin)['results'])"
```


.secrets.baseline = reviewed to only have false postives 

#### git_secrets

[git secrets](https://github.com/awslabs/git-secrets.git) is a command line utility for validating that you do not have any git credentials stored in your git repo commit history



- Global install

```
    git init

    git remote add origin https://github.com/awslabs/git-secrets.git

    git fetch origin

    git merge origin/master

    sudo make install
```

- Web Hook install

Configuring git secrets as a web hook will ensure that git secrets runs on every commit, scanning for credentials
```
    cd ~/Documents/devdocs

    git secrets --install

    git secrets --register-aws
```


Allow the sample lambda cloudwatch event since it uses a fake 
account
```bash
    git config --add secrets.allowed "util/lambda_cw_event.json"
```

- Run a git secrets check recursively on all files in directory

```bash
# git ls-files are scanned by default

git secrets --scan 
```


### project_directory_overview
Provides information on each directory/ source file

#### builds


- buildspec_dev_backend.yml = Creates templates/ratings_backend.yml
and Tests backend ratings logic

- buildspec_prod.yml = updates and invokes prod lambda functions for polling reddit api and backing up dynamodb



#### devops

ci.sh = miscellaneous awscli commands to configure environment



#### historical
- ratings_05262012_to_05272017.json = ratings from May 26th, 2012 until May 27th 2017, credit to these historical ratings [from this source](https://github.com/FOSSforlife/toonami_ratings)
  
- ratings_11102018_04112020.json = ratings from November 10th 2018 through April 11th 2020, source was the reddit api


#### scripts
- adhoc_item_update.py = Script to perform ad-hoc updates of all items in 
  the dynamodb table at once (data quality)
  
- historical_ratings_upload.py = one time upload of json from the [historical](#historical) directory

- reddit_ratings.py = api call to reddit to get television ratings and transform for upload into dynamodb

- backup_dynamodb_ratings.py = Runs monthly to backup dynamodb table and validate that new ratings were inserted in the last month


#### integration-tests


- test_dev_ratings_backend.py = end-to-end dev tests used by 
  - builds/buildspec_dev_backend.yml

- test_prod_ratings_backend.py = end-to-end prod validation used by
  - builds/buildspec_prod.yml

- test_reddit_ratings.py = local integration tests



##### util

- news_flair_fixture.json = reddit response with posts that have a news flair for unit testing
  
- reddit_search_response.json = Reddit search api json response using the
following api query:
https://oauth.reddit.com/r/toonami/search.json?limit=25&q=flair:news&sort=new&restrict_sr=on&t=all&raw_json=1&after=t3_a19qyq

- test_reddit_rating_config.py = fixtures for use in tests/test_reddit_rating.py


## run_locally

```scripts.reddit_ratings``` = To run locally you need the ```AWS_LAMBDA_FUNCTION_NAME``` and ```BUILD_ENVIRONMENT``` variables


## unit-tests
```bash
python -m unittest
```