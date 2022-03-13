from copy import deepcopy

import json


def ratings_fixture_bad_data():
    """Fixture of bad data from production ratings source in 2022 Q1
    
        Returns
        ----------
        all_ratings_list : list
            safe source of element structure is scripts.reddit_ratings.clean_dict_value
    """
    with open("fixtures/2022_data_quality.json", "r") as e2e_fixture:
        sample_ratings_data_quality = json.load(e2e_fixture)
    
    return(
        deepcopy(sample_ratings_data_quality)
    )