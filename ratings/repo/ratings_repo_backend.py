import json
import logging
from copy import deepcopy
from datetime import date, datetime
from http.client import HTTPResponse
from typing import Dict, List, Optional, Union
from urllib.parse import urlencode
from urllib.request import Request, urlopen

import boto3
import requests
from bs4 import BeautifulSoup
from dateutil import parser

from ratings.entities.ratings_entities import SecretConfig, TelevisionRating
from ratings.repo.excluded_ratings_titles import get_excluded_titles
from ratings.repo.name_mapper import (get_table_column_name_mapping,
                                      keys_to_ignore)




def standardize_time(
    show_time: str
    ) -> str:
    """A foolish consistency is the hobgoblin of little minds
    """
    clean_string = show_time.strip().replace(" ", "").lower().replace(".", "")
    
    if "pm" in clean_string:
        return(clean_string.replace("pm", ""))
    if "p" in clean_string:
        return(clean_string.replace("p", ""))
    if "am" in clean_string:
        return(clean_string.replace("am", "a"))
    
    return(clean_string)



def _standardize_key_name(
        dict_to_clean: Dict[str, Union[str, int]]
    ) -> None:
    """Mutates key names for dict_to_clean 
    to align with values of get_table_column_name_mapping
    
    Raises
    ------
    KeyError if the key in dict_to_clean is not found

    """
    '''
            Iterates over all keys in each dict
    '''
    for user_input_key in list(dict_to_clean.keys()):
        '''Do nothing if we match the correct column names'''
        if user_input_key in get_table_column_name_mapping(
        ).values():
            return(None)


        '''
            lower caseing and removing trailing/leading 
            spaces for comparison
        '''
        clean_ratings_key = user_input_key.lower().strip()

        '''Do nothing if we if it is an excluded key'''
        if clean_ratings_key in keys_to_ignore():
            return(None)

        '''
            pops old key value from dict_to_clean
            and adds the correct dynamo
            column name mapping
            user_input_key will be one of the keys in 
            get_table_column_name_mapping
        '''
        if clean_ratings_key in get_table_column_name_mapping().keys():

            dict_to_clean[
                    get_table_column_name_mapping()[
                        clean_ratings_key
                    ]
                ] =  dict_to_clean.pop(
                    user_input_key
                )



        if clean_ratings_key not in get_table_column_name_mapping(
        ).keys():
            raise KeyError(f"_standardize_key_name - "+
            f" No match for - {clean_ratings_key}")




def handle_table_header(
        bs_obj)-> List[str]:
    """Converts th tags for the html table into list
        Parameters
        ----------
        bs_obj : bs4.BeautifulSoup
            BeautifulSoup Object to parse table header
        Returns
        -------
        header_columns
            list of header columns parsed from html table header
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

    logging.info("handle_table_header - Original ratings post column names")
    logging.info(header_columns)

    return(header_columns)



def handle_table_body(
        bs_obj, 
        header_columns: List
        ) -> List[Dict]:
    """Converts table body for the html table into dict
        Parameters
        ----------
        bs_obj : bs4.BeautifulSoup
            BeautifulSoup Object to parse table header
        header_columns
            list of header columns parsed from html table header
        Returns
        -------
        saturday_ratings 
            list of dict of one saturday nights ratings where the key
            is from the header_columns list and the value
            is from the <tr> html tag
        
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


