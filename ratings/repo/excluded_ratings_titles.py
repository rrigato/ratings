from copy import deepcopy

def get_excluded_titles():
    """Gets excluded posts with ratings in the name but are not actually 
        ratings post

        Returns
        -------
        excluded_ratings_titles : list
            List of titles that are not ratings posts
    """
    return(deepcopy(
        [
            "The Future Of Ratings | Toonami Faithful",
            "June 24, July 1 and July 8 Toonami Ratings",
            "Toonami Ratings for June 10 + 17th",
            "August 5 & 12 Toonami Ratings"
        ]
    ))