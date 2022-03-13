import logging

def _manual_skip_date(ratings_date_to_skip, all_ratings_list):
    """Manually skips a passed date

        Parameters
        ----------
        ratings_date_to_skip: str
            elements of all_ratings_list with RATINGS_OCCURRED_ON
            equal to ratings_date_to_skip will be removed from the list

        all_ratings_list : list
            safe source of element structure is scripts.reddit_ratings.clean_dict_value
    """

    logging.info("_manual_skip_date - dropping - " + str(ratings_date_to_skip))
    elements_to_drop = []

    for rating_element in range(len(all_ratings_list)):
        if all_ratings_list[rating_element["RATINGS_OCCURRED_ON"]] == ratings_date_to_skip:
            elements_to_drop.append(rating_element)

    for element_to_drop in elements_to_drop:
        removed_rating = all_ratings_list.pop(element_to_drop)
        logging.info("_manual_skip_date - dropped element - " + str(elements_to_drop))

    logging.info("_manual_skip_date - complete")
    



def data_override_factory(all_ratings_list):
    """Factory function for mutation based data scrubbing activities from production data
    Extend this public interface with new private functionality whenever applying
    new manual data preparation activities

        Parameters
        ----------
        all_ratings_list : list
            safe source of element structure is scripts.reddit_ratings.clean_dict_value
   
    """
    pass
