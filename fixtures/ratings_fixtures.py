from copy import deepcopy
from datetime import date
from random import randint
from random import paretovariate
from ratings.entities.ratings_entities import TelevisionRating
from typing import Union

import json


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


