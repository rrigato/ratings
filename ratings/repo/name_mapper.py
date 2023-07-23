from copy import deepcopy
from typing import Dict, List


def get_table_column_name_mapping() -> Dict[str, str]:
    """Ratings post column name to dynamodb mapping logic

        Returns
        -------
        key_to_dynamo_column_map
            key is the name of column in the television ratings
            post, value is the standard key used in dynamodb.
            Dict is returned by copy

    """
    return(deepcopy(
        {
            "atotal": "TOTAL_VIEWERS_AGE_18_49",
            "ahousehold": "PERCENTAGE_OF_HOUSEHOLDS_AGE_18_49",
            "date": "RATINGS_OCCURRED_ON",
            "household": "PERCENTAGE_OF_HOUSEHOLDS",
            "rating": "PERCENTAGE_OF_HOUSEHOLDS",
            "ratings_occurred_on": "RATINGS_OCCURRED_ON",
            "show": "SHOW",
            "time": "TIME", 
            "timeslot": "TIME", 
            "total": "TOTAL_VIEWERS", 
            "viewers": "TOTAL_VIEWERS",
            "viewers (000)": "TOTAL_VIEWERS",
            "viewers (000s)": "TOTAL_VIEWERS",
            "18-49": "PERCENTAGE_OF_HOUSEHOLDS_AGE_18_49",
            "18-49 rating": "PERCENTAGE_OF_HOUSEHOLDS_AGE_18_49",
            "18-49 views (000)": "TOTAL_VIEWERS_AGE_18_49",
            "year": "YEAR",
            "is_rerun": "IS_RERUN",
            "program": "SHOW"

        }
    ))


def television_rating_from_table_column() -> Dict[str, str]:
    """maps TelevisionRating entity properties
    to dynamodb table column names 

        Returns
        -------
            key is the entity property name for the
            TelevisionRating property
            value corresponds to a value from 
            get_table_column_name_mapping return dict

    """

    return(deepcopy(
        {
        "time_slot": "TIME",
        "rating_year": "YEAR",
        "household": "PERCENTAGE_OF_HOUSEHOLDS",
        "household_18_49": "PERCENTAGE_OF_HOUSEHOLDS_AGE_18_49",
        #TODO - "is_rerun": "IS_RERUN",
        "show_name": "SHOW",
        "show_air_date": "RATINGS_OCCURRED_ON",
        "rating_18_49": "TOTAL_VIEWERS_AGE_18_49",
        "rating": "TOTAL_VIEWERS"
        } 
    ))


def keys_to_ignore() -> List[str]:
    """user input keys to ignore
    """
    return([
        "rank (/150)",
        "vs last",
        "vs last*",
        "vs. last wk",
        "change"
    ])

