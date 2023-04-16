import json
from copy import deepcopy
from datetime import date
from random import paretovariate, randint
from typing import Dict, Union

from ratings.entities.ratings_entities import SecretConfig, TelevisionRating


def get_mock_television_ratings(number_of_ratings: int
                                ) -> list[TelevisionRating]:
    """Creates a list of mock TelevisionRating 
    of length number_of_ratings
    """
    television_ratings_list = []

    for rating_num in range(number_of_ratings):

        mock_television_rating = TelevisionRating()

        mock_television_rating.show_air_date = date.fromisoformat(
            "2014-01-04")
        mock_television_rating.time_slot = str(rating_num) + ":00 am"
        mock_television_rating.show_name = "MOCK_SHOW" + str(rating_num)
        mock_television_rating.rating = min(
            int(100 * paretovariate(1)), 9999)
        mock_television_rating.rating_18_49 = max(
            int(mock_television_rating.rating - 
                (10*paretovariate(3))), 25
        )
        mock_television_rating.household = round(
            paretovariate(2) / 10, 2)
        mock_television_rating.household_18_49 = max(
            round(mock_television_rating.household - 
                  (10*paretovariate(3))), .05
        )
        mock_television_rating.rating_year = randint(2012, 3005)

        television_ratings_list.append(mock_television_rating)

    return(deepcopy(television_ratings_list))



def mock_secret_config(
    ) -> SecretConfig:
    """Every attribute of the SecretConfig entity is populated
    """
    
    
    object_properties = [
        attr_name for attr_name in dir(SecretConfig)
        if not attr_name.startswith("_")
    ]
    
    mock_entity = SecretConfig()

    mock_entity.reddit_client_id = "mockclientid"
    # pragma: allowlist nextline secret
    mock_entity.reddit_client_secret = "mockvalue"    
    # pragma: allowlist nextline secret
    mock_entity.reddit_password = "mockvalue2"    
    mock_entity.reddit_username = "mockvalue3"    

    for object_property in object_properties:
        assert getattr(
            mock_entity, object_property
        ) is not None, (
            f"mock_secret_config = fixture missing {object_property}"
        )
    
    return(deepcopy(mock_entity))



def mock_oauth_token_response(
    ) -> Dict[str, Union[str, int]]:
    """Mock reddit token api response
    """
    
    return(deepcopy(
        {
            "access_token": "FIXTURETOKEN123",
            "token_type": "bearer",
            "expires_in": 3600,
            "scope": "*"
        }
    ))

