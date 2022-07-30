from typing import Union
import logging

def _manual_skip_date(ratings_date_to_skip, all_ratings_list):
    """Manually excludes elements based on ratings_date_to_skip

        Parameters
        ----------
        ratings_date_to_skip: str
            pass str in YYYY-MM-DD format
            elements of all_ratings_list with RATINGS_OCCURRED_ON
            equal to ratings_date_to_skip will be removed from the list
        

        all_ratings_list : list
            safe source of element structure is scripts.reddit_ratings.clean_dict_value
    """

    logging.info("_manual_skip_date - dropping - " + str(ratings_date_to_skip))
    elements_to_drop = []

    for rating_element in range(len(all_ratings_list)):
        if all_ratings_list[rating_element]["RATINGS_OCCURRED_ON"] == ratings_date_to_skip:
            elements_to_drop.append(rating_element)

    elements_to_drop.sort(reverse=True)
    
    logging.info(elements_to_drop)

    for element_to_drop in elements_to_drop:
        removed_rating = all_ratings_list.pop(element_to_drop)
        

    logging.info("_manual_skip_date - complete")
    


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


def _manual_override_by_date(date_to_override: str, 
    all_ratings_list: list[dict[str, Union[str, int]]]) -> None:
    """Applies manual ovverrides based on 

        Parameters
        ----------

        date_to_override
            YYYY-MM-DD format
            

        all_ratings_list : list
            safe source of element structure is scripts.reddit_ratings.clean_dict_value
    """
    override_count = 0
    

    for tv_rating in all_ratings_list:
        if tv_rating["RATINGS_OCCURRED_ON"] == date_to_override:
            override_count += 1

    logging.info("_manual_override_by_date - override_count " + str(override_count))



def _remove_missing_time(all_ratings_list):
    """Removes all elements of all_ratings_list with a dict key 
    TIME element of empty string ''

        Parameters
        ----------
        all_ratings_list : list
            safe source of element structure is scripts.reddit_ratings.clean_dict_value
    """

    logging.info("_remove_missing_time - initialized - " + str(all_ratings_list))
    elements_to_drop = []

    for rating_element in range(len(all_ratings_list)):
        if all_ratings_list[rating_element]["TIME"] == "":
            elements_to_drop.append(rating_element)

    logging.info(elements_to_drop)

    for element_to_drop in elements_to_drop:
        removed_rating = all_ratings_list.pop(element_to_drop)
        
    logging.info("_remove_missing_time - complete")
    



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

    _manual_skip_date(
        ratings_date_to_skip="2022-01-29",
        all_ratings_list=all_ratings_list
    )


    logging.info("data_override_factory - _manual_skip_date - " + str(len(all_ratings_list)))

    _override_ratings_occurred_on(
        date_to_override="2022-02-15",
        correct_ratings_date="2022-02-12",
        all_ratings_list=all_ratings_list
    )

    logging.info("data_override_factory - _override_ratings_occurred_on - " + 
        str(len(all_ratings_list))
    )

    _remove_missing_time(all_ratings_list=all_ratings_list)

    logging.info("data_override_factory - _remove_missing_time - " + str(len(all_ratings_list)))

