import json
import logging
from copy import deepcopy
from typing import Dict, List, Optional, Union
from urllib.request import Request

import boto3
import requests

from ratings.entities.ratings_entities import SecretConfig, TelevisionRating


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
REDDIT_USER_AGENT = "Lambda:toonamiratings:v1.0 (by /u/toonamiratings)"


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



def _orchestrate_http_request(
    secret_config: SecretConfig
    ) -> Dict:
    """creates http api request and returns
    dict
    """
    oauth_response = get_oauth_token(
        secret_config.reddit_client_id,
        secret_config.reddit_client_secret
    )
    logging.info(f"_orchestrate_http_request - oauth_response")
    # Request("")

    logging.info(f"_orchestrate_http_request - invocation end")
    return(None)



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

    return([], None)




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
