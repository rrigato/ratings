from bs4 import BeautifulSoup
from datetime import datetime
from unittest.mock import MagicMock
from unittest.mock import patch

import json
import logging
import os
import requests
import unittest



from util.test_reddit_rating_config import MOCK_RATINGS_LIST
from util.test_reddit_rating_config import REDDIT_RATING_TABLE_2019
from util.test_reddit_rating_config import REDDIT_RATING_TABLE_2020


class IntegrationRedditApi(unittest.TestCase):
    """Integration test for the reddit api pull

        Parameters
        ----------

        Returns
        -------

        Raises
        ------
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

    def test_get_news_flair(self):
        """Tests that we are retriving posts with a news flair

            Parameters
            ----------


            Returns
            -------

            Raises
            ------
        """
        from scripts.reddit_ratings import get_client_secrets
        from scripts.reddit_ratings import get_news_flair

        from scripts.reddit_ratings import get_oauth_token

        reddit_client_key, reddit_client_secret = get_client_secrets()

        '''
            Getting an Oauth token and testing for
            a specific fullname which is a unique
            identifier for a given reddit api object
            which ensures the same post will be returned
            each time
        '''
        oauth_token = get_oauth_token(
            client_key=reddit_client_key,
            client_secret=reddit_client_secret
        )
        '''
            The fullname will anchor this search to
            ensure the api always returns the same news
            posts
        '''
        news_search = get_news_flair(
            access_token=oauth_token["access_token"],
            posts_to_return=7,
            fullname_after="t3_dm3brn"
        )

        '''
            testing last reddit post in the
            list
        '''
        self.assertEqual(
            news_search["data"]["children"][6]["data"]["created_utc"],
            1570559167.0
        )
        '''
            Testing there is 7 posts returned
        '''
        self.assertEqual(
            len(news_search["data"]["children"]),
            7
        )
        '''
            Unique id of the first post returned
        '''
        self.assertEqual(
            news_search["data"]["children"][0]["data"]["name"],
            "t3_dlyuen"
        )





class RedditApi(unittest.TestCase):
    """Testing the reddit api pull

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
            Using date format that aligns with
            historical ratings
        '''
        self.assertEqual(
            clean_saturday_ratings[0]["ratings_occurred_on"],
            "2019-11-02"

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
            Using date format that aligns with
            historical ratings
        '''
        self.assertEqual(
            clean_saturday_st[0]["ratings_occurred_on"],
            "2019-12-21"
        )

        clean_saturday_th = handle_table_clean(mock_rating_table,
            rating_call_counter=0,
            ratings_title="Toonami Ratings for January 18th, 2020"
        )
        '''
            Using date format that aligns with
            historical ratings
        '''
        self.assertEqual(
            clean_saturday_th[0]["ratings_occurred_on"],
            "2020-01-18"
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

    def test_handle_ratings_insertion(self):
        """Tests outbound arguements for ratings put item in dynamodb

            Parameters
            ----------

            Returns
            -------

            Raises
            ------
        """
        from scripts.reddit_ratings import handle_ratings_insertion
        handle_ratings_insertion(all_ratings_list=MOCK_RATINGS_LIST)


    def test_dict_key_mapping(self):
        """Validating mapping of rating keys to dynamodb columns

            Parameters
            ----------

            Returns
            -------

            Raises
            ------
        """
        from scripts.reddit_ratings import dict_key_mapping
        original_json_list_example = [
            {
                "Time": "12",
                "Total": "1036",
                "Household": "0.70",
                "ATotal": "630",
                "AHousehold": "0.20",
                "Show": "sample show",
                "Date": "2014-09-06"

            }
        ]

        clean_original_values = dict_key_mapping(
            pre_clean_ratings_keys=original_json_list_example
        )

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
            is replaced with None
        '''
        self.assertIsNone(
            clean_ratings_list[0]["PERCENTAGE_OF_HOUSEHOLDS_AGE_18_49"]
        )   
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
            Testing what happens if PERCENTAGE_OF_HOUSEHOLDS_AGE_18_49
            is not present
        '''
        self.assertEqual(
            clean_ratings_list[2]["SHOW"],
            "sample show without adult household (r"
        )
        self.assertIsNone(clean_ratings_list[2]["IS_RERUN"])     


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
        '''
            Assigns a class attribute which is 
            a dict that represents news posts
        '''
        with open("util/lambda_cw_event.json", "r") as news_flair:
            cls.lambda_event_fixture = json.load(news_flair)

    @patch("scripts.reddit_ratings.ratings_iteration")
    @patch("scripts.reddit_ratings.get_logger")
    def test_lambda_handler_event(self, get_logger_mock,
        ratings_iteration_mock):
        """Tests passing sample event to lambda_handler

            Parameters
            ----------
            get_logger_mock : unittest.mock.MagicMock
                Mock object used to patch get_logger

            ratings_iteration_mock : unittest.mock.MagicMock
                 Mock object used to patch ratings_iteration

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

        '''
            Testing call count and args passed
        '''
        self.assertEqual(
            get_logger_mock.call_count,
            1
        )

        ratings_iteration_mock.assert_called_once_with(
            number_posts=10
        )





if __name__ == "__main__":
    unittest.main()
