from bs4 import BeautifulSoup
from datetime import datetime
from unittest.mock import MagicMock
from unittest.mock import patch

import json
import logging
import os
import requests
import unittest


from util.test_reddit_rating_config import MOCK_CLEAN_RATINGS_LIST
from util.test_reddit_rating_config import MOCK_RATINGS_LIST
from util.test_reddit_rating_config import REDDIT_RATING_TABLE_2019
from util.test_reddit_rating_config import REDDIT_RATING_TABLE_2020






class BackupDynamoDbUnit(unittest.TestCase):
    """Unit tests for BackupDynamoDB

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
            How many news posts the client main function is using
        '''
        cls.DYNAMODB_TABLE_NAME = "dev_toonami_ratings"
        os.environ["DYNAMODB_TABLE_NAME"] = cls.DYNAMODB_TABLE_NAME
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


    @patch("scripts.reddit_ratings.handle_ratings_insertion")
    @patch("scripts.reddit_ratings.ratings_iteration")
    def test_main(self, ratings_iteration_mock,
        handle_ratings_iteration_mock):
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
        from scripts.backup_dynamodb_ratings import main

        pass

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
        from scripts.backup_dynamodb_ratings import get_boto_clients

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


    def test_get_boto_clients_table_resource(self):
        """Tests getting a dynamodb table resource from get_boto_clients

            Parameters
            ----------

            Returns
            -------


            Raises
            ------
        """
        from scripts.backup_dynamodb_ratings import get_boto_clients

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
        from scripts.backup_dynamodb_ratings import get_boto_clients

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



    @patch("scripts.backup_dynamodb_ratings.get_boto_clients")
    def test_delete_dynamodb_backups(self, get_boto_clients_mock):
        '''Tests that we delete the old/recent dynamodb backups

            Parameters
            ----------
            get_boto_clients_mock : unittest.mock.MagicMock
                Mock object used to patch
                AWS Python SDK dynamodb clients

            Returns
            -------


            Raises
            ------
        '''
        from scripts.backup_dynamodb_ratings import delete_dynamodb_backups

        mock_dynamodb_client = MagicMock()

        mock_dynamodb_client.list_backups.return_value = {
            "BackupSummaries":[
                
            ]
        }

        get_boto_clients_mock.return_value = mock_dynamodb_client

        delete_dynamodb_backups(table_name=self.DYNAMODB_TABLE_NAME)


        '''
            validate call args for list_backups
        '''
        mock_dynamodb_client.list_backups.assert_called_once_with(
            TableName=self.DYNAMODB_TABLE_NAME,
            BackupType="USER"
        )


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

    @patch("logging.getLogger")
    @patch("scripts.backup_dynamodb_ratings.main")
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
        from scripts.backup_dynamodb_ratings import lambda_handler

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


