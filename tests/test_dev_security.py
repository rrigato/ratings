from datetime import datetime
from datetime import timedelta

import argparse
import boto3
import json
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


class SecurityAnalysisTests(unittest.TestCase):
    """Backend code security analysis 

        Parameters
        ----------

        Returns
        -------

        Raises
        ------
    """
    fake_client_key = "fake key"
    def test_detect_secrets(self):
        '''Validates no secrets are present in the repo

            Parameters
            ----------

            Returns
            -------

            Raises
            ------
        '''
        '''
            scan all tracked files in the current working directory
        '''
        detect_secrets_output = subprocess.run(
            ["detect-secrets", "scan", "--all-files", "."],
            capture_output=True
        )

        '''
            Load json string from detect-secrets stdout 
        '''
        secret_scan_result = json.loads(
            detect_secrets_output.stdout
        )

        '''
            Validate there are no secrets in the current directory
        '''
        self.assertEqual(
            secret_scan_result["results"],
            {}
        )