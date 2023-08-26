![Python 3.9](https://img.shields.io/badge/python-3.9-blue.svg)

# archival
- Effective 2023-08-27 I archived this project, might revisit in the future but the upstream television ratings sources were too inconsistent to reliably pull the required data.
  

# ratings

This application creates a lambda function that polls the reddit api to retrieve television ratings. The ratings are then parsed from an html table element and inserted into dynamodb. 


## table_of_contents


- [archival](#archival)
- [ratings](#ratings)
  - [table\_of\_contents](#table_of_contents)
    - [dev\_tools](#dev_tools)
      - [detect\_secrets](#detect_secrets)
      - [git\_secrets](#git_secrets)
      - [historical](#historical)
  - [scripts](#scripts)
  - [run\_locally](#run_locally)
  - [unit-tests](#unit-tests)
    - [integration-tests](#integration-tests)
  - [known-issues](#known-issues)





### dev_tools

The goal of these dev tools is to build security checks into the CI/CD pipeline so that controls are put into place without manual intervention by the developer.



#### detect_secrets
[detect-secrets](https://github.com/Yelp/detect-secrets) is a python library that performs static code analysis to ensure no secrets have entered your code base.


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
    git secrets --install

    git secrets --register-aws
```



- Run a git secrets check recursively on all files in directory

```bash
# git ls-files are scanned by default

git secrets --scan 
```






#### historical
- ratings_05262012_to_05272017.json = ratings from May 26th, 2012 until May 27th 2017, credit to these historical ratings [from this source](https://github.com/FOSSforlife/toonami_ratings)
  
- ratings_11102018_04112020.json = ratings from November 10th 2018 through April 11th 2020, source was the reddit api


## scripts
- adhoc_item_update.py = Script to perform ad-hoc updates of all items in 
  the dynamodb table at once (data quality)
  
- historical_ratings_upload.py = one time upload of json from the [historical](#historical) directory



## run_locally


```bash
# assumes you have exported aws profile with aws cli locally
python -m scripts.reddit_ratings
```

- reddit_ratings.py = api call to reddit to get television ratings and transform for upload into persistant storage

## unit-tests
```bash
python -m unittest
```

### integration-tests

```bash
python -m unittest discover integration
```


## known-issues
- No data from 2022-10-29 through 2023-03-18 inclusive
- No data after 2023-06-10 outside of 2023-07-15 due to project archival