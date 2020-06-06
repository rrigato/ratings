from bs4 import BeautifulSoup
from datetime import datetime
from dateutil import parser

import boto3
import json
import logging
import math
import os
import requests

'''
    Special user agent that is recommended according to the
    api docs
    <platform>:<app ID>:<version string> (by /u/<reddit username>)
'''
REDDIT_USER_AGENT = "Lambda:toonamiratings:v1.0 (by /u/toonamiratings)"


def get_logger(working_directory=os.getcwd()):
    """Sets up logger

        Parameters
        ----------
        working_directory: str
            Where to put logger, defaults to cwd

        Returns
        -------

        Raises
        ------
    """
    '''
        Adds the file name to the logs/ directory without
        the extension
    '''
    logging.basicConfig(
        filename=os.path.join(working_directory, "logs/",
        os.path.basename(__file__).split(".")[0]),
        format="%(asctime)s %(message)s",
         datefmt="%m/%d/%Y %I:%M:%S %p", level=logging.DEBUG
         )
    logging.info("\n")

def get_boto_clients(resource_name, region_name='us-east-1',
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



def get_client_secrets():
    """Returns reddit client key and reddit client secret 

        Parameters
        ----------

        Returns
        -------
        reddit_client_key : str
            Reddit client key

        reddit_client_secret : str
            Reddit client secret        

        Raises
        ------
    """
    secrets_manager_client = get_boto_clients(resource_name="secretsmanager")


    '''
        Passing the Name of the string to the boto client
    '''
    reddit_client_key = secrets_manager_client.get_secret_value(
        SecretId="/prod/reddit_api_key"
    )

    reddit_client_secret = secrets_manager_client.get_secret_value(
        SecretId="/prod/reddit_api_secret"
    )

    return(
        reddit_client_key["SecretString"],
        reddit_client_secret["SecretString"]
    )


def get_oauth_token(client_key, client_secret):
    """Gets an Oath token from the reddit API

        Parameters
        ----------
        client_key : str
            Key for the reddit api

        client_secret : str
            Secret for the reddit api

        Returns
        -------
        oauth_token : dict
            Dictionary with the oauth_token and expires_in
            keys. Ex:
            {
                "access_token": "<token_value>",
                "token_type": "bearer",
                "expires_in": 3600,
                "scope": "*"
            }

        Raises
        ------
    """
    '''
        user agent specification outlined here:
        https://github.com/reddit-archive/reddit/wiki/API
    '''
    reddit_headers = {
        "user-agent": REDDIT_USER_AGENT
    }
    logging.info("Custom Headers: ")
    logging.info(reddit_headers)
    '''
        grant_type=client_credentials is
        x-www-form-urlencoded which is what indicates
        this is a application only with no
        user sign in
        auth basic auth where key is reddit client key
        and password is reddit client secret
    '''
    oauth_token = requests.post(
        url="https://www.reddit.com/api/v1/access_token",
        auth=(client_key, client_secret),
        data={"grant_type":"client_credentials"},
        headers=reddit_headers
    )
    
    return(oauth_token.json())

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

def get_ratings_post(news_flair_posts):
    """Retrieves

        Parameters
        ----------
        news_flair_posts : dict
            Dict of all posts after fullname_after

        Returns
        -------
        ratings_post_list : list
            list providing the elements of the reddit
            search api response that are ratings posts
            Ex: [0, 3, 8]

        Raises
        ------
    """
    ratings_post_list = []
    element_counter = 0
    '''
        Iterates over every reddit post looking for
    '''
    for reddit_post in news_flair_posts["data"]["children"]:

        '''
            If the string "ratings" is in the title of the
            post after lowercasing the title string
            then we count that as a ratings related post
        '''
        if (reddit_post["data"]["title"].lower().find("ratings")
            != (-1)):
            logging.info("Rating post found")
            logging.info(reddit_post["data"]["title"])
            logging.info(reddit_post["data"]["name"])

            ratings_post_list.append(element_counter)
        element_counter += 1
    return(ratings_post_list)


def handle_table_header(bs_obj):
    """Converts table header for the html table into list

        Parameters
        ----------
        bs_obj : bs4.BeautifulSoup
            BeautifulSoup Object to parse table header

        Returns
        -------
        header_columns : list
            list of header columns parsed from html table header

        Raises
        ------
    """
    '''
        Gets all table header html tags
        And putting the contents of each of those in a
        list
    '''
    all_th_tags = bs_obj.find("thead").findAll("th")
    logging.info("Found the following table headers: ")
    logging.info(all_th_tags)

    header_columns = []

    for th_tag in all_th_tags:
        header_columns.append(th_tag.text)

    logging.info("header columns parsed: ")
    logging.info(header_columns)

    return(header_columns)

def handle_table_body(bs_obj, header_columns):
    """Converts table body for the html table into dict

        Parameters
        ----------
        bs_obj : bs4.BeautifulSoup
            BeautifulSoup Object to parse table header

        header_columns : list
            list of header columns parsed from html table header

        Returns
        -------
        saturday_ratings : list
            list of dict of one saturday nights ratings where the key
            is from the header_columns list and the value
            is from the <tr> html tag

        Raises
        ------
    """
    '''
        Gets all table header html tags
        And putting the contents of each of those in a
        list
    '''
    all_tr_tags = bs_obj.find("tbody").findAll("tr")

    logging.info("Found this many shows: ")
    logging.info(len(all_tr_tags))

    saturday_ratings = []
    '''
        First iteration is over list of <tr>
        table rows

        individual_show = list of bs4.element.Tag
    '''
    for individual_show in all_tr_tags:
        show_dict = {}
        '''
        Second iteration
        is the columns that will be used for key values
        of each dict in the list

        Iterating over the column name and
        the associated td which will be the value
        of the dict

        These two lists will always be the same length
        becuase each <td> (table data) needs a corresponding
        <tr> (table row)

        dict_key : str
        dict_value : bs4.element.Tag
        '''
        for dict_key, dict_value in zip(header_columns,
            individual_show.findAll("td")):
            '''
                will be something like
                show_dict["Time"] = "11:00"
                Taking text from td tag
            '''
            show_dict[dict_key] = dict_value.text

        ''' Append dict to list '''
        saturday_ratings.append(show_dict)

    return(saturday_ratings)


def handle_table_clean(reddit_post_html, rating_call_counter,
    ratings_title):
    """Cleans the html table reddit post returned

        Parameters
        ----------
        reddit_post_html : str
            HTML post for the table

        rating_call_counter : int
            Sequence starting at 0 that describes
            how many ratings posts have been called

        ratings_title : str
            The title we are attempting to parse the
            date from


        Returns
        -------
        body_dict : dict
            Dict of individual show ratings
            Ex:
            {
                "Time": "12:00a",
                "Show": "My Hero Academia (r)", 
                "Viewers (000)": "590", 
                "18-49 Rating": "0.29", 
                "18-49 Views (000)": "380", 
                "ratings_occurred_on": "2020-05-09"
            }

        Raises
        ------
    """
    bs_obj = BeautifulSoup(reddit_post_html, "html.parser")
    header_columns = handle_table_header(bs_obj)
    body_dict = handle_table_body(
        bs_obj=bs_obj,
        header_columns=header_columns
    )
    logging.info("Cleaned the ratings post")

    '''
        Parses a datetime from the title of the
        post which will originally be something like:
        "Toonami Ratings for November 2nd, 2019"

        Returns tuple where the first element is
        the datetime and the second is the leftover
        string
        (datetime.datetime(2019, 11, 2, 0, 0), ('Toonami Ratings for ', ' ', ', '))
    '''
    ratings_occurred_on = parser.parse(ratings_title,
        fuzzy_with_tokens=True)

    logging.info("Date Parse Fuzzy Logic: ")
    logging.info(ratings_title)
    logging.info(ratings_occurred_on)

    '''
        Iterating over every saturday night ratings
        which is list of dict and adding a new element
        for the datetime on which the ratings occurred
        formatting date in ISO 8601 standard
    '''
    for show_element in body_dict:
        show_element["ratings_occurred_on"] = ratings_occurred_on[0].strftime("%Y-%m-%d")
    return(body_dict)

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

def dict_key_mapping(pre_clean_ratings_keys):
    """Maps inconsistent source data to column names for dynamodb

        Parameters
        ----------
        pre_clean_ratings_keys : list
            list of dict whose 

        Returns
        -------
        clean_ratings_columns : list
            list of dict with standardized column names
            matching one of the following 7:
            [
                "PERCENTAGE_OF_HOUSEHOLDS",
                "PERCENTAGE_OF_HOUSEHOLDS_AGE_18_49",
                "RATINGS_OCCURRED_ON",
                "SHOW",
                "TIME", 
                "TOTAL_VIEWERS", 
                "TOTAL_VIEWERS_AGE_18_49"

            ]


        Raises
        ------
        KeyError :
            KeyError is raised if the keys for a dict
            in pre_clean_ratings_keys cannot be mapped 
            back to a dynamodb column listed in key_to_dynamo_column_map
    """
    key_to_dynamo_column_map = {
        "ATotal": "TOTAL_VIEWERS_AGE_18_49",
        "AHousehold": "PERCENTAGE_OF_HOUSEHOLDS_AGE_18_49",
        "Date": "RATINGS_OCCURRED_ON",
        "Household": "PERCENTAGE_OF_HOUSEHOLDS",
        "ratings_occurred_on": "RATINGS_OCCURRED_ON",
        "Show": "SHOW",
        "Time": "TIME", 
        "Total": "TOTAL_VIEWERS", 
        "Viewers (000)": "TOTAL_VIEWERS",
        "18-49 Rating": "PERCENTAGE_OF_HOUSEHOLDS_AGE_18_49",
        "18-49 Views (000)": "TOTAL_VIEWERS_AGE_18_49"

    }

    clean_ratings_columns = []
    for dict_to_clean in pre_clean_ratings_keys:
        '''
            Iterates over all keys in each dict
        '''
        for original_key in list(dict_to_clean.keys()):
            '''
                If the key is already a valid output column 
                name we do nothing
            '''
            if original_key in list(key_to_dynamo_column_map.values()):
                pass
            else:
                '''
                    static mapping to standardize dynamodb
                    keys that removes old key and adds the correct dynamo
                    column name mapping

                    original_key will be one of the keys in key_to_dynamo_column_map

                    Will pop (remove) that key from original dict and 
                    assign the corresponding value for original_key 
                    in key_to_dynamo_column_map to dict_to_clean
                '''

                dict_to_clean[key_to_dynamo_column_map[original_key]] =  dict_to_clean.pop(
                    original_key
                )
        '''
            Append each cleaned dict
        '''
        clean_ratings_columns.append(dict_to_clean)

    return(clean_ratings_columns)

def clean_dict_value(ratings_values_to_clean):
    """Overrides for ratings data

        Parameters
        ----------
        ratings_values_to_clean : list
            list of dict where each dict has already been
            passed through dict_key_mapping

        Returns
        -------
        clean_ratings_values : list
            list of dict where the values have been cleaned

        Raises
        ------
    """
    clean_ratings_values = []
    for dict_to_clean in ratings_values_to_clean:
        dict_to_clean["IS_RERUN"] = None
        '''
            If we are able to find " (r)" in the 
            SHOW string that indicates a rerun
            removing everthing before the space and
            marking IS_RERUN as True
        '''
        if dict_to_clean["SHOW"].find(" (r)") > 0:
            dict_to_clean["SHOW"] = dict_to_clean["SHOW"].split(" (r)")[0]
            dict_to_clean["IS_RERUN"] = True
        
        '''
            Try catch handles if PERCENTAGE_OF_HOUSEHOLDS_AGE_18_49
            is not included in the list of keys
        '''
        try:
            if dict_to_clean["PERCENTAGE_OF_HOUSEHOLDS_AGE_18_49"] == "9.99":
                dict_to_clean["PERCENTAGE_OF_HOUSEHOLDS_AGE_18_49"] = None
        except KeyError:
            '''
                do nothing if PERCENTAGE_OF_HOUSEHOLDS_AGE_18_49
                is not present
            '''
            pass
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


def handle_ratings_insertion(all_ratings_list, table_name):
    """Handles inserting ratings into dynamodb

        Parameters
        ----------
        all_ratings_list : list
            List of dict where each element is
            one saturday night ratings

        table_name : str
            name of the dynamodb table

        Returns
        -------

        Raises
        ------

    """
    dynamo_client, dynamo_table = get_boto_clients(
            resource_name="dynamodb",
            region_name="us-east-1",
            table_name=table_name
    )

    ratings_occurred_on = sort_ratings_occurred_on(
        ratings_list=all_ratings_list
    )

    import pdb; pdb.set_trace()




def lambda_handler(event, context):
    """Handles lambda invocation from cloudwatch events rule

        Parameters
        ----------

        Returns
        -------

        Raises
        ------
    """
    get_logger()
    all_ratings_list = ratings_iteration(number_posts=10)


def main():
    """Entry point into the script
        Parameters
        ----------

        Returns
        -------

        Raises
        ------
    """
    get_logger()

    all_ratings_list = ratings_iteration(number_posts=10)

    clean_rating_keys = dict_key_mapping(
        pre_clean_ratings_keys=all_ratings_list
    )

    clean_rating_values = clean_dict_value(
        ratings_values_to_clean=all_ratings_list
    )

    handle_ratings_insertion(
        all_ratings_list=all_ratings_list,
        table_name="dev_toonami_ratings"
    )

if __name__ == "__main__":
    main()
