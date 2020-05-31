from scripts.reddit_ratings import clean_dict_value
from scripts.reddit_ratings import dict_key_mapping
import boto3
import json


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
    dynamo_resource = boto3.resource(
            "dynamodb",
            region_name="us-east-1"
    )

    dynamo_table = dynamo_resource.Table(table_name)
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
    # get_logger()
    # batch_json_upload(
    #     json_file_location="ratings_earliest_november_11_2018.json",
    #     table_name="dev_toonami_ratings"
    # )


if __name__ == "__main__":
    main()
