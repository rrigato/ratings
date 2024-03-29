import json
import os
import unittest
from unittest.mock import MagicMock, patch


from util.test_reddit_rating_config import (MOCK_RATINGS_LIST)


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

        os.environ["AWS_LAMBDA_FUNCTION_NAME"] = "dev-ratings-backend-lambda-poll"
        
        '''
            Assigns a class attribute which is 
            a dict that represents news posts
        '''
        with open("util/news_flair_fixture.json", "r") as news_flair:
            cls.news_flair_fixture = json.load(news_flair)
        

        cls.valid_column_names = [
            "PERCENTAGE_OF_HOUSEHOLDS",
            "PERCENTAGE_OF_HOUSEHOLDS_AGE_18_49",
            "RATINGS_OCCURRED_ON",
            "SHOW",
            "TIME", 
            "TOTAL_VIEWERS", 
            "TOTAL_VIEWERS_AGE_18_49"

        ]


    def test_dict_key_mapping(self):
        """Validating mapping of rating keys to dynamodb columns

        """
        from scripts.historical_ratings_upload import dict_key_mapping
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
        from scripts.historical_ratings_upload import dict_key_mapping
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
        from scripts.historical_ratings_upload import dict_key_mapping


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
        from scripts.historical_ratings_upload import clean_dict_value

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


    @patch("scripts.reddit_ratings.persist_show_names")
    @patch("scripts.reddit_ratings.persist_ratings")
    @patch("scripts.reddit_ratings.ratings_from_internet")
    def test_main(
        self, 
        ratings_from_internet_mock: MagicMock, 
        persist_ratings_mock: MagicMock,
        persist_show_names_mock: MagicMock
        ):
        """orchestration for main function"""
        from fixtures.ratings_fixtures import get_mock_television_ratings
        from scripts.reddit_ratings import main

        ratings_from_internet_mock.return_value = (
           get_mock_television_ratings(5), None
        )

        persist_ratings_mock.return_value = None
        persist_show_names_mock.return_value = None


        main()


        ratings_from_internet_mock.assert_called()
        persist_ratings_mock.assert_called()
        persist_show_names_mock.assert_called()



class RatingsLambdaHandler(unittest.TestCase):
    """Tests specific to when the script is run from a lambda function
    """
    

    @patch("logging.getLogger")
    @patch("scripts.reddit_ratings.main")
    def test_lambda_handler_event(
        self, 
        main_mock: MagicMock, 
        getLogger_mock: MagicMock
        ):
        """Tests passing sample event to lambda_handler
        """
        from scripts.reddit_ratings import lambda_handler

        lambda_handler(
            event={"unused": "event"},
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

