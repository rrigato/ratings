![Build Status](https://codebuild.us-east-1.amazonaws.com/badges?uuid=eyJlbmNyeXB0ZWREYXRhIjoiNWRzcDRZemNOTTZVM1F1ZVNZb2J6UG1ZMFdPWnRobytweG9aOE81RTgyTXlEeFg1RDcvQWFlWm96OXpQSTBBZ0VQNTFDeEJweWdtcU9ORTBYSVRGTmQ4PSIsIml2UGFyYW1ldGVyU3BlYyI6IjRIRExOZk5ZRnFZdFdRVE0iLCJtYXRlcmlhbFNldFNlcmlhbCI6MX0%3D&branch=master) ![Python 3.7](https://img.shields.io/badge/python-3.7-blue.svg)

#ratings

This application creates a lambda function that polls the reddit api to retrieve television ratings. The ratings are then parsed from an html table element and inserted into dynamodb.



## table_of_contents


- [table_of_contents](#table_of_contents)
  - [dev_tools](#dev_tools)
    - [cfn_lint](#cfn_lint)
    - [detect_secrets](#detect_secrets)
    - [git_secrets](#git_secrets)
  - [project_directory_overview](#project_directory_overview)
    - [builds](#builds)
      - [builds](#builds-1)
    - [devops](#devops)
    - [dynamodb_erd](#dynamodb_erd)
    - [historical](#historical)
    - [logs](#logs)
    - [scripts](#scripts)
    - [templates](#templates)
    - [tests](#tests)
      - [util](#util)
    - [setup_ci](#setup_ci)





### dev_tools

The goal of these dev tools is to build security checks into the CI/CD pipeline so that controls are put into place without manual intervention by the developer.

Follow [this aws example](https://forums.aws.amazon.com/thread.jspa?threadID=228206) on how to have multiple rsa key pairs in the same local machine being used with different accounts.

#### cfn_lint
[cfn-lint](https://github.com/aws-cloudformation/cfn-python-lint.git) Provides yaml/json cloudformation validation and checks for best practices

- Install

```
    pip install cfn-lint
```

- Run on a file
```
    cfn-lint <filename.yml>

    cfn-lint templates/code_pipeline.yml
```

- Run on all files in Directory
```
    cfn-lint templates/*.yml
```

#### detect_secrets
[detect-secrets](https://github.com/Yelp/detect-secrets) is a python library that performs static code analysis to ensure no secrets have entered your code base.

A detect-secrets scan is run as part of the dev CI build to ensure no secrets are promoted to prod. This enables security to be built into the application ci/cd platform and is recursive by default

```
#detect secrets in tracked git files

detect-secrets scan .
```

```
#detect secrets for all files in cwd

detect-secrets scan --all-files .
```


#### git_secrets

[git secrets](https://github.com/awslabs/git-secrets.git) is a command line utility for validating that you do not have any git credentials stored in your git repo commit history

This is useful for not only open source projects, but also to make sure best practices are being followed with limited duration credentials (IAM roles) instead of long term access keys

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
```
    git config --add secrets.allowed "util/lambda_cw_event.json"
```

- Run a git secrets check recursively on all files in directory

```
git secrets --scan -r .
```


### project_directory_overview
Provides information on each directory/ source file

#### builds


- buildspec_dev_backend.yml = Creates templates/ratings_backend.yml
and Tests backend ratings logic




##### builds

- buildspec_dev.yml = Buildspec to use for the development (QA)
    CodeBuild project

- buildspec_prod.yml = Buildspec to use for the prod deployment CodeBuild project

#### devops

ci.sh = miscellaneous awscli commands to configure environment

#### dynamodb_erd
prod_ratings.json = Entity relationship diagram built using [NoSQL Workbench for DynamoDB](https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/workbench.html). Helps model access patterns before implementation


#### historical
- ratings_05262012_to_05272017.json = ratings from May 26th, 2012 until May 27th 2017, credit to these historical ratings [from this source](https://github.com/FOSSforlife/toonami_ratings)
  
- ratings_11102018_04112020.json = ratings from November 10th 2018 through April 11th 2020, source was the reddit api

#### logs
- directory for python log files

#### scripts
- adhoc_item_update.py = Script to perform ad-hoc updates of all items in 
  the dynamodb table at once (data quality)
  
- historical_ratings_upload.py = one time upload of json from the [historical](#historical) directory

- reddit_ratings.py = api call to reddit to get television ratings and transform for upload into dynamodb

- backup_dynamodb_ratings.py = Runs monthly to backup dynamodb table and validate that new ratings were inserted in the last month

#### templates

- code_pipeline.yml = Creates CodeBuild/Code Pipeline resources
    necessary for Dev/Prod

- ratings_backend.yml = Creates the backend storage and compute necessary for
updating ratings

#### tests

- test_dev_ratings_backend.py = tests backend dynamodb/lamdba aws resources

- test_reddit_ratings.py = tests logic for making api call to
return television ratings


##### util
- lambda_cw_event.json = lambda cloudwatch invokation event json

- news_flair_fixture.json = reddit response with posts that have a news flair for unit testing
  
- reddit_search_response.json = Reddit search api json response using the
following api query:
https://oauth.reddit.com/r/toonami/search.json?limit=25&q=flair:news&sort=new&restrict_sr=on&t=all&raw_json=1&after=t3_a19qyq

- test_reddit_rating_config.py = fixtures for use in tests/test_reddit_rating.py

#### setup_ci

Add the remote repo using the following:
```
git init

git remote add origin <origin_url_or_ssh>

```


Fetch origin repo locally and merge if the remote

has any references you do not

```
    git fetch origin

    git merge origin/<branch_name>
```



