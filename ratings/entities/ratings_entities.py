from copy import deepcopy
from datetime import date
from typing import Optional



class TelevisionRating:
    """Television rating for one night, one timeslot, one show"""

    def __init__(self):
        """Initialize all attributes to None"""
        self.show_air_date: Optional[date] = None
        self.time_slot: Optional[str] = None
        self.show_name: Optional[str] = None
        self.rating: Optional[int] = None
        self.rating_18_49: Optional[float] = None
        self.household: Optional[float] = None
        self.household_18_49: Optional[float] = None
        self.rating_year: Optional[int] = None

    @property
    def show_air_date(self):
        return(self._show_air_date)

    @show_air_date.setter
    def show_air_date(self, show_air_date):
        if type(show_air_date) not in (date, type(None)):
            raise TypeError(
                "TelevisionRating - show_air_date datatype" +
                " must be a date")
        self._show_air_date = show_air_date


    @property
    def time_slot(self):
        return(self._time_slot)

    @time_slot.setter
    def time_slot(self, time_slot):
        if type(time_slot) not in (str, type(None)):
            raise TypeError(
                "TelevisionRating - time_slot datatype" +
                " must be a str")
        self._time_slot = time_slot


    @property
    def show_name(self):
        return(self._show_name)

    @show_name.setter
    def show_name(self, show_name):
        if type(show_name) not in (str, type(None)):
            raise TypeError(
                "TelevisionRating - show_name datatype" +
                " must be a str")
        self._show_name = show_name


    @property
    def rating(self):
        return(self._rating)

    @rating.setter
    def rating(self, rating):
        if type(rating) not in (int, type(None)):
            raise TypeError(
                "TelevisionRating - rating datatype" +
                " must be a int")
        self._rating = rating


    @property
    def rating_18_49(self):
        return(self._rating_18_49)

    @rating_18_49.setter
    def rating_18_49(self, rating_18_49):
        if type(rating_18_49) not in (int, type(None)):
            raise TypeError(
                "TelevisionRating - rating_18_49 datatype" +
                " must be a int")
        self._rating_18_49 = rating_18_49


    @property
    def household(self):
        return(self._household)

    @household.setter
    def household(self, household):
        if type(household) not in (float, type(None)):
            raise TypeError(
                "TelevisionRating - household datatype" +
                " must be a float")
        self._household = household


    @property
    def household_18_49(self):
        return(self._household_18_49)

    @household_18_49.setter
    def household_18_49(self, household_18_49):
        if type(household_18_49) not in (float, type(None)):
            raise TypeError(
                "TelevisionRating - household_18_49 datatype" +
                " must be a float")
        self._household_18_49 = household_18_49


    @property
    def rating_year(self):
        return(self._rating_year)

    @rating_year.setter
    def rating_year(self, rating_year):
        if type(rating_year) not in (int, type(None)):
            raise TypeError(
                "TelevisionRating - rating_year datatype" +
                " must be a int")
        self._rating_year = rating_year


class SecretConfig():
    """Any secrets and environment config"""
    def __init__(self):
        """Initialize all attributes to None"""
        self.reddit_client_secret = None
        self.reddit_client_id = None
        self.reddit_password = None
        self.reddit_username = None

    @property
    def reddit_client_id(self) -> Optional[str]:
        return(self._reddit_client_id)

    @reddit_client_id.setter
    def reddit_client_id(self, reddit_client_id: Optional[str]):
        if type(reddit_client_id) not in (
            str, type(None)):
            raise TypeError(
                "SecretConfig - reddit_client_id datatype " +
                "must be a str or None"
            )
        self._reddit_client_id = reddit_client_id


    @property
    def reddit_client_secret(self) -> Optional[str]:
        return(self._reddit_client_secret)

    @reddit_client_secret.setter
    def reddit_client_secret(self, reddit_client_secret: Optional[str]):
        if type(reddit_client_secret) not in (
            str, type(None)):
            raise TypeError(
                "SecretConfig - reddit_client_secret datatype " +
                "must be a str or None"
            )
        self._reddit_client_secret = reddit_client_secret

    @property
    def reddit_password(self) -> Optional[str]:
        return(self._reddit_password)

    @reddit_password.setter
    def reddit_password(self, reddit_password: Optional[str]):
        if type(reddit_password) not in (
            str, type(None)):
            raise TypeError(
                "SecretConfig - reddit_password datatype " +
                "must be a str or None"
            )
        self._reddit_password = reddit_password


    @property
    def reddit_username(self) -> Optional[str]:
        return(self._reddit_username)

    @reddit_username.setter
    def reddit_username(self, reddit_username: Optional[str]):
        if type(reddit_username) not in (
            str, type(None)):
            raise TypeError(
                "SecretConfig - reddit_username datatype " +
                "must be a str or None"
            )
        self._reddit_username = reddit_username

