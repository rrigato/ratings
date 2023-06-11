import json
import os
import unittest
from datetime import datetime, timedelta
from unittest.mock import MagicMock, patch


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
        with open("util/lambda_cw_event.json", "r") as cw_event:
            cls.lambda_event_fixture = json.load(cw_event)

        cls.dynamodb_backups_fixture = {
            "BackupSummaries": [
                {
                    "TableName": "dev_toonami_ratings",
                    "TableId": "f1234567-12460",
                    "TableArn": "arn:aws:dynamodb:us-east-1:1234:table/dev_toonami_ratings",
                    "BackupArn": ("arn:aws:dynamodb:us-east-1:1234:table/" +
                            "dev_toonami_ratings/backup/012340"),
                    "BackupName": "manual_backup_test",
                    "BackupCreationDateTime": datetime.now(),
                    "BackupStatus": "AVAILABLE",
                    "BackupType": "USER",
                    "BackupSizeBytes": 575731
                },
                {
                    "TableName": "dev_toonami_ratings",
                    "TableId": "f1234567-12461",
                    "TableArn": "arn:aws:dynamodb:us-east-1:1234:table/dev_toonami_ratings",
                    "BackupArn": ("arn:aws:dynamodb:us-east-1:1234:table/" +
                            "dev_toonami_ratings/backup/012341"),
                    "BackupName": "manual_backup_test",
                    "BackupCreationDateTime": datetime.now() - timedelta(days=3),
                    "BackupStatus": "AVAILABLE",
                    "BackupType": "USER",
                    "BackupSizeBytes": 575731
                },  
                {
                    "TableName": "dev_toonami_ratings",
                    "TableId": "f1234567-12462",
                    "TableArn": "arn:aws:dynamodb:us-east-1:1234:table/dev_toonami_ratings",
                    "BackupArn": ("arn:aws:dynamodb:us-east-1:1234:table/" +
                            "dev_toonami_ratings/backup/012342"),
                    "BackupName": "manual_backup_test",
                    "BackupCreationDateTime": datetime.now() - timedelta(days=10),
                    "BackupStatus": "AVAILABLE",
                    "BackupType": "USER",
                    "BackupSizeBytes": 575731
                },                                
                {
                    "TableName": "dev_toonami_ratings",
                    "TableId": "f1234567-12463",
                    "TableArn": "arn:aws:dynamodb:us-east-1:1234:table/dev_toonami_ratings",
                    "BackupArn": ("arn:aws:dynamodb:us-east-1:1234:table/" +
                            "dev_toonami_ratings/backup/012343"),
                    "BackupName": "manual_backup_test",
                    "BackupCreationDateTime": datetime.now() - timedelta(days=100),
                    "BackupStatus": "AVAILABLE",
                    "BackupType": "USER",
                    "BackupSizeBytes": 575731
                },                
                {
                    "TableName": "dev_toonami_ratings",
                    "TableId": "f1234567-12464",
                    "TableArn": "arn:aws:dynamodb:us-east-1:1234:table/dev_toonami_ratings",
                    "BackupArn": ("arn:aws:dynamodb:us-east-1:1234:table/" +
                            "dev_toonami_ratings/backup/012344"),
                    "BackupName": "manual_backup_test",
                    "BackupCreationDateTime": datetime.now()- timedelta(days=367),
                    "BackupStatus": "AVAILABLE",
                    "BackupType": "USER",
                    "BackupSizeBytes": 575731
                }                
            ]
        }


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




