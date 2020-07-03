from datetime import datetime
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

def batch_item_scan(table_name):
    """retrieves all items in a large scan operation

        Parameters
        ----------
        
        table_name : str
            Name of the dynamodb table to insert into

        Returns
        -------
        all_television_ratings : list
            List of dict where each dict represents a timeslot
            for a show

        Raises
        ------

    """
    dynamo_client, dynamo_table = get_boto_clients(
            resource_name="dynamodb",
            region_name="us-east-1",
            table_name=table_name
    )

    
    all_prod_items = dynamo_table.scan()

    return(all_prod_items["Items"])


def get_year_attribute(all_television_ratings):
    """Places a year attribute on each item
        Removes IS_RERUN if it is None

        Parameters
        ----------
        
        all_television_ratings : list
            List of dict where each dict represents a timeslot
            for a show


        Returns
        -------

        Raises
        ------

    """
    for ratings_timeslot in all_television_ratings:

        ratings_timeslot["YEAR"] = datetime.strptime(
            ratings_timeslot["RATINGS_OCCURRED_ON"], "%Y-%m-%d").year
        try:
            '''
                If the timeslot is a rerun, remove that 
                key from the dict
            '''
            if ratings_timeslot["IS_RERUN"] is None:
                ratings_timeslot["IS_RERUN"].pop()
        except KeyError:
            '''
                If IS_RERUN is not present
            '''
            pass


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
            resource_name="dynamodb",
            region_name="us-east-1",
            table_name=table_name
    )

    '''
        Open and load historical file
    '''
    with open(json_file_location, "r") as json_file:

        historical_ratings = json.load(json_file)

        '''
            batch writer
        '''
        with dynamo_table.batch_writer() as batch_insert:
            '''
                Iterate over all items for upload
            '''
            for individual_item in clean_rating_values:
                batch_insert.update_item(
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
    batch_item_scan(table_name="prod_toonami_ratings")

if __name__ == "__main__":
    main()
