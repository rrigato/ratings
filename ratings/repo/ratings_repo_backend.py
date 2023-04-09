import json
import logging
from copy import deepcopy
from typing import Dict, List, Optional, Union

import boto3

from ratings.entities.ratings_entities import SecretConfig, TelevisionRating


def ratings_from_internet() -> Union[
    Optional[List[TelevisionRating]], Optional[str]
]:
    """Returns List[TelevsionRating], None if success
    None, None if no error but no TelevisionRating
    None, str if error
    """
    return(None)

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

