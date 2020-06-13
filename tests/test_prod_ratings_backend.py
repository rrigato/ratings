from datetime import datetime
from datetime import timedelta

import boto3
import logging
import os
import requests
import unittest

ENVIRON_DEF = "prod-backend"


def get_boto_clients(resource_name, region_name='us-east-1',
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
        cls.DYNAMO_TABLE_NAME = "prod_toonami_ratings"
        cls.LAMBDA_FUNCTION_NAME = "prod-ratings-backend-lambda-poll"
        cls.S3_CODE_BUCKET = "prod-ratings-backend-source-code"
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

    @unittest.skip("Skipping for now")
    def test_s3_code_object(self):
        '''s3 zip file used to update lambda function code

            Parameters
            ----------

            Returns
            -------

            Raises
            ------
        '''

        """
            gets s3 bucket information
        """
        s3_client = get_boto_clients(
            resource_name="s3",
            region_name="us-east-1"
        )


        '''
            Testing code used to update lambda function
        '''
        s3_code_configuration = s3_client.head_object(
            Bucket=self.S3_CODE_BUCKET,
            Key=self.S3_CODE_ZIP_FILE
        )
        '''
            Testing code content type
        '''
        self.assertEqual(
            s3_code_configuration["ContentType"],
            "application/zip"
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
            50
        )


    def test_dynamodb_recent_insertion(self):
        '''Validates the ratings where inserted in the last month

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

        from boto3.dynamodb.conditions import Key
        current_year_items = dynamo_table.query(
            KeyConditionExpression=Key("RATINGS_OCCURRED_ON").between(
                start=datetime.now() - timedelta(days=30),
                end=datetime.now()
            )
        )
        import pdb; pdb.set_trace()
        datetime.now().year