from scripts.reddit_ratings import clean_dict_value
from scripts.reddit_ratings import dict_key_mapping
from scripts.reddit_ratings import get_boto_clients

import boto3
import json
import logging
import os

def get_logger(working_directory=os.getcwd()):
    """Sets up logger

        Parameters
        ----------
        working_directory: str
            Where to put logger, defaults to cwd

        Returns
        -------

        Raises
        ------
    """
    '''
        Adds the file name to the logs/ directory without
        the extension
    '''
    logging.basicConfig(
        filename=os.path.join(working_directory, "logs/",
        os.path.basename(__file__).split(".")[0]),
        format="%(asctime)s %(message)s",
         datefmt="%m/%d/%Y %I:%M:%S %p", level=logging.DEBUG
         )
    logging.info("\n")


def batch_json_upload(json_file_location, table_name):
    """Batch inserts json file into dynamodb table

        Parameters
        ----------
        json_file_location : str
            Where the json file is located on local disk
        
        table_name : str
            Name of the dynamodb table to insert into

        Returns
        -------

        Raises
        ------

    """
    dynamo_client, dynamo_table = get_boto_clients(
            service_name="dynamodb",
            region_name="us-east-1",
            table_name=table_name
    )

    '''
        Open and load historical file
    '''
    with open(json_file_location, "r") as json_file:

        historical_ratings = json.load(json_file)

        clean_rating_keys = dict_key_mapping(
            pre_clean_ratings_keys=historical_ratings
        )

        clean_rating_values = clean_dict_value(
            ratings_values_to_clean=clean_rating_keys
        )
        '''
            Iterate over all items for upload
        '''
        for individual_item in clean_rating_values:
            dynamo_table.put_item(
                TableName=table_name,
                Item=individual_item
            )


def main():
    """Entry point into the script
        Parameters
        ----------

        Returns
        -------

        Raises
        ------
    """
    get_logger()
    batch_json_upload(
        json_file_location="historical/ratings_05262012_to_05272017.json",
        table_name="dev_toonami_ratings"
    )

    batch_json_upload(
        json_file_location="historical/ratings_11102018_04112020.json",
        table_name="dev_toonami_ratings"
    )

if __name__ == "__main__":
    main()
