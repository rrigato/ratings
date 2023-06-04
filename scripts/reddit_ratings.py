import json
import logging
import os
from datetime import datetime

import boto3
import requests

from ratings.repo.ratings_repo_backend import (REDDIT_USER_AGENT,
                                               persist_ratings,
                                               persist_show_names,
                                               ratings_from_internet)


def get_boto_clients(resource_name, region_name="us-east-1",
    table_name=None):
    '''Returns the boto client for various aws resources

        Parameters
        ----------
        resource_name : str
            Name of the resource for the client

        region_name : str
                aws region you are using, defaults to
                us-east-1

        Returns
        -------
        service_client : boto3.client
            boto3 client for the aws resource in resource_name
            in region region_name

        dynamodb_table_resource : boto3.resource.Table
            boto3 Table resource, only returned if table_name is
            not None
        


        Raises
        ------
    '''

    service_client = boto3.client(
            service_name=resource_name, 
            region_name=region_name
        )

    '''
        return boto3 DynamoDb table resource in addition to boto3 client
        if table_name parameter is not None
    '''
    if table_name is not None:
        dynamodb_table_resource = boto3.resource(
            service_name=resource_name,
            region_name=region_name
        ).Table(table_name)

        return(service_client, dynamodb_table_resource)

    '''
        Otherwise return just a resource client
    '''
    return(service_client)



def get_client_secrets(region_name="us-east-1"):
    """Returns reddit client key and reddit client secret 

        Parameters
        ----------
        region_name : str
                aws region you are using, defaults to
                us-east-1        

        Returns
        -------
        reddit_client_key : str
            Reddit client key

        reddit_client_secret : str
            Reddit client secret        

        Raises
        ------
    """
    secrets_manager_client = get_boto_clients(
        resource_name="secretsmanager",
        region_name=region_name
    )


    '''
        Passing the Name of the string to the boto client
    '''
    all_client_secrets = secrets_manager_client.get_secret_value(
        SecretId="/prod/v1/credentials"
    )

    '''
        Secrets are stored in a json string
    '''
    client_secrets_dict = json.loads(all_client_secrets["SecretString"])

    '''
        return reddit api key and secret
    '''
    return(
        client_secrets_dict["reddit_api_key"],
        client_secrets_dict["reddit_api_secret"]
    )


def get_news_flair(access_token,
    posts_to_return, fullname_after=None):
    """Retrieves toonami subreddit posts before a given reddit post
        Post must have a flair of News
        fullname_after is a reddit unique id called a fullname,
        more info is provided in the docs here:
        https://www.reddit.com/dev/api/#fullnames

        Parameters
        ----------
        access_token : str
            access_token retrieved from get_oauth_token

        posts_to_return : int
            Number of reddit posts to return. Defaults
            to 25

        fullname_after : str
            Optional arguement to only include posts
            before a given fullname. Defautls to None


        Returns
        -------
        news_flair_posts : dict
            Dict of all posts with a news reddit flair
            after fullname_after



        Raises
        ------
    """
    '''
        API Query Parameter explanation
        q=flair:news
            Searching posts with a flair of new
        limit=10
            limit of how many posts to return
        sort=new
            sort by new posts
        restrict_sr=on
            restrict subreddit on to only search /r/toonami
        t=all
            time period, all
        raw_json=1
            Converts &lt; &gt; and &amp;
            to < > and & in response body
        after=fullname_after
            fullname is a unique identifier
            of a reddit api object
    '''
    url_param_dict = {
        "q":"flair:news",
        "limit":posts_to_return,
        "sort":"new",
        "restrict_sr":"on",
        "t":"all",
        "after":fullname_after

    }
    reddit_search_url = "https://oauth.reddit.com/r/toonami/search.json?raw_json=1"
    '''
        Iterating over the dict if the value is
        null that url parameter is not included
    '''
    for url_param in url_param_dict.keys():
        if (url_param_dict[url_param] is not None):
            reddit_search_url = (
                reddit_search_url + "&" +
                url_param + "=" +
                str(url_param_dict[url_param])
            )

    logging.info("Final search url:")
    logging.info(reddit_search_url)

    reddit_search_headers = {
        "user-agent":REDDIT_USER_AGENT,
        "Authorization":("Bearer " + access_token)
    }
    '''
        passing oauth token and user-agent as headers
    '''
    news_flair_posts = requests.get(
        reddit_search_url,
        headers=reddit_search_headers
    )
    logging.info("Successfully made search request")

    return(news_flair_posts.json())


def deprecated_main():
    """Entry point into the script
    """
    '''
        get dev or prod from the function name
    '''
    environment_prefix = os.environ.get(
        "AWS_LAMBDA_FUNCTION_NAME").split("-")[0]
    logging.info("main - running in " + environment_prefix)
    



def main() -> None:
    """Orchestrates clean architecture invocations from
    external

    Raises
    ------
    RuntimeError
        if unexpected error from clean architecture
    """
    logging.info(f"--------------main - invocation begin--------------")

    tv_ratings, retreival_error = ratings_from_internet()

    if retreival_error is not None:
        raise RuntimeError(retreival_error)
    
    logging.info(
        f"main - len(tv_ratings) - {len(tv_ratings)}"
    )

    persistence_error = persist_ratings(tv_ratings)

    if persistence_error is not None:
        raise RuntimeError(persistence_error)
    
    logging.info(f"main - persist_ratings successful")

    analytics_error = persist_show_names(tv_ratings)

    if analytics_error is not None:
        raise RuntimeError(analytics_error)
    
    logging.info(f"--------------main - invocation end--------------")

    return(None)



def lambda_handler(event, context):
    """Handles lambda invocation from cloudwatch events rule
    """
    '''
        Logging required for cloudwatch logs
    '''
    logging.getLogger().setLevel(logging.INFO)
    main()




if __name__ == "__main__":
    import logging
    import os
    from time import strftime
    os.environ["AWS_REGION"] = "us-east-1"
    logging.basicConfig(
        format=("%(levelname)s | %(asctime)s.%(msecs)03d" +
            strftime("%z") + " | %(message)s"
        ),
        datefmt="%Y-%m-%dT%H:%M:%S", 
        level=logging.INFO
    )
    lambda_handler({}, None)

