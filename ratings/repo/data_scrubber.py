from typing import Union
import logging

def _override_ratings_occurred_on(date_to_override, correct_ratings_date, all_ratings_list):
    """Overrides incorrect RATINGS_OCCURRED_ON values

        Parameters
        ----------
        date_to_override: str
            pass str in YYYY-MM-DD format

        correct_ratings_date: str
            pass str in YYYY-MM-DD format
            All elements of all_ratings_list with RATINGS_OCCURRED_ON key of
            date_to_override will be replaced will have that keys value
            replaced by correct_ratings_date
        

        all_ratings_list : list
            safe source of element structure is scripts.reddit_ratings.clean_dict_value
    """
    override_count = 0
    
    logging.info("_override_ratings_occurred_on - overriding {incorrect} to {correct}".format(
        incorrect=date_to_override, correct=correct_ratings_date
    ))

    for tv_rating in all_ratings_list:
        if tv_rating["RATINGS_OCCURRED_ON"] == date_to_override:
            tv_rating["RATINGS_OCCURRED_ON"] = correct_ratings_date
            override_count += 1

    logging.info("_override_ratings_occurred_on - override_count " + str(override_count))


def data_override_factory(all_ratings_list):
    """Factory function for mutation based data scrubbing activities from production data
    Extend this public interface with new private functionality whenever applying
    new manual data preparation activities

        Parameters
        ----------
        all_ratings_list : list
            safe source of element structure is scripts.reddit_ratings.clean_dict_value
   
    """
    logging.info("data_override_factory - abstraction layer - " + str(len(all_ratings_list)))

    _override_ratings_occurred_on(
        date_to_override="2022-02-15",
        correct_ratings_date="2022-02-12",
        all_ratings_list=all_ratings_list
    )

    logging.info("data_override_factory - _override_ratings_occurred_on - " + 
        str(len(all_ratings_list))
    )
