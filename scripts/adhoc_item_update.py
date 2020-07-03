from datetime import datetime
from scripts.reddit_ratings import clean_dict_value
from scripts.reddit_ratings import dict_key_mapping
from scripts.reddit_ratings import get_boto_clients

import boto3
import json
import os


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
        clean_television_ratings : list
            all_television ratings where each item has a YEAR
            attribute

        Raises
        ------

    """
    for ratings_timeslot in all_television_ratings:

        '''
            Gets the year from the ISO 8601 formatted date
        '''
        ratings_timeslot["YEAR"] = datetime.strptime(
            ratings_timeslot["RATINGS_OCCURRED_ON"], "%Y-%m-%d").year
        
        try:
            '''
                If the timeslot is a rerun, remove that 
                key from the dict
            '''
            if ratings_timeslot["IS_RERUN"] is None:
                ratings_timeslot.pop("IS_RERUN")
        except KeyError:
            '''
                If IS_RERUN is not present
            '''
            pass

    return(all_television_ratings)

def batch_put_item(television_ratings, table_name):
    """Batch puts updated ratings items

        Parameters
        ----------
        television_ratings : list
            list of dict where each dict is an item to insert
        
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
        batch writer
    '''
    with dynamo_table.batch_writer() as batch_insert:
        '''
            Iterate over all items for upload
        '''
        for individual_item in television_ratings:
            batch_insert.put_item(
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
    all_television_ratings = batch_item_scan(
        table_name="prod_toonami_ratings"
    )

    clean_television_ratings = get_year_attribute(
        all_television_ratings=all_television_ratings
    )

    batch_put_item(
        television_ratings=clean_television_ratings,
        table_name="prod_toonami_ratings"
    )

if __name__ == "__main__":
    main()