def handle_table_clean(
        reddit_post_html: str, rating_call_counter: int,
        ratings_title: str) -> List[Dict[str, str]]:
    """Cleans the html table reddit post returned
        Parameters
        ----------
        reddit_post_html
            HTML post for the table
        rating_call_counter
            Sequence starting at 0 that describes
            how many ratings posts have been called
        ratings_title
            The title we are attempting to parse the
            date from
        Returns
        -------
        body_dict
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
        '''
            Add the YEAR
        '''
        show_element["YEAR"] = ratings_occurred_on[0].year
    return(body_dict)


def _populate_secret_config(sdk_response: Dict) -> SecretConfig:
    """https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/secretsmanager.html#SecretsManager.Client.get_secret_value
    """
    secret_config = SecretConfig()

    deserialized_secret_string = json.loads(
        sdk_response["SecretString"]
    )

    logging.info(f"_populate_secret_config - deserialized secrets")
    
    secret_config.reddit_client_id = deserialized_secret_string[
        "reddit_api_key"
    ]
    
    secret_config.reddit_client_secret = deserialized_secret_string[
        "reddit_api_secret"
    ]
    secret_config.reddit_password = deserialized_secret_string[
        "reddit_api_password"
    ]
    secret_config.reddit_username = deserialized_secret_string[
        "reddit_api_username"
    ]
    
    return(secret_config)



def load_secret_config() -> Optional[SecretConfig]:
    """Returns None if unexpected error
    """
    try:
        
        secretsmanager_client = boto3.client(
            service_name="secretsmanager", 
            region_name="us-east-1"
        )

        sdk_secret_response = secretsmanager_client.get_secret_value(
            SecretId="/prod/v1/credentials"
        )
        logging.info(f"load_secret_config - obtained config")
        

        return(_populate_secret_config(
            sdk_secret_response
        ))
    except Exception as errror_suppression:
        logging.exception(errror_suppression)
        return(None)


'''
    Special user agent that is recommended according to the
    api docs
    <platform>:<app ID>:<version string> (by /u/<reddit username>)
'''
REDDIT_USER_AGENT = "Lambda:toonamiratings:v3.0.0 (by /u/toonamiratings)"


def get_oauth_token(
        client_key: str, client_secret: str
    )-> Dict[str, Union[str, int]]:
    """Gets an Oath token from the reddit API
        Parameters
        ----------
        client_key
            Key for the reddit api
        client_secret
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
    """
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


def evaluate_ratings_post_title(
        ratings_title: str) -> bool:
    """Validates whether the post is a television post
    based on the title
        Parameters
        ----------
        ratings_title
            title of reddit post
        Returns
        -------
        True if ratings_title includes the string
            ratings and if it is not in the excluded
            ratings list
    """
    if ratings_title in get_excluded_titles():
        logging.info("evaluate_ratings_post_title - " +
                     "get_excluded_titles - " +
                     ratings_title
                )
        return(False)

    return(ratings_title.lower().find("ratings") != (-1))



def get_ratings_post(
        news_flair_posts: Dict) -> List[Dict]:
    """Retrieves posts with ratings in the name
        
        Returns
        -------
        ratings_post_list 
            list providing the elements of the reddit
            search api response that are ratings posts
            Ex: [0, 3, 8]
        
    """
    ratings_post_list = []
    element_counter = 0
    '''
        Iterates over every reddit post 
        looking for news ratings
    '''
    for reddit_post in news_flair_posts["data"]["children"]:

        if (evaluate_ratings_post_title(
            ratings_title=reddit_post["data"]["title"]
            )
            ):
            logging.info(
                "get_ratings_post - valid title - " +
                str(reddit_post["data"]["title"])
            )
            logging.info(
                "get_ratings_post - valid name - " +
                str(reddit_post["data"]["name"])
            )

            ratings_post_list.append(element_counter)
        element_counter += 1

    logging.info(
        "get_ratings_post - len(ratings_post_list) - " +
        f"{len(ratings_post_list)}"
    )

    return(ratings_post_list)


def _parse_int(
    potential_int: str
    ) -> int:
    """ensures the potential_int is valid

    Raises
    ------
    AssertionError
        if potential_int is not numeric
    """
    assert potential_int.isnumeric(), (
        f"_parse_int - {potential_int}"
    )
    return(int(potential_int))


def _parse_float(
    potential_float: str
    ) -> Optional[float]:
    """ensures the potential_float is valid

    Raises
    ------
    AssertionError
        if potential_float is not numeric
    """
    if potential_float is None:
        return(None)
    assert potential_float.replace(".", "").isnumeric(), (
        f"_parse_float - {potential_float}"
    )
    return(float(potential_float))


def _handle_show_air_date(rating_dict: Dict) -> date:
    """parses show_air_date property from rating_dict

    Raises
    ------
    KeyError
        if show_air_date is not found in rating_dict
    """
    show_air_date = rating_dict.get("RATINGS_OCCURRED_ON")

    if show_air_date is None:
        show_air_date = rating_dict["ratings_occurred_on"]

    return (datetime.strptime(
            show_air_date,
            "%Y-%m-%d"
        ).date())


def _create_television_rating(
    news_post: Dict
    ) -> List[TelevisionRating]:
    """Creates new TelevisionRating
    """
    ratings_for_news_post: List[TelevisionRating] = []
    

    parsed_table_ratings = handle_table_clean(
        reddit_post_html=news_post["data"]["selftext_html"],
        rating_call_counter=None,
        ratings_title=news_post["data"]["title"]
    )

    for rating_dict in parsed_table_ratings:
        tv_rating = TelevisionRating()

        _standardize_key_name(rating_dict)

        '''
        refer to get_table_column_name_mapping value
        '''
        tv_rating.household = _parse_float(
            rating_dict.get("PERCENTAGE_OF_HOUSEHOLDS")
        )
        tv_rating.household_18_49 = _parse_float(
            rating_dict.get("PERCENTAGE_OF_HOUSEHOLDS_AGE_18_49")
        )
        tv_rating.rating = _parse_int(
            rating_dict["TOTAL_VIEWERS"]
        )
        if rating_dict.get("TOTAL_VIEWERS_AGE_18_49") is not None:
            tv_rating.rating_18_49 = _parse_int(
                rating_dict.get("TOTAL_VIEWERS_AGE_18_49")
            )
        tv_rating.rating_year = rating_dict["YEAR"] 
        tv_rating.show_air_date = _handle_show_air_date(rating_dict)
        tv_rating.show_name = rating_dict["SHOW"]
        tv_rating.time_slot = standardize_time(rating_dict["TIME"])

        ratings_for_news_post.append(tv_rating)

    logging.info(
        f"_create_television_rating - len(ratings_for_news_post)"
        + f" - {len(ratings_for_news_post)}")    
    
    return(ratings_for_news_post)


def _populate_television_ratings_entities(
    reddit_api_response: Dict   
    ) -> List[TelevisionRating]:
    """
    Parameters
    ----------
    https://www.reddit.com/dev/api/#GET_search
    """
    logging.info(
        f"_populate_television_ratings_entities - invocation begin")
    
    ratings_posts: List[TelevisionRating] = []

    for news_post in reddit_api_response["data"]["children"]:
        if evaluate_ratings_post_title(
            news_post["data"]["title"]
        ):
            
            ratings_posts.extend(
                _create_television_rating(news_post)
            )
    
    logging.info(
        f"_populate_television_ratings_entities - len(ratings_posts)"
        + f" - {len(ratings_posts)}"
    )
    
    return(ratings_posts)



def _orchestrate_http_request(
    secret_config: SecretConfig
    ) -> Dict:
    """reddit http api request to
    load news posts
    """
    oauth_response = get_oauth_token(
        secret_config.reddit_client_id,
        secret_config.reddit_client_secret
    )
    logging.info(f"_orchestrate_http_request - oauth_response")
    
    

    url_encoded_params = urlencode({
        "limit": 25,
        "q":"flair:news",
        "raw_json": 1,
        "restrict_sr":"on",
        "sort":"new",
        "t":"all"
    })
    
    reddit_api_request = Request(
        "https://oauth.reddit.com" +
        "/r/toonami/search.json?" +
        url_encoded_params
    )

    reddit_api_request.add_header("Authorization",
        "Bearer " + oauth_response["access_token"]
    )


    api_response : HTTPResponse
    with urlopen(
            url=reddit_api_request
        ) as api_response:

        logging.info(f"_orchestrate_http_request - status_code " +
                     str(api_response.status)
        )    
        
        
        return(
            _populate_television_ratings_entities(
                json.loads(api_response.read())
            )
        )
    



def ratings_from_internet() -> Union[
    Optional[List[TelevisionRating]], Optional[str]
]:
    """Returns List[TelevsionRating], None if success
    None, None if no error but no TelevisionRating
    None, str if error
    """
    secret_config = load_secret_config()

    if secret_config is None:
        logging.info(
            f"ratings_from_internet - secret retrieval error")
        return(None, "secret retrieval error")

    logging.info(
        f"ratings_from_internet - obtained secret_config"
    )

    news_posts = _orchestrate_http_request(secret_config)


    logging.info(
        f"ratings_from_internet - obtained news_posts"
    )

    return(news_posts, None)


def persist_ratings(
    ratings_to_save: List[TelevisionRating]
    ) -> Optional[str]:
    """Returns None if successful, str of error otherwise
    """
    dynamodb_resource = boto3.resource(
        "dynamodb", "us-east-1"
    )

    dynamodb_table = dynamodb_resource.Table("prod_toonami_ratings")
    
    logging.info(f"persist_ratings - obtained table")
    
    
    for rating_to_save in ratings_to_save:
        new_item = {}
        if rating_to_save.household is not None:
            new_item["PERCENTAGE_OF_HOUSEHOLDS"] = (
                str(rating_to_save.household)
            )
        if rating_to_save.household_18_49 is not None:
            new_item["PERCENTAGE_OF_HOUSEHOLDS_AGE_18_49"] = (
                str(rating_to_save.household_18_49)
            )
        
        new_item["RATINGS_OCCURRED_ON"] = (
                rating_to_save.show_air_date.isoformat()
            )
        new_item["TIME"] = rating_to_save.time_slot
        new_item["TOTAL_VIEWERS"] = str(rating_to_save.rating)
        if rating_to_save.rating_18_49 is not None:
            new_item["TOTAL_VIEWERS_AGE_18_49"] = (
                str(rating_to_save.rating_18_49)
            )
        new_item["SHOW"] = rating_to_save.show_name
        new_item["YEAR"] = rating_to_save.rating_year

        
        dynamodb_table.put_item(Item=new_item)

    logging.info(f"persist_ratings - invocation end")
    return(None)


def persist_show_names(
        television_ratings_list: List[TelevisionRating]
    ) -> None:
    """Saves the unique show names to dynamodb
    """
    dynamodb_resource = boto3.resource(
        "dynamodb", "us-east-1"
    )

    dynamodb_table = dynamodb_resource.Table("prod_toonami_analytics")
    
    logging.info(f"persist_show_names - obtained table")
    
    
    
    all_show_names = set([
        rating.show_name for rating
        in television_ratings_list
        if rating.show_name is not None
    ])
    
    for show_name in all_show_names:
        show_name_item = {
            "PK": "ratings#showName",
            "SK": show_name
        }
        dynamodb_table.put_item(Item=show_name_item)

    
    logging.info(f"persist_show_names - invocation end")
    return(None)


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
    tv_ratings, retreival_error = ratings_from_internet()

    print(tv_ratings[0].show_air_date)
    print(tv_ratings[1].show_air_date)

    persist_ratings(tv_ratings[0:2])


