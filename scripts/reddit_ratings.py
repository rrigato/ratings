import logging
import os

from ratings.repo.ratings_repo_backend import (persist_ratings,
                                               persist_show_names,
                                               ratings_from_internet)


def main() -> None:
    """Orchestrates clean architecture invocations from
    external

    Raises
    ------
    RuntimeError
        if unexpected error from clean architecture
    """
    logging.info(f"--------------main - invocation begin--------------")

    tv_ratings, retreival_error = ratings_from_internet()

    if retreival_error is not None:
        raise RuntimeError(retreival_error)
    
    logging.info(
        f"main - len(tv_ratings) - {len(tv_ratings)}"
    )

    persistence_error = persist_ratings(tv_ratings)

    if persistence_error is not None:
        raise RuntimeError(persistence_error)
    
    logging.info(f"main - persist_ratings successful")

    analytics_error = persist_show_names(tv_ratings)

    if analytics_error is not None:
        raise RuntimeError(analytics_error)
    
    logging.info(f"--------------main - invocation end--------------")

    return(None)



def lambda_handler(event, context):
    """Handles lambda invocation from cloudwatch events rule
    """
    '''
        Logging required for cloudwatch logs
    '''
    logging.getLogger().setLevel(logging.INFO)
    main()




if __name__ == "__main__":
    import logging
    import os
    from time import strftime
    os.environ["AWS_REGION"] = "us-east-1"
    logging.basicConfig(
        format=("%(levelname)s | %(asctime)s.%(msecs)03d" +
            strftime("%z") + " | %(message)s"
        ),
        datefmt="%Y-%m-%dT%H:%M:%S", 
        level=logging.INFO
    )
    lambda_handler({}, None)

