from datetime import datetime
from datetime import timedelta

import boto3
import json
import os
import requests
import subprocess
import unittest

ENVIRON_DEF = "dev-backend"

def get_boto_clients(resource_name, region_name="us-east-1",
    table_name=None):
    '''Returns the boto client for various aws resources

        Parameters
        ----------
        resource_name : str
            Name of the resource for the client

        region_name : str
                aws region you are using, defaults to
                us-east-1

        Returns
        -------
        service_client : boto3.client
            boto3 client for the aws resource in resource_name
            in region region_name

        dynamodb_table_resource : boto3.resource.Table
            boto3 Table resource, only returned if table_name is
            not None
        


        Raises
        ------
    '''

    service_client = boto3.client(
            service_name=resource_name, 
            region_name=region_name
        )

    '''
        return boto3 DynamoDb table resource in addition to boto3 client
        if table_name parameter is not None
    '''
    if table_name is not None:
        dynamodb_table_resource = boto3.resource(
            service_name=resource_name,
            region_name=region_name
        ).Table(table_name)

        return(service_client, dynamodb_table_resource)

    '''
        Otherwise return just a resource client
    '''
    return(service_client)


class BackendTests(unittest.TestCase):
    """Tests backend AWS resources from templates/ratings_backend.yml

        Parameters
        ----------

        Returns
        -------

        Raises
        ------
    """
    @classmethod
    def setUpClass(cls):
        '''Unitest function that is run once for the class

            Parameters
            ----------

            Returns
            -------

            Raises
            ------
        '''
        cls.DYNAMO_TABLE_NAME = "dev_toonami_ratings"
        cls.LAMBDA_FUNCTION_NAME = "dev-ratings-backend-lambda-poll"
        cls.S3_CODE_BUCKET = "dev-ratings-backend-source-code"
        cls.S3_CODE_ZIP_FILE = "built_lambda.zip"

    def test_dynamodb_config(self):
        '''Tests that the dynamodb table is present

            Parameters
            ----------

            Returns
            -------

            Raises
            ------
        '''

        """
            Creates dynamodb resource and
            puts an item in the table
        """
        dynamo_client = get_boto_clients(
            resource_name="dynamodb",
            region_name="us-east-1"
        )

        table_configuration = dynamo_client.describe_table(
            TableName=self.DYNAMO_TABLE_NAME
        )

        self.assertEqual(
            table_configuration["Table"]["TableName"],
            self.DYNAMO_TABLE_NAME
        )


        '''
            Checking that primary key configuration is valid
            Only two primary keys:
            HASH Key - RATINGS_OCCURRED_ON
            RANGE Key - TIME
        '''
        self.assertEqual(
            len(table_configuration["Table"]["KeySchema"]),
            2
        )
        for primary_key in table_configuration["Table"]["KeySchema"]:
            if (primary_key["AttributeName"] == "RATINGS_OCCURRED_ON"):
                self.assertEqual(
                    primary_key["KeyType"],
                    "HASH"
                )
            else:
                self.assertEqual(
                    primary_key["AttributeName"],
                    "TIME"
                )
                self.assertEqual(
                    primary_key["KeyType"],
                    "RANGE"
                )
        '''
            Testing on demand billing type
            and that encryption is enabled on the dynamodb
            table
        '''
        self.assertEqual(
            table_configuration["Table"]["BillingModeSummary"]["BillingMode"],
            "PAY_PER_REQUEST"
        )

        self.assertEqual(
            table_configuration["Table"]["SSEDescription"]["Status"],
            "ENABLED"
        )


    def test_lambda_config(self):
        '''Tests that the lambda function configuration

            Parameters
            ----------

            Returns
            -------

            Raises
            ------
        '''

        """
            Creates dynamodb resource and
            puts an item in the table
        """
        lambda_client = get_boto_clients(
            resource_name="lambda",
            region_name="us-east-1"
        )


        lambda_configuration = lambda_client.get_function(
            FunctionName=self.LAMBDA_FUNCTION_NAME
        )


        '''
            Testing state, runtime, and handler config
        '''
        self.assertEqual(
            lambda_configuration["Configuration"]["Runtime"],
            "python3.7"
        )

        self.assertEqual(
            lambda_configuration["Configuration"]["State"],
            "Active"
        )

        self.assertEqual(
            lambda_configuration["Configuration"]["Handler"],
            "reddit_ratings.lambda_handler"
        )
        
        
    def test_dynamodb_count(self):
        '''Tests that the number of items present in dynamodb table

            Parameters
            ----------

            Returns
            -------

            Raises
            ------
        '''
        dynamo_client, dynamo_table = get_boto_clients(
                resource_name="dynamodb",
                region_name="us-east-1",
                table_name=self.DYNAMO_TABLE_NAME
        )

        '''
            Testing item count
        '''
        item_count = dynamo_table.scan(
            TableName=self.DYNAMO_TABLE_NAME,
            Select="COUNT"
        )

        self.assertGreater(
            item_count["Count"],
            10
        )



    def test_dynamodb_recent_insertion(self):
        """Validates the ratings where inserted in the last month

            Parameters
            ----------

            Returns
            -------

            Raises
            ------
        """
        dynamo_client, dynamo_table = get_boto_clients(
                resource_name="dynamodb",
                region_name="us-east-1",
                table_name=self.DYNAMO_TABLE_NAME
        )

        from boto3.dynamodb.conditions import Key

        '''
            Query the current year ratings
        '''
        current_year = datetime.now().year

        '''
            If we are in the first 14 days of the year,
            check last year
        '''
        if datetime.now().timetuple().tm_yday <= 14:
            current_year = datetime.now().year - 1

        '''
            Formatting in "YYYY-MM-DD"
        '''
        start_day = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")

        '''
            Getting the items for the current year that 
            were in the last 30 days
        '''
        current_year_items = dynamo_table.query(
            IndexName="YEAR_ACCESS",
            KeyConditionExpression=
            Key("YEAR").eq(current_year) & 
            Key("RATINGS_OCCURRED_ON").gte(start_day)

        )
      
        self.assertGreater(
            current_year_items["Count"],
            5
        )


        '''
            Validate that SHOW element is not none
            and that TOTAL_VIEWERS is a number if you exclude , or .
        '''
        for show_rating in current_year_items["Items"]:
            self.assertIsNotNone(show_rating["SHOW"])
            self.assertTrue(
                show_rating["TOTAL_VIEWERS"].replace(",", "").replace(".","").isnumeric()
            )
            
            
    def test_dynamodb_backup_time(self):
        '''Validates a backup was created

            Parameters
            ----------

            Returns
            -------

            Raises
            ------
        '''
        dynamo_client = get_boto_clients(
                resource_name="dynamodb",
                region_name="us-east-1"
        )


        dynamo_backups = dynamo_client.list_backups(
            TableName=self.DYNAMO_TABLE_NAME
        )

        '''
            Assert we have a dyamodb backup
        '''
        self.assertGreater(len(dynamo_backups["BackupSummaries"]), 0) 

        '''
            Initialize a random backup time for comparison
        '''
        most_recent_backup = dynamo_backups["BackupSummaries"][0]["BackupCreationDateTime"]

        '''
            Iterating over every backup to get the most recent backup 
            time
        '''
        for dynamo_backup in dynamo_backups["BackupSummaries"]:
            
            if dynamo_backup["BackupCreationDateTime"] > most_recent_backup:
                most_recent_backup = dynamo_backup["BackupCreationDateTime"]
        
        '''
            Validating that the most recent backup has occurred in the 
            last 10 minutes
        '''
        self.assertGreater(
            most_recent_backup.replace(tzinfo=None),
            datetime.now() - timedelta(minutes=10)
        )


    def test_dynamodb_gsi(self):
        '''Validate dynamodb global secondary index (gsi)

            Parameters
            ----------

            Returns
            -------

            Raises
            ------
        '''

        """
            Creates dynamodb resource and
            puts an item in the table
        """
        dynamo_client = get_boto_clients(
            resource_name="dynamodb",
            region_name="us-east-1"
        )

        table_configuration = dynamo_client.describe_table(
            TableName=self.DYNAMO_TABLE_NAME
        )

        '''
            key is index name, value is attributes of key
        '''
        expected_index_structure = {
            
            "SHOW_ACCESS": {
                "Projection": {
                    "ProjectionType":"ALL"
                },
                "KeySchema": [
                    {"AttributeName": "SHOW", "KeyType": "HASH"}, 
                    {"AttributeName": "RATINGS_OCCURRED_ON", "KeyType": "RANGE"}
                ]

            },
            "YEAR_ACCESS": {
                "Projection": {
                    "ProjectionType":"ALL"
                },
                "KeySchema": [
                    {"AttributeName": "YEAR", "KeyType": "HASH"}, 
                    {"AttributeName": "RATINGS_OCCURRED_ON", "KeyType": "RANGE"}
                ]
            }
            
        }

        dynamo_table_gsis = table_configuration["Table"]["GlobalSecondaryIndexes"]

        self.assertEqual(
            len(dynamo_table_gsis),
            2
        )


        '''
            Iterate over all GSI's
        '''
        for global_secondary_index in dynamo_table_gsis:
            '''
                Validate name of the GSI
            '''
            self.assertIn(
                global_secondary_index["IndexName"],
                list(expected_index_structure.keys())
            )

            '''
                Validate Partition/Sort Key Attributes
            '''
            self.assertEqual(
                global_secondary_index["KeySchema"],
                expected_index_structure[global_secondary_index["IndexName"]]["KeySchema"]
            )




