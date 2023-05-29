import json
import logging
import math
import os
from datetime import datetime
from typing import Dict, List, Union

import boto3
import requests

from ratings.repo.data_scrubber import data_override_factory
from ratings.repo.ratings_repo_backend import (REDDIT_USER_AGENT,
                                               _standardize_key_name,
                                               get_oauth_token,
                                               get_ratings_post,
                                               handle_table_clean, persist_ratings, persist_show_names, ratings_from_internet)


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


def iterate_handle_table_clean(news_flair_posts, ratings_post_list,
    ratings_list_to_append):
    """Tests cleaning of ratings data

        Parameters
        ----------
        news_flair_posts : dict
            Dict of all posts with a news reddit flair
            after fullname_after

        ratings_post_list : list
            list providing the elements of the reddit
            search api response that are ratings posts
            Ex: [0, 3, 8]

        ratings_list_to_append : list
            Existing list of dict where each element is
            one saturday night ratings that will be appended to

        Returns
        -------
        all_ratings_list : list
            List of dict where each element is
            one saturday night ratings populated from
            news_flair_list

        Raises
        ------
    """

    '''
        Iterating over just news flair posts
        that are ratings posts
    '''
    for ratings_post in ratings_post_list:
        
        clean_ratings_post = handle_table_clean(
            reddit_post_html=news_flair_posts["data"]["children"][ratings_post]["data"]["selftext_html"],
            rating_call_counter=0,
            ratings_title=news_flair_posts["data"]["children"][ratings_post]["data"]["title"]
        )
        '''
            extend takes all dicts from
            clean_ratings_post and puts them in
            all_ratings_list
        '''
        ratings_list_to_append.extend(clean_ratings_post)


    return(ratings_list_to_append)



def ratings_iteration(number_posts=10):
    """Handles rating iteration

        Parameters
        ----------
        number_posts : int
            Defaults to 10, the number of news posts to 
            search over for ratings.

        Returns
        -------
        all_ratings_list : list
            List of dict where each element is
            one saturday night ratings


        Raises
        ------

    """
    reddit_client_key, reddit_client_secret = get_client_secrets()


    oauth_token = get_oauth_token(
        client_key=reddit_client_key,
        client_secret=reddit_client_secret
        )

    '''
        Initializing ratings post name tracker
        and list
    '''
    fullname_after = None
    all_ratings_list = []

    logging.info("Oauth token for ratings_iteration")
    '''
        If number_posts is None we are only looking
        for the most recent ratings post
    '''
    if (number_posts <= 25):
        news_flair_posts = get_news_flair(
            access_token=oauth_token["access_token"],
            posts_to_return=number_posts)

        ratings_post_list = get_ratings_post(news_flair_posts)

        all_ratings_list = iterate_handle_table_clean(
            news_flair_posts=news_flair_posts,
            ratings_post_list=ratings_post_list,
            ratings_list_to_append=all_ratings_list
        )

        return(all_ratings_list)

    else:
        '''
            Iterate in batches of 25 if we want to 
            iterate all posts
        '''
        assert type(number_posts) is int, (
            "news_flair_posts must be passed an int for posts_to_return"
        )


        '''
            Logic for breaking apart the historical api calls
        '''
        for api_call_count in range(math.ceil(number_posts/25)):
            news_flair_posts = get_news_flair(
                access_token=oauth_token["access_token"],
                posts_to_return=number_posts,
                fullname_after=fullname_after)

            '''
                No more historical posts to search over
            '''
            if news_flair_posts["data"]["dist"] == 0:
                logging.info("No more posts to iterate")
                return(all_ratings_list)

            ratings_post_list = get_ratings_post(news_flair_posts)

            '''
                Small number of news posts does not
                have any ratings posts to return
            '''
            if len(ratings_post_list) == 0:
                logging.info("No more posts to iterate")
                return(all_ratings_list)

            all_ratings_list = iterate_handle_table_clean(
                news_flair_posts=news_flair_posts,
                ratings_post_list=ratings_post_list,
                ratings_list_to_append=all_ratings_list
            )
            '''
                Gets the fullname of the last post
                in the ratings_post_list
                ratings_post_list[len(ratings_post_list) - 1] =
                last element in list
            '''
            fullname_after = news_flair_posts["data"]["children"][
                ratings_post_list[len(ratings_post_list) - 1]
                ]["data"]["name"]


