from bs4 import BeautifulSoup
from copy import deepcopy
from datetime import datetime
from unittest.mock import MagicMock
from unittest.mock import patch

import json
import os
import requests
import unittest


from util.test_reddit_rating_config import MOCK_CLEAN_RATINGS_LIST
from util.test_reddit_rating_config import MOCK_RATINGS_LIST
from util.test_reddit_rating_config import REDDIT_RATING_TABLE_2019
from util.test_reddit_rating_config import REDDIT_RATING_TABLE_2020


class IntegrationRedditApi(unittest.TestCase):
    """Integration test for the reddit api pull
    """
    def test_get_client_secrets(self):
        """Integration test for the get_client_secrets function

            Parameters
            ----------

            Returns
            -------

            Raises
            ------
        """
        from scripts.reddit_ratings import get_client_secrets

        reddit_client_key, reddit_client_secret = get_client_secrets()

        self.assertEqual(type(reddit_client_key), str)

        self.assertEqual(type(reddit_client_secret), str)






    def test_get_oath_token(self):
        """Integration test for the oath token 
            Ensures it is returned from reddit api

            Parameters
            ----------

            Returns
            -------

            Raises
            ------
        """

        from scripts.reddit_ratings import get_oauth_token
        from scripts.reddit_ratings import get_client_secrets
        reddit_client_key, reddit_client_secret = get_client_secrets()

        oauth_token = get_oauth_token(
            client_key=reddit_client_key,
            client_secret=reddit_client_secret
        )
        self.assertIsNotNone(oauth_token["access_token"])






