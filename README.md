![Build Status]() ![Python 3.7](https://img.shields.io/badge/python-3.7-blue.svg)


### CloudFormation Limitations


#### DeletionPolicy attribute must be string
[According to this forum post](https://forums.aws.amazon.com/message.jspa?messageID=560586)
The DeletionPolicy must be a string, this limits flexibility when trying to pass it as a parameter dependent on environment...

### Development Tooling Overview

Followed [this aws example](https://forums.aws.amazon.com/thread.jspa?threadID=228206) on how to have multiple rsa key pairs in the same local machine being used with different accounts

#### cfn-lint (cloudformation Linting)
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


#### Git Secrets Scan

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


### Project Directory Overview
Provides information on each directory/ source file

#### builds


- buildspec_dev_backend.yml = Creates templates/ratings_backend.yml
and Tests backend ratings logic




##### Buildspec Files
- buildspec_dev.yml = Buildspec to use for the development (QA)
    CodeBuild project

- buildspec_prod.yml = Buildspec to use for the prod deployment CodeBuild project

#### docs


#### devops

ci.sh = miscellaneous awscli commands to configure environment

#### logs
- directory for python log files





#### templates



- code_pipeline.yml = Creates CodeBuild/Code Pipeline resources
    necessary for Dev/Prod

- ratings_backend.yml = Creates the backend storage and compute necessary for
updating ratings

- ratings_update_lambda.yml = Lambda function that updates dynamodb table from
  templates/ratings_backend.yml

#### tests

- test_dev_aws_resources.py = tests dev website

- test_dev_ratings_backend.py = tests backend resources for storing
calling televison ratings api

- test_reddit_ratings.py = tests logic for making api call to
return television ratings


##### util
- reddit_search_response.json = Reddit search api json response using the
following api query:
https://oauth.reddit.com/r/toonami/search.json?limit=25&q=flair:news&sort=new&restrict_sr=on&t=all&raw_json=1&after=t3_a19qyq


#### Setup Continuous Integration

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



#### Setup Infrastructure