def dict_key_mapping(
        pre_clean_ratings_keys: List[Dict]
        ) -> List[Dict[str, Union[str, int]]]:
    """Maps inconsistent source data to column names for dynamodb

        Parameters
        ----------
        pre_clean_ratings_keys
            refer to keys of get_table_column_name_mapping return
            value for potential key names since this is user input data
            that can be highly inconsistent

        Returns
        -------
        clean_ratings_columns
            list of dict with standardized column names
            matching one of the following:
            [
                "PERCENTAGE_OF_HOUSEHOLDS",
                "PERCENTAGE_OF_HOUSEHOLDS_AGE_18_49",
                "RATINGS_OCCURRED_ON",
                "SHOW",
                "TIME", 
                "TOTAL_VIEWERS", 
                "TOTAL_VIEWERS_AGE_18_49",
                "YEAR",
                "IS_RERUN"

            ]


        Raises
        ------
        KeyError :
            KeyError is raised if the keys for a dict
            in pre_clean_ratings_keys cannot be mapped 
            back to a dynamodb column listed in get_table_column_name_mapping
    """

    clean_ratings_columns = []
    for dict_to_clean in pre_clean_ratings_keys:
        _standardize_key_name(dict_to_clean)
        '''
            Append each cleaned dict
        '''
        clean_ratings_columns.append(dict_to_clean)

    logging.info("dict_key_mapping - Mapped ratings post column names")
    logging.info(clean_ratings_columns)
    
    return(clean_ratings_columns)

def clean_adult_household(dict_to_clean):
    """Cleans the PERCENTAGE_OF_HOUSEHOLDS_AGE_18_49 field

        Parameters
        ----------
        dict_to_clean : dict
            Individual rating that is pass by reference

        Returns
        -------

        Raises
        ------
    """
    '''
        Try catch handles if PERCENTAGE_OF_HOUSEHOLDS_AGE_18_49
        is not included in the list of keys
    '''
    try:
        if dict_to_clean["PERCENTAGE_OF_HOUSEHOLDS_AGE_18_49"] == "9.99":
            dict_to_clean.pop("PERCENTAGE_OF_HOUSEHOLDS_AGE_18_49")
    except KeyError:
        '''
            do nothing if PERCENTAGE_OF_HOUSEHOLDS_AGE_18_49
            is not present
        '''
        pass


def clean_dict_value(ratings_values_to_clean):
    """Calls cleaning helper functions to clean elements of
        each rating show

        Parameters
        ----------
        ratings_values_to_clean : list
            list of dict where each dict has already been
            passed through dict_key_mapping

        Returns
        -------
        clean_ratings_values : list
            list of dict with the following keys:
            RATINGS_OCCURRED_ON - YYYY-MM-DD date
            TIME - str of timeslot Example 12:00a
            SHOW - str of show  
            TOTAL_VIEWERS - int of viewers in thousands 
            PERCENTAGE_OF_HOUSEHOLDS_AGE_18_49 - float  
            YEAR - int of year Example - 2022
            

        Raises
        ------
    """
    clean_ratings_values = []
    for dict_to_clean in ratings_values_to_clean:
        '''
            If we are able to find " (r)" in the 
            SHOW string that indicates a rerun
            removing everthing before the space and
            marking IS_RERUN as True
        '''
        if dict_to_clean["SHOW"].find(" (r)") > 0:
            dict_to_clean["SHOW"] = dict_to_clean["SHOW"].split(" (r)")[0]
            dict_to_clean["IS_RERUN"] = True
        
        clean_adult_household(dict_to_clean=dict_to_clean)
        

        clean_ratings_values.append(dict_to_clean)

    return(clean_ratings_values)

def sort_ratings_occurred_on(ratings_list):
    """Sorts ratings in descending order by date

        Parameters
        ----------
        ratings_list : list
            List of dict where each element is
            one saturday night ratings

        Returns
        -------
        ratings_occurred_on : list
            List of str sorted by date

        Raises
        ------
    """
    
    ratings_as_dates = [] 
    '''
        For each dict of ratings get the 
        RATINGS_OCCURRED_ON string and convert that to 
        a datetime object
    '''
    for individual_rating in ratings_list:
        ratings_as_dates.append(
            datetime.strptime(
                individual_rating["RATINGS_OCCURRED_ON"], "%Y-%m-%d"
            )
        )


    '''
        Unique ratings
    '''
    ratings_as_dates = set(ratings_as_dates)

    '''
        sorted = Turns set into a list of datetime objects that are
        in descending order

        List comprehension iterates through each of those datetime objects
        formats as a string in "YYYY-MM-DD" that is added to the list
    '''
    ratings_occurred_on = [ 
        datetime.strftime(original_datetime, "%Y-%m-%d") for original_datetime in 
        sorted(ratings_as_dates, reverse=True)
    ]

    return(ratings_occurred_on)


def deprecated_main():
    """Entry point into the script
    """
    '''
        get dev or prod from the function name
    '''
    environment_prefix = os.environ.get(
        "AWS_LAMBDA_FUNCTION_NAME").split("-")[0]
    logging.info("main - running in " + environment_prefix)

    all_ratings_list = ratings_iteration(number_posts=25)

    clean_rating_keys = dict_key_mapping(
        pre_clean_ratings_keys=all_ratings_list
    )

    clean_rating_values = clean_dict_value(
        ratings_values_to_clean=all_ratings_list
    )

    logging.info("main - clean_dict_value - " + str(len(all_ratings_list)))
    
    






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

