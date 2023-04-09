from copy import deepcopy
import logging
from typing import List, Optional, Union

from ratings.entities.ratings_entities import TelevisionRating


def ratings_from_internet() -> Union[
    Optional[List[TelevisionRating]], Optional[str]
]:
    """Returns List[TelevsionRating], None if success
    None, None if no error but no TelevisionRating
    None, str if error
    """
    return(None)