class RedditApi(unittest.TestCase):
    """Testing the reddit api pull unit tests only

        Parameters
        ----------

        Returns
        -------

        Raises
        ------
    """
    @classmethod
    def setUpClass(cls):
        """Unitest function that is run once for the class

        """
        '''
            How many news posts the client main function is using
        '''
        cls.MAIN_FUNCTION_POST_COUNT = 25
        os.environ["DYNAMODB_TABLE_NAME"] = "dev_toonami_ratings"

        if os.environ.get("AWS_LAMBDA_FUNCTION_NAME") is None:
            print("RedditAPI setUpClass - setting AWS_LAMBDA_FUNCTION_NAME environment variable")
            os.environ["AWS_LAMBDA_FUNCTION_NAME"] = "dev-ratings-backend-lambda-poll"
        
        '''
            Assigns a class attribute which is 
            a dict that represents news posts
        '''
        with open("util/news_flair_fixture.json", "r") as news_flair:
            cls.news_flair_fixture = json.load(news_flair)
        
        cls.oauth_token_fixture = {
            "access_token": "FIXTURETOKEN123",
            "token_type": "bearer",
            "expires_in": 3600,
            "scope": "*"
        }

        cls.valid_column_names = [
            "PERCENTAGE_OF_HOUSEHOLDS",
            "PERCENTAGE_OF_HOUSEHOLDS_AGE_18_49",
            "RATINGS_OCCURRED_ON",
            "SHOW",
            "TIME", 
            "TOTAL_VIEWERS", 
            "TOTAL_VIEWERS_AGE_18_49"

        ]

    @patch("scripts.reddit_ratings.put_show_names")
    @patch("scripts.reddit_ratings.handle_ratings_insertion")
    @patch("scripts.reddit_ratings.ratings_iteration")
    def test_main(self, ratings_iteration_mock,
        handle_ratings_iteration_mock, put_show_names_mock):
        '''Test for main function

            Parameters
            ----------
            ratings_iteration_mock : unittest.mock.MagicMock
                Mock object to make sure the reddit api is 
                not called

            handle_ratings_iteration_mock : unittest.mock.MagicMock
                Mock object used to ensure no logging is setup
                for the test

            Returns
            -------

            Raises
            ------
        '''
        from scripts.reddit_ratings import main

        ratings_iteration_mock.return_value = MOCK_RATINGS_LIST

        main()

        ratings_iteration_mock.assert_called_once_with(
            number_posts=self.MAIN_FUNCTION_POST_COUNT
        )

        self.assertEqual(
            handle_ratings_iteration_mock.call_count,
            1
        )

        handle_ratings_iteration_mock.assert_called_once_with(
            all_ratings_list=MOCK_RATINGS_LIST,
            table_name="dev_toonami_ratings"
        )

        put_show_names_args, put_show_names_kwargs = put_show_names_mock.call_args
        self.assertEqual(put_show_names_mock.call_count, 1)
        self.assertEqual(put_show_names_kwargs["table_name"], "dev_toonami_analytics")
        self.assertEqual(type(put_show_names_kwargs["all_ratings_list"]), list)
        self.assertEqual(type(put_show_names_kwargs["all_ratings_list"][0]), dict)


    @patch("boto3.client")
    def test_get_boto_clients_no_region(self, boto3_client_mock):
        '''Tests outgoing boto3 client generation when no region is passed

            Parameters
            ----------
            boto3_client_mock : unittest.mock.MagicMock
                Mock object used to patch
                AWS Python SDK

            Returns
            -------


            Raises
            ------
        '''
        from scripts.reddit_ratings import get_boto_clients

        test_service_name="lambda"
        get_boto_clients(resource_name=test_service_name)


        '''
            Default region is us-east-1 for 
            get_boto_clients
        '''
        boto3_client_mock.assert_called_once_with(
            service_name=test_service_name,
            region_name="us-east-1"
        )

    def test_sort_ratings_occurred_on(self):
        """Tests that we are able to sort when the ratings occurred

            Parameters
            ----------

            Returns
            -------

            Raises
            ------
        """
        from scripts.reddit_ratings import sort_ratings_occurred_on

        ratings_occurred_on = sort_ratings_occurred_on(
            ratings_list=MOCK_RATINGS_LIST
        )

        '''
            The ratings_occurred_on should be a descending
            list based on date
        '''
        self.assertEqual(
            ratings_occurred_on,
            [
                "2020-05-23",
                "2020-05-16",
                "2020-05-09",
                "2020-05-02"
            ]
        )




    def test_get_boto_clients_table_resource(self):
        """Tests getting a dynamodb table resource from get_boto_clients

            Parameters
            ----------

            Returns
            -------


            Raises
            ------
        """
        from scripts.reddit_ratings import get_boto_clients

        dynamodb_functions_to_test = [
            "put_item",
            "query",
            "scan"
        ]
        '''
            boto3 does not make any calls to 
            aws until you use the resource/client
        '''
        test_service_name = "dynamodb"
        test_table_name = "fake_ddb_table"

        dynamodb_client, dynamodb_table = get_boto_clients(
            resource_name=test_service_name, 
            table_name=test_table_name
        )


        '''
            Testing the objects returned have the needed functions
        '''
        self.assertIn(
            "describe_table",
            dir(dynamodb_client)
        )

        '''
            ensuring we have all needed functions for
            working with a table
        '''
        for dynamodb_function in dynamodb_functions_to_test:
            self.assertIn(
                dynamodb_function,
                dir(dynamodb_table)
            )        





    @patch("boto3.client")
    def test_get_boto_clients_with_region(self, boto3_client_mock):
        '''Tests outgoing boto3 client generation when a region is passed

            Parameters
            ----------
            boto3_client_mock : unittest.mock.MagicMock
                Mock object used to patch
                AWS Python SDK

            Returns
            -------


            Raises
            ------
        '''
        from scripts.reddit_ratings import get_boto_clients

        test_service_name = "s3"
        test_region_name = "us-west-1"

        
        get_boto_clients(
            resource_name=test_service_name,
            region_name=test_region_name
        )

        '''
            patch outgoing args should match
            wrapper function
        '''
        boto3_client_mock.assert_called_once_with(
            service_name=test_service_name,
            region_name=test_region_name
        )

    @patch("requests.post")
    def test_get_oauth_token_unit(self, requests_post_mock):
        '''Unittest for get_oauth_token

            Parameters
            ----------
            requests_post_mock : unittest.mock.MagicMock
                Mock object used to patch http post to reddit
                api client service

            Returns
            -------

            Raises
            ------
        '''
        from scripts.reddit_ratings import get_oauth_token

        '''
            json returned by http post
            will be the class oauth_token fixture
        '''
        json_mock = MagicMock()

        requests_post_mock.return_value = json_mock

        json_mock.json.return_value = self.oauth_token_fixture



        test_client_key="fakeid"
        test_client_secret="fakesecret"

        oauth_token = get_oauth_token(
            client_key=test_client_key, 
            client_secret=test_client_secret
        )

        '''
            Testing the outbound HTTP POST arguements
            to the reddit token endpoint
        '''
        requests_post_mock.assert_called_once_with(
            url="https://www.reddit.com/api/v1/access_token",
            auth=(test_client_key, test_client_secret),
            data={"grant_type":"client_credentials"},
            headers={
                "user-agent":"Lambda:toonamiratings:v1.0 (by /u/toonamiratings)"
            }
        )

        self.assertEqual(
            oauth_token,
            self.oauth_token_fixture
        )

    def test_evaluate_ratings_post_title(self):
        """Happy path ratings in the title
        """
        from scripts.reddit_ratings import _evaluate_ratings_post_title

        valid_ratings_post_titles = [
            "Toonami Ratings for May 15th, 2021"
        ]
        for valid_ratings_title in valid_ratings_post_titles:

            with self.subTest(valid_ratings_title=valid_ratings_title):
                self.assertTrue(
                    _evaluate_ratings_post_title(ratings_title=valid_ratings_title)
                )


    def test_evaluate_ratings_post_title_invalid_title(self):
        """Unhappy path ratings not in title
        """
        from scripts.reddit_ratings import _evaluate_ratings_post_title

        invalid_ratings_post_titles = [
            "General News post",
            "Show announcement",
            "The Future Of Ratings | Toonami Faithful"
        ]
        for invalid_ratings_title in invalid_ratings_post_titles:

            with self.subTest(invalid_ratings_title=invalid_ratings_title):
                self.assertFalse(
                    _evaluate_ratings_post_title(ratings_title=invalid_ratings_title)
                )

    def test_get_ratings_post(self):
        """Tests that only reddit ratings news posts are returned

            Parameters
            ----------


            Returns
            -------

            Raises
            ------
        """
        from scripts.reddit_ratings import get_ratings_post
        '''
            loading a mock reddit api response to
            test if we are returning the correct number of
            ratings related posts
        '''
        with open("util/reddit_search_response.json") as static_response:
            mock_response = json.load(static_response)
            ratings_post_list = get_ratings_post(mock_response)
        '''
            Elements of the ["data"]["children"]
            list that are ratings posts
        '''
        self.assertEqual(ratings_post_list,
            [0, 4, 13, 17, 19, 20, 22, 23])

    def test_handle_table_header(self,
        mock_rating_table=REDDIT_RATING_TABLE_2019):
        """Tests columns are retrieved from html table header

            Parameters
            ----------
            mock_rating_table : str
                Example of an html table returned by the
                reddit api

            Returns
            -------

            Raises
            ------
        """
        from scripts.reddit_ratings import handle_table_header

        '''
            Creating BeautifulSoup object from
            a test reddit html table post
            and validating the handle_table_header
            function returns a list of column names
        '''
        bs_obj = BeautifulSoup(mock_rating_table, "html.parser")
        header_columns = handle_table_header(bs_obj)

        self.assertEqual(header_columns,
            [
                "Time", "Show", "Viewers (000)",
                "18-49 Rating", "18-49 Views (000)"
            ]
        )

    def test_handle_table_body(self,
        mock_rating_table=REDDIT_RATING_TABLE_2019):
        """Tests dict from html body handler

            Parameters
            ----------
            mock_rating_table : str
                Example of an html table returned by the
                reddit api

            Returns
            -------

            Raises
            ------
        """
        from scripts.reddit_ratings import handle_table_body

        '''
            Creating BeautifulSoup object from
            a test reddit html table post
            and validating the handle_table_body
            function returns a list of ratings
        '''
        bs_obj = BeautifulSoup(mock_rating_table, "html.parser")
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



    def test_handle_table_clean(self,
        mock_rating_table=REDDIT_RATING_TABLE_2020):
        """Tests cleaning of ratings data

            Parameters
            ----------
            mock_rating_table : str
                Example of an html table returned by the
                reddit api

            Returns
            -------

            Raises
            ------
        """
        from scripts.reddit_ratings import handle_table_clean
        clean_saturday_ratings = handle_table_clean(mock_rating_table,
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
        clean_saturday_st = handle_table_clean(mock_rating_table,
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

        clean_saturday_th = handle_table_clean(mock_rating_table,
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




    def test_iterate_handle_table_clean(self):
        """Tests iteration of ratings data with empty list

            Parameters
            ----------

            Returns
            -------

            Raises
            ------
        """
        from scripts.reddit_ratings import iterate_handle_table_clean

        
        '''
            Checking the iteration returns 12 seperate ratings dicts
        '''
        all_ratings_list = iterate_handle_table_clean(
            news_flair_posts=self.news_flair_fixture,
            ratings_post_list=[0,3],
            ratings_list_to_append=[]
        )
        self.assertEqual(len(all_ratings_list),
            12
        )

        
    def test_iterate_handle_table_clean_list_populated(self):
        """Tests iteration of ratings data with list that has ratings

            Parameters
            ----------

            Returns
            -------

            Raises
            ------
        """
        from scripts.reddit_ratings import iterate_handle_table_clean

        existing_ratings_list =[
            {
                "Time": "12:00a",
                "Show": "My Hero Academia (r)", 
                "Viewers (000)": "590", 
                "18-49 Rating": "0.29", 
                "18-49 Views (000)": "380", 
                "ratings_occurred_on": "2020-04-25"
            },
            {
                "Time": "11:30",
                "Show": "ExampleShow1", 
                "Viewers (000)": "59", 
                "18-49 Rating": "0.14", 
                "18-49 Views (000)": "380", 
                "ratings_occurred_on": "2020-05-02"
            }            

        ]
        '''
            Checking the iteration returns 12 seperate ratings dicts
        '''
        all_ratings_list = iterate_handle_table_clean(
            news_flair_posts=self.news_flair_fixture,
            ratings_post_list=[0,3],
            ratings_list_to_append=existing_ratings_list
        )

        self.assertEqual(len(all_ratings_list),
            14
        ) 

        '''
            Checking that the primary keys used are unique

            set(["x", "x"])
            
            returns unique values
            {"x"}
        '''
        primary_key_list = []
        for show_rating in all_ratings_list:
            '''
                Concatening the two fields that should be 
                unique
            '''
            primary_key_list.append(
                str(show_rating["Time"]) + 
                str(show_rating["ratings_occurred_on"])
            )

        self.assertEqual(
            14,
            len(set(primary_key_list))
        )

    @patch("scripts.reddit_ratings.get_oauth_token")
    @patch("scripts.reddit_ratings.get_news_flair")
    def test_ratings_iteration(self, news_flair_patch, oauth_token_mock):
        """Tests that we can iterate over most recent posts

            Parameters
            ----------
            news_flair_patch : unittest.mock.MagicMock
                Mock object used to test how often
                get_news_flair is called

            oauth_token_mock : unittest.mock.MagicMock
                Mock object used to patch
                get_oauth_token

            Returns
            -------

            Raises
            ------
        """
        from scripts.reddit_ratings import ratings_iteration

        '''
            setting return values for mock
        '''
        oauth_token_mock.return_value = self.oauth_token_fixture

        news_flair_patch.return_value = self.news_flair_fixture
        
        all_ratings_posts = ratings_iteration()
        '''
            Testing that the get_news_flair
            meaning we are only looking for the most recent ratings
        '''
        self.assertEqual(news_flair_patch.call_count,
            1
        )

        self.assertEqual(oauth_token_mock.call_count,
            1
        )

        news_flair_patch.assert_called_once_with(
            access_token="FIXTURETOKEN123",
            posts_to_return=10
        )

        self.assertEqual(
            all_ratings_posts[5]["Time"],
            "2:30a"
        )

        self.assertEqual(
            12,
            len(all_ratings_posts)
        )

    @patch("scripts.reddit_ratings.get_ratings_post")
    @patch("scripts.reddit_ratings.get_oauth_token")
    @patch("scripts.reddit_ratings.get_news_flair")
    def test_ratings_iteration_historical(self, news_flair_patch,
         oauth_token_mock, get_ratings_post_mock):
        """Test for historical rating iterations

            Parameters
            ----------
            news_flair_patch : unittest.mock.MagicMock
                Mock object used to test how often
                get_news_flair is called

            oauth_token_mock : unittest.mock.MagicMock
                Mock object used to patch
                get_oauth_token

            get_ratings_post_mock : unittest.mock.MagicMock
                Mock object used to patch
                get_ratings_post

            Returns
            -------

            Raises
            ------
        """
        from scripts.reddit_ratings import ratings_iteration

        '''
            Used to make sure the posts are iterated the 
            correct number of times
        '''
        news_flair_patch.return_value = self.news_flair_fixture


        get_ratings_post_mock.return_value = [0,3]

        all_ratings_posts = ratings_iteration(number_posts=100)

        '''
            Should be called 4 times each if 
            100 posts are being iterated
        '''
        self.assertEqual(
            news_flair_patch.call_count,
            4
        )

        self.assertEqual(
            get_ratings_post_mock.call_count,
            4
        )        

    @patch("scripts.reddit_ratings.get_boto_clients")
    def test_handle_ratings_insertion_no_match(self, get_boto_clients_patch):
        """Tests outbound arguements for ratings put item in dynamodb
            mocks if the ratings in MOCK_CLEAN_RATINS_LIST 
            are not already in table

            Parameters
            ----------
            get_ratings_post_mock : unittest.mock.MagicMock
                Patch to return boto3 dynamodb resource


            Returns
            -------

            Raises
            ------
        """
        from scripts.reddit_ratings import handle_ratings_insertion

        '''
            Mocking the clients
        '''
        dynamo_client_mock = MagicMock()

        dynamo_table_mock = MagicMock()

        '''
            Mocking not having the given week night in the 
            ratings
        '''
        dynamo_table_mock.query.return_value = {
            "Items":[]
        }


        '''
            mocking a function that has two return values
        '''
        get_boto_clients_patch.return_value = [
            dynamo_client_mock, dynamo_table_mock
        ]

        handle_ratings_insertion(
            all_ratings_list=MOCK_CLEAN_RATINGS_LIST,
            table_name="dev_toonami_ratings"
        )


        '''
            the query function should be called 
            4 times, once for each unique ratings_occurred_on
            in MOCK_CLEAN_RATINGS_LIST
        '''
        self.assertEqual(
            dynamo_table_mock.query.call_count,
            4
        )
        
        self.assertEqual(
            dynamo_table_mock.batch_writer.call_count,
            4
        )


        '''
            with context manager calls the __enter__()
            function of the mock

            One call for each item
        '''
        self.assertEqual(
            dynamo_table_mock.batch_writer().__enter__().put_item.call_count,
            24
        )


    @patch("scripts.reddit_ratings.get_boto_clients")
    def test_handle_ratings_insertion_with_match(self, get_boto_clients_patch):
        """Tests outbound arguements for ratings put item in dynamodb
            mocks if the ratings in MOCK_CLEAN_RATINS_LIST 
            are already in table

            Parameters
            ----------
            get_ratings_post_mock : unittest.mock.MagicMock
                Patch to return boto3 dynamodb resource


            Returns
            -------

            Raises
            ------
        """
        from scripts.reddit_ratings import handle_ratings_insertion

        '''
            Mocking the clients
        '''
        dynamo_client_mock = MagicMock()

        dynamo_table_mock = MagicMock()

        '''
            Mocking not having the given week night in the 
            ratings
        '''
        dynamo_table_mock.query.return_value = {
            "Items":[
                {
                    "TIME": "2:30a", 
                    "SHOW": "Naruto: Shippuden", 
                    "TOTAL_VIEWERS": "336", 
                    "PERCENTAGE_OF_HOUSEHOLDS_AGE_18_49": "0.19",
                    "TOTAL_VIEWERS_AGE_18_49": "241",
                    "RATINGS_OCCURRED_ON": "2020-05-09",
                    "IS_RERUN": None
                }
            ]
        }


        '''
            mocking a function that has two return values
        '''
        get_boto_clients_patch.return_value = [
            dynamo_client_mock, dynamo_table_mock
        ]

        handle_ratings_insertion(
            all_ratings_list=MOCK_CLEAN_RATINGS_LIST,
            table_name="dev_toonami_ratings"
        )


        '''
            the query function is only called once 
            because it returns after checking the most recent rating
        '''
        self.assertEqual(
            dynamo_table_mock.query.call_count,
            1
        )


        '''
            everything else should be skipped
        '''
        self.assertEqual(
            dynamo_table_mock.batch_writer.call_count,
            0
        )





    def test_dict_key_mapping(self):
        """Validating mapping of rating keys to dynamodb columns

        """
        from scripts.reddit_ratings import dict_key_mapping
        original_json_list_example = [
            [
                {
                    "Time": "12",
                    "Total": "1036",
                    "Household": "0.70",
                    "ATotal": "630",
                    "AHousehold": "0.20",
                    "Show": "sample show",
                    "Date": "2014-09-06"

                }
            ],
            [
                {
                    "time": "12",
                    "Total": "1036",
                    "Household": "0.70",
                    "ATotal": "630",
                    "AHousehold": "0.20",
                    " proGram ": "sample show",
                    "Date": "2014-09-06"

                }
            ]

        ]

        for json_show_list in original_json_list_example:
            clean_original_values = dict_key_mapping(
                pre_clean_ratings_keys=json_show_list
            )
            with self.subTest(clean_original_values=clean_original_values):
                '''
                    Iterates first over each dict in the list
                    then over each key to validate all keys are 
                    in the dynamodb list 
                '''
                for cleaned_show_dict in clean_original_values:
                    '''
                        Making sure the unique key values is 7
                    '''
                    self.assertEqual(
                        len(tuple(cleaned_show_dict.keys())),
                        7
                    )
                    for cleaned_key in cleaned_show_dict.keys():
                        self.assertIn(cleaned_key, self.valid_column_names)
                        self.assertTrue(cleaned_key.isupper())


    def test_dict_key_mapping_unmapped_column(self):
        """KeyError raised when a column name is not mapped
        """
        from scripts.reddit_ratings import dict_key_mapping
        '''
            list of dicts passed to dict_key_mapping
        '''
        ratings_post_original_headers = [
            [
                {
                    "Time": "12",
                    "Total": "1036",
                    "Household": "0.70",
                    "ATotal": "630",
                    "AHousehold": "0.20",
                    "Show": "sample show",
                    "Date": "2014-09-06",
                    "unmappedColumn": "-1"

                }
            ],
            [
                {
                    "Househld": "0.70",
                    "Time": "12",
                    "Total": "1036",
                    "ATotal": "630",
                    "AHousehold": "0.20",
                    "Show": "sample show",
                    "Date": "2014-09-06"

                }
            ], [
                {
                    "Time": "12",
                    "Total": "1036",
                    "Household": "0.70",
                    "Show": "sample show",
                    "Weekly Show Time": "2014-09-06",

                }
            ]


        ]
        '''
            Message that should be raised in KeyError
        '''
        parameter_key_mapping = [
            "unmappedcolumn",
            "househld",
            "Weekly Show Time".lower()
        ]
        for original_headers, key_error_message in zip(
                ratings_post_original_headers, parameter_key_mapping):
            with self.subTest(
                    original_headers=original_headers,
                    key_error_message=key_error_message
                ):
                self.assertRaisesRegex(
                    KeyError, 
                    key_error_message, 
                    dict_key_mapping, 
                    pre_clean_ratings_keys=original_headers
                )
            
    def test_dict_key_mapping_recent(self):
        """Validates recent ratings keys using MOCK_RATINGS_LIST

            Parameters
            ----------

            Returns
            -------

            Raises
            ------
        """
        from scripts.reddit_ratings import dict_key_mapping


        clean_original_values = dict_key_mapping(
            pre_clean_ratings_keys=MOCK_RATINGS_LIST
        )

        '''
            Iterates first over each dict in the list
            then over each key to validate all keys are 
            in the dynamodb list 
        '''
        for cleaned_show_dict in clean_original_values:
            '''
                Making sure the unique key values is 5 or 
                6 for MOCK_RATING_LIST
            '''
            self.assertIn(
                len(tuple(cleaned_show_dict.keys())),
                [5, 6]
            )
            for cleaned_key in cleaned_show_dict.keys():
                '''
                    Making sure all keys are in the list
                    and all values are upper case
                '''
                self.assertIn(cleaned_key, self.valid_column_names)

                self.assertTrue(cleaned_key.isupper())

    def test_clean_dict_value(self):
        """Validates handling of bad ratings data

            Parameters
            ----------

            Returns
            -------

            Raises
            ------
        """
        from scripts.reddit_ratings import clean_dict_value

        list_with_rerun_and_bad_household = [
            {
                "TIME": "12",
                "TOTAL_VIEWERS": "1036",
                "PERCENTAGE_OF_HOUSEHOLDS": "0.70",
                "TOTAL_VIEWERS_AGE_18_49": "630",
                "PERCENTAGE_OF_HOUSEHOLDS_AGE_18_49": "9.99",
                "SHOW": "sample show",
                "RATINGS_OCCURRED_ON": "2014-09-06"

            },
            {
                "TIME": "12:00a", 
                "SHOW": "My Hero Academia (r)", 
                "TOTAL_VIEWERS": "590", 
                "PERCENTAGE_OF_HOUSEHOLDS_AGE_18_49": "0.29", 
                "TOTAL_VIEWERS_AGE_18_49": "380", 
                "RATINGS_OCCURRED_ON": "2020-05-09"
            },{
                "TIME": "12",
                "TOTAL_VIEWERS": "1036",
                "PERCENTAGE_OF_HOUSEHOLDS": "0.70",
                "TOTAL_VIEWERS_AGE_18_49": "630",
                "SHOW": "sample show without adult household (r",
                "RATINGS_OCCURRED_ON": "2014-09-06"

            }
        ]
        clean_ratings_list = clean_dict_value(
            ratings_values_to_clean=list_with_rerun_and_bad_household
        )


        '''
            Testing that household rating value of 9.99 
            is not returned in dict
        '''
        with self.assertRaises(KeyError, msg="PERCENTAGE_OF_HOUSEHOLDS_AGE_18_49"):
            self.assertIsNone(clean_ratings_list[0]["PERCENTAGE_OF_HOUSEHOLDS_AGE_18_49"])
 

        '''
            Validating that IS_RERUN is not returned
            for a Show without reruns
        '''
        with self.assertRaises(KeyError, msg="IS_RERUN"):
            self.assertIsNone(clean_ratings_list[0]["IS_RERUN"])

        '''
            Testing string split and 
            new key for dict
        '''
        self.assertEqual(
            clean_ratings_list[1]["SHOW"],
            "My Hero Academia"
        )
        self.assertTrue(clean_ratings_list[1]["IS_RERUN"]) 

        '''
            Testing that a show is only modified if (r) is 
            in the show name
        '''
        self.assertEqual(
            clean_ratings_list[2]["SHOW"],
            "sample show without adult household (r"
        )
        '''
            Validating that IS_RERUN is not returned
            for a Show without reruns
        '''
        with self.assertRaises(KeyError, msg="IS_RERUN"):        
            self.assertIsNone(clean_ratings_list[2]["IS_RERUN"])     


    def test_clean_dict_value_time(self):
        """Validates time cleaning logic
        """
        from scripts.reddit_ratings import clean_dict_value
        ratings_time_list = deepcopy(MOCK_CLEAN_RATINGS_LIST)
        correct_time_mapping = [
            {
                "original_time": "12am",
                "clean_time": "12a"
            },
            {
                "original_time": "3 a",
                "clean_time": "3a"
            },
            {
                "original_time": "10:00 pm",
                "clean_time": "10:00"
            },
            {
                "original_time": "1:30 a",
                "clean_time": "1:30a"
            },
            {
                "original_time": "12 Am",
                "clean_time": "12a"
            },
            {
                "original_time": "11:30pM",
                "clean_time": "11:30"
            },
            {
                "original_time": "9pm",
                "clean_time": "9"
            }


        ]

        for time_to_check in correct_time_mapping:

            with self.subTest(time_to_check=time_to_check):
                '''
                    assign original TIME
                '''
                for show_ratings in ratings_time_list:
                    show_ratings["TIME"] = time_to_check["original_time"]
                
                clean_dict_value(ratings_values_to_clean=ratings_time_list)

                '''
                    validate clean output time
                '''
                for show_ratings in ratings_time_list:
                    self.assertEqual(show_ratings["TIME"], time_to_check["clean_time"])
                
    @patch("scripts.reddit_ratings.get_boto_clients")
    def test_put_show_names(self, get_boto_clients_mock):
        """Tests the put_item call for show names
        """
        from scripts.reddit_ratings import put_show_names

        '''
            Mocking the clients
        '''
        dynamo_client_mock = MagicMock()

        dynamo_table_mock = MagicMock()

        batch_insert_mock = MagicMock()

        put_item_mock = MagicMock()
        
        '''
            dynamo_table.batch_writer().__enter__().put_item() mock
            simulating using a with block
        '''
        dynamo_table_mock.batch_writer.return_value.__enter__.return_value = batch_insert_mock
        
        '''
            dynamo_table.batch_writer().__enter__().put_item() mock
            simulating using a with block
        '''
        batch_insert_mock.put_item = put_item_mock

        get_boto_clients_mock.return_value = [dynamo_client_mock, dynamo_table_mock]


        put_show_names(
            all_ratings_list=MOCK_CLEAN_RATINGS_LIST,
            table_name="mock_table_name"
        )
        all_show_names = [show["SHOW"] for show in MOCK_CLEAN_RATINGS_LIST]
        
        unique_show_names = set(all_show_names)
        self.assertEqual(put_item_mock.call_count, len(unique_show_names))

        '''
            validate outgoing put_item call has a show_name from
            the list of unique_show_names
        '''
        for put_item_call in put_item_mock.call_args_list:
            put_item_args, put_item_kwargs = put_item_call
            self.assertEqual(put_item_kwargs["Item"]["PK"], "ratings#showName")
            self.assertIn(put_item_kwargs["Item"]["SK"], unique_show_names)
        
class LambdaHandler(unittest.TestCase):
    """Tests specific to when the script is run from a lambda
        function

        Parameters
        ----------

        Returns
        -------

        Raises
        ------
    """
    @classmethod
    def setUpClass(cls):
        """Unitest function that is run once for the class

            Parameters
            ----------

            Returns
            -------

            Raises
            ------
        """
        os.environ["AWS_LAMBDA_FUNCTION_NAME"] = "dev"
        '''
            Assigns a class attribute which is 
            a dict that represents news posts
        '''
        with open("util/lambda_cw_event.json", "r") as news_flair:
            cls.lambda_event_fixture = json.load(news_flair)

    @patch("logging.getLogger")
    @patch("scripts.reddit_ratings.main")
    def test_lambda_handler_event(self, main_mock, 
        getLogger_mock):
        """Tests passing sample event to lambda_handler

            Parameters
            ----------
            main_mock : unittest.mock.MagicMock
                Mock object used to patch the main function

            getLogger_mock : unittest.mock.MagicMock
                Mock object used to patch get_logger for lambda handler

            Returns
            -------

            Raises
            ------
        """
        from scripts.reddit_ratings import lambda_handler

        lambda_handler(
            event=self.lambda_event_fixture,
            context={}
        )

        self.assertEqual(
            getLogger_mock.call_count,
            1
        )

        '''
            Testing call count and args passed
        '''
        self.assertEqual(
            main_mock.call_count,
            1
        )



if __name__ == "__main__":
    unittest.main()
