import unittest
from unittest.mock import MagicMock, patch


class BackupDynamoDbUnit(unittest.TestCase):
    """Unit tests for BackupDynamoDB
    """

    @patch("boto3.client")
    def test_get_boto_clients_no_region(self, boto3_client_mock: MagicMock):
        '''Tests outgoing boto3 client generation when no region is passed
        '''
        from scripts.historical_ratings_upload import get_boto_clients

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
        """Tests getting a dynamodb table resource from get_boto_clients"""
        from scripts.historical_ratings_upload import get_boto_clients

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
    def test_get_boto_clients_with_region(self, boto3_client_mock: MagicMock):
        '''Tests outgoing boto3 client generation when a region is passed
        '''
        from scripts.historical_ratings_upload import get_boto_clients

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

