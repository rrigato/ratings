from copy import deepcopy

def get_table_column_name_mapping():
    """Ratings post column name to dynamodb mapping logic

        Returns
        -------
        key_to_dynamo_column_map: dict
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
            "18-49": "PERCENTAGE_OF_HOUSEHOLDS_AGE_18_49",
            "18-49 rating": "PERCENTAGE_OF_HOUSEHOLDS_AGE_18_49",
            "18-49 views (000)": "TOTAL_VIEWERS_AGE_18_49",
            "year": "YEAR",
            "is_rerun": "IS_RERUN",
            "program": "SHOW"

        }
    ))