
from datetime import datetime
import json
import unittest
from copy import deepcopy
from unittest.mock import MagicMock, patch
from urllib.request import Request

from fixtures.ratings_fixtures import (mock_oauth_token_response,
                                       mock_reddit_search_response,
                                       mock_secret_config)
from util.test_reddit_rating_config import (REDDIT_RATING_TABLE_2019,
                                            REDDIT_RATING_TABLE_2020)


class TestRatingsRepoBackend(unittest.TestCase):

    
    @patch("ratings.repo.ratings_repo_backend.urlopen")
    @patch("ratings.repo.ratings_repo_backend.get_oauth_token")
    @patch("ratings.repo.ratings_repo_backend.load_secret_config")
    def test_ratings_from_internet(
        self,
        load_secret_config_mock: MagicMock,
        get_oauth_token_mock: MagicMock,
        urlopen_mock: MagicMock
        ):
        """Parsing of TelevisionRatings entities"""
        from ratings.entities.ratings_entities import TelevisionRating
        from ratings.repo.ratings_repo_backend import (get_ratings_post,
                                                       ratings_from_internet)

        load_secret_config_mock.return_value = mock_secret_config()
        get_oauth_token_mock.return_value = mock_oauth_token_response()
        
        mock_api_response = MagicMock()
        mock_api_response.status.return_value = 200
        mock_api_response.read.return_value = (
            json.dumps(mock_reddit_search_response())
        )
        urlopen_mock.return_value.__enter__.return_value = (
            mock_api_response
        )


        television_ratings, unexpected_error = ratings_from_internet()



        self.assertEqual(
            110,
            len(television_ratings),
            msg=("\n\ncheck that one TelevisionRating " +
                 "is returned for each ratings post in " +
                 "mock_reddit_search_response return value"
            )
        )
        for television_rating in television_ratings:
            self.assertIsInstance(
                television_rating, TelevisionRating
            )
        self.assertIsNone(unexpected_error)
        load_secret_config_mock.assert_called()
        get_oauth_token_mock.assert_called()
        
        args, kwargs = urlopen_mock.call_args

        
        self.assertIsInstance(
            kwargs["url"], 
            Request
        )

        self.assertIsNotNone(
            len(kwargs["url"].headers["Authorization"]),
            msg="\n\n Not passing Authorization header"
        )
        

    @patch("ratings.repo.ratings_repo_backend.boto3")
    def test_persist_ratings(
            self,
            boto3_mock: MagicMock
        ):
        """TelevisionRatings entity sucessfully saved"""
        from fixtures.ratings_fixtures import get_mock_television_ratings
        from ratings.repo.ratings_repo_backend import persist_ratings

        table_mock = MagicMock()
        '''
        API response structure
        https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/dynamodb/client/put_item.html
        '''
        table_mock.put_item.return_value = {
            "Attributes": {}, "ConsumedCapacity": {}
        }

        boto3_mock.resource.return_value.Table.return_value = (
            table_mock
        )
        

        storage_error = persist_ratings(get_mock_television_ratings(5))

        self.assertEqual(table_mock.put_item.call_count, 5)
        self.assertIsNone(storage_error)


    @patch("boto3.client")
    def test_load_secret_config(self, 
        boto_client_mock: MagicMock):
        """Environment config successfully loaded"""
        from ratings.entities.ratings_entities import SecretConfig
        from ratings.repo.ratings_repo_backend import load_secret_config

        mock_reddit_username = "mock2"
        # pragma: allowlist nextline secret
        mock_reddit_password = "mock3"
        boto_client_mock.return_value.get_secret_value.return_value = (
        deepcopy(
            {
                "Name": "prod/v1/credentials",
                "SecretString": json.dumps(
                    {                
                        # pragma: allowlist nextline secret
                        "reddit_api_secret": "mock0",
                        # pragma: allowlist nextline secret
                        "reddit_api_key": "mock1",
                        "reddit_api_username": mock_reddit_username,
                        "reddit_api_password": mock_reddit_password
                    }
                )

            }
        )
        )


        secret_config = load_secret_config()

        get_secret_args, get_secret_kwargs = (
            boto_client_mock.return_value.get_secret_value.call_args
        )

        self.assertIsInstance(secret_config, SecretConfig)

        self.assertIn("SecretId", get_secret_kwargs.keys())

        
        
        populated_secret_properties = [
            attr_name for attr_name in dir(secret_config)
            if not attr_name.startswith("_")
            and getattr(secret_config, attr_name) is not None
        ]

        for populated_secret in populated_secret_properties:
            self.assertIsNotNone(
                getattr(secret_config, populated_secret),
                msg=f"\n\n secrets_config property {populated_secret}"
            )
        self.assertEqual(
            len(populated_secret_properties),
            4,
            msg="incorrect number of SecretConfig attributes populated"
        )
        
        self.assertEqual(
            secret_config.reddit_username,
            mock_reddit_username,
            msg="\n\ne2e bug where username not populated correctly"
        )
        self.assertEqual(
            secret_config.reddit_password,
            mock_reddit_password,
            msg="\n\ne2e bug where password not populated correctly"
        )


    def test_evaluate_ratings_post_title(self):
        """Happy path ratings in the title"""
        from ratings.repo.ratings_repo_backend import \
            evaluate_ratings_post_title

        valid_ratings_post_titles = [
            "Toonami Ratings for May 15th, 2021"
        ]
        for valid_ratings_title in valid_ratings_post_titles:

            with self.subTest(
                valid_ratings_title=valid_ratings_title
                ):
                self.assertTrue(
                    evaluate_ratings_post_title(
                        ratings_title=valid_ratings_title
                    )
                )


    def test_evaluate_ratings_post_title_invalid_title(self):
        """Unhappy path ratings not in title"""
        from ratings.repo.ratings_repo_backend import \
            evaluate_ratings_post_title

        invalid_ratings_post_titles = [
            "General News post",
            "Show announcement",
            "The Future Of Ratings | Toonami Faithful"
        ]
        for invalid_ratings_title in invalid_ratings_post_titles:

            with self.subTest(
                invalid_ratings_title=invalid_ratings_title
                ):
                self.assertFalse(
                    evaluate_ratings_post_title(
                        ratings_title=invalid_ratings_title
                    )
                )

    def test_get_ratings_post(self):
        """Tests that only reddit ratings news posts are returned
        """
        from ratings.repo.ratings_repo_backend import get_ratings_post
        '''
            loading a mock reddit api response to
            test if we are returning the correct number of
            ratings related posts
        '''
        
        ratings_post_list = get_ratings_post(
            mock_reddit_search_response()
        )
        '''
            Elements of the ["data"]["children"]
            list that are ratings posts
        '''
        self.assertEqual(ratings_post_list,
            [0, 4, 13, 17, 19, 20, 22, 23])
        



    def test_handle_table_clean(self):
        """HTML table to parsed dict"""
        from ratings.repo.ratings_repo_backend import handle_table_clean
        clean_saturday_ratings = handle_table_clean(
            REDDIT_RATING_TABLE_2020,
            rating_call_counter=0,
            ratings_title="Toonami Ratings for November 2nd, 2019"
        )

        '''
            ratings_occurred_on and YEAR should be the 
            same for each element of the dict
        '''
        for individual_saturday_show in clean_saturday_ratings:
            '''
                Using date format that aligns with
                historical ratings
            '''
            self.assertEqual(
                individual_saturday_show["ratings_occurred_on"],
                "2019-11-02"

            )
            '''
                Validate year is added as key to dict
            '''
            self.assertEqual(
                individual_saturday_show["YEAR"],
                2019
            )

        self.assertEqual(clean_saturday_ratings[2]["Viewers (000)"],
            "453"
        )
        self.assertEqual(
            len(clean_saturday_ratings), 7
        )
        '''
            Checking the value of the date parsed from the
            title for different variations

            ex: 1st, 2nd, 3rd, 5th, etc.
        '''
        clean_saturday_st = handle_table_clean(
            REDDIT_RATING_TABLE_2020,
            rating_call_counter=0,
            ratings_title="Toonami Ratings for December 21st, 2019"
        )
        '''
            ratings_occurred_on and YEAR should be the 
            same for each element of the dict
        '''
        for individual_saturday_show_st in clean_saturday_st:
            '''
                Using date format that aligns with
                historical ratings
            '''
            self.assertEqual(
                individual_saturday_show_st["ratings_occurred_on"],
                "2019-12-21"

            )
            '''
                Validate year is added as key to dict
            '''
            self.assertEqual(
                individual_saturday_show_st["YEAR"],
                2019
            )

        clean_saturday_th = handle_table_clean(
            REDDIT_RATING_TABLE_2020,
            rating_call_counter=0,
            ratings_title="Toonami Ratings for January 18th, 2020"
        )

        '''
            ratings_occurred_on and YEAR should be the 
            same for each element of the dict
        '''
        for individual_saturday_show_th in clean_saturday_th:
            '''
                Using date format that aligns with
                historical ratings
            '''
            self.assertEqual(
                individual_saturday_show_th["ratings_occurred_on"],
                "2020-01-18"

            )
            '''
                Validate year is added as key to dict
            '''
            self.assertEqual(
                individual_saturday_show_th["YEAR"],
                2020
            )


    def test_handle_table_body(self):
        """Tests dict from html body handler"""
        from bs4 import BeautifulSoup

        from ratings.repo.ratings_repo_backend import handle_table_body

        '''
            Creating BeautifulSoup object from
            a test reddit html table post
            and validating the handle_table_body
            function returns a list of ratings
        '''
        bs_obj = BeautifulSoup(
            REDDIT_RATING_TABLE_2019, "html.parser"
        )
        '''
            Stub of header columns to pass to
            handle_table_body
        '''
        header_columns = [
            "Time", "Show", "Viewers (000)",
            "18-49 Rating", "18-49 Views (000)"
        ]
        saturday_ratings = handle_table_body(
            bs_obj=bs_obj,
            header_columns=header_columns)

        self.assertEqual(
            saturday_ratings[0]["Time"],
            "11:00"
        )
        self.assertEqual(
            saturday_ratings[7]["18-49 Rating"],
            "0.12"
        )
        self.assertEqual(
            saturday_ratings[9]["Viewers (000)"],
            "282"
        )


    def test_handle_table_header(self):
        """Tests columns are retrieved from html table header
        """
        from bs4 import BeautifulSoup

        from ratings.repo.ratings_repo_backend import handle_table_header

        '''
            Creating BeautifulSoup object from
            a test reddit html table post
            and validating the handle_table_header
            function returns a list of column names
        '''
        bs_obj = BeautifulSoup(
            REDDIT_RATING_TABLE_2019, "html.parser"
        )
        header_columns = handle_table_header(bs_obj)

        self.assertEqual(header_columns,
            [
                "Time", "Show", "Viewers (000)",
                "18-49 Rating", "18-49 Views (000)"
            ]
        )


    @patch("ratings.repo.ratings_repo_backend.boto3")
    def test_persist_show_names(
            self,
            boto3_mock: MagicMock
        ):
        """TelevisionRatings unique show names saved"""
        from fixtures.ratings_fixtures import get_mock_television_ratings
        from ratings.repo.ratings_repo_backend import persist_show_names

        table_mock = MagicMock()
        '''
        API response structure
        https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/dynamodb/client/put_item.html
        '''
        table_mock.put_item.return_value = {
            "Attributes": {}, "ConsumedCapacity": {}
        }

        boto3_mock.resource.return_value.Table.return_value = (
            table_mock
        )
        
        mock_tv_ratings = get_mock_television_ratings(5)
        mock_tv_ratings[1].show_name = "duplicate show"
        mock_tv_ratings[3].show_name = "duplicate show"

        persist_show_names(mock_tv_ratings)


        self.assertEqual(table_mock.put_item.call_count, 4)
        boto3_mock.resource.return_value.Table.assert_called_once_with(
            "prod_toonami_analytics"
        )
        

    def test_standardize_time(
            self
        ):
        """Not perfect but consistent times"""
        from ratings.repo.ratings_repo_backend import standardize_time


        self.assertEqual(
            standardize_time("9:00 PM"),
            "9:00"
        )
        self.assertEqual(
            standardize_time("9:00 pm"),
            "9:00"
        )
        self.assertEqual(
            standardize_time("12:00 am"),
            "12:00a"
        )
        self.assertEqual(
            standardize_time("12:00 AM"),
            "12:00a"
        )
        self.assertEqual(
            standardize_time("12am"),
            "12a"
        )
        self.assertEqual(
            standardize_time("3 a"),
            "3a"
        )
        self.assertEqual(
            standardize_time("10:00 pm"),
            "10:00"
        )
        self.assertEqual(
            standardize_time("1:30 a"),
            "1:30a"
        )
        self.assertEqual(
            standardize_time("12 Am"),
            "12a"
        )
        self.assertEqual(
            standardize_time("11:30pM"),
            "11:30"
        )
        self.assertEqual(
            standardize_time("9pm"),
            "9"
        )

        
    @patch("ratings.repo.ratings_repo_backend.urlopen")
    def test_get_oauth_token_builtins(
            self, 
            urlopen_mock: MagicMock
        ):
        """using only built in python libraries to load oauth token"""
        from ratings.repo.ratings_repo_backend import get_oauth_token

        
        (
            urlopen_mock.return_value.__enter__.
            return_value.getcode.return_value
        ) = 200

        (
            urlopen_mock.return_value.__enter__.
            return_value.read.return_value
        ) = json.dumps(
            mock_oauth_token_response()
        ).encode("utf-8")
        
        

        oauth_dict_response = get_oauth_token(
            "mockval0",
            "mockval1"
        )


        self.assertIsNotNone(
            oauth_dict_response["access_token"]
        )


    def test_parse_float(self):
        """float parsing logic that handles random characters"""
        from ratings.repo.ratings_repo_backend import parse_float


        self.assertEqual(
            parse_float("<0.17"),
            .17
        )


    @unittest.skip("skip until implementation")
    def test_ratings_title_override_manaual_override(self):
        """Manual override of ratings title"""
        from ratings.repo.ratings_repo_backend import ratings_title_override

        
        self.assertIsInstance(
            ratings_title_override(
                "July 22 Toonami Ratings (no numbers available for July 29)"
            ),
            datetime
        )

