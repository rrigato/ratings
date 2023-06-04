import json
import logging
import os
from typing import Dict, List, Union

from ratings.repo.ratings_repo_backend import standardize_key_name
from scripts.backup_dynamodb_ratings import get_boto_clients


def dict_key_mapping(
        pre_clean_ratings_keys: List[Dict]
        ) -> List[Dict[str, Union[str, int]]]:
    """Maps inconsistent source data to column names for dynamodb

        Parameters
        ----------
        pre_clean_ratings_keys
            refer to keys of get_table_column_name_mapping return
            value for potential key names since this is user input data
            that can be highly inconsistent

        Returns
        -------
        clean_ratings_columns
            list of dict with standardized column names
            matching one of the following:
            [
                "PERCENTAGE_OF_HOUSEHOLDS",
                "PERCENTAGE_OF_HOUSEHOLDS_AGE_18_49",
                "RATINGS_OCCURRED_ON",
                "SHOW",
                "TIME", 
                "TOTAL_VIEWERS", 
                "TOTAL_VIEWERS_AGE_18_49",
                "YEAR",
                "IS_RERUN"

            ]


        Raises
        ------
        KeyError :
            KeyError is raised if the keys for a dict
            in pre_clean_ratings_keys cannot be mapped 
            back to a dynamodb column listed in get_table_column_name_mapping
    """

    clean_ratings_columns = []
    for dict_to_clean in pre_clean_ratings_keys:
        standardize_key_name(dict_to_clean)
        '''
            Append each cleaned dict
        '''
        clean_ratings_columns.append(dict_to_clean)

    logging.info("dict_key_mapping - Mapped ratings post column names")
    logging.info(clean_ratings_columns)
    
    return(clean_ratings_columns)



def clean_adult_household(dict_to_clean):
    """Cleans the PERCENTAGE_OF_HOUSEHOLDS_AGE_18_49 field

        Parameters
        ----------
        dict_to_clean : dict
            Individual rating that is pass by reference

        Returns
        -------

        Raises
        ------
    """
    '''
        Try catch handles if PERCENTAGE_OF_HOUSEHOLDS_AGE_18_49
        is not included in the list of keys
    '''
    try:
        if dict_to_clean["PERCENTAGE_OF_HOUSEHOLDS_AGE_18_49"] == "9.99":
            dict_to_clean.pop("PERCENTAGE_OF_HOUSEHOLDS_AGE_18_49")
    except KeyError:
        '''
            do nothing if PERCENTAGE_OF_HOUSEHOLDS_AGE_18_49
            is not present
        '''
        pass



def clean_dict_value(ratings_values_to_clean):
    """Calls cleaning helper functions to clean elements of
        each rating show

        Parameters
        ----------
        ratings_values_to_clean : list
            list of dict where each dict has already been
            passed through dict_key_mapping

        Returns
        -------
        clean_ratings_values : list
            list of dict with the following keys:
            RATINGS_OCCURRED_ON - YYYY-MM-DD date
            TIME - str of timeslot Example 12:00a
            SHOW - str of show  
            TOTAL_VIEWERS - int of viewers in thousands 
            PERCENTAGE_OF_HOUSEHOLDS_AGE_18_49 - float  
            YEAR - int of year Example - 2022
            

        Raises
        ------
    """
    clean_ratings_values = []
    for dict_to_clean in ratings_values_to_clean:
        '''
            If we are able to find " (r)" in the 
            SHOW string that indicates a rerun
            removing everthing before the space and
            marking IS_RERUN as True
        '''
        if dict_to_clean["SHOW"].find(" (r)") > 0:
            dict_to_clean["SHOW"] = dict_to_clean["SHOW"].split(" (r)")[0]
            dict_to_clean["IS_RERUN"] = True
        
        clean_adult_household(dict_to_clean=dict_to_clean)
        

        clean_ratings_values.append(dict_to_clean)

    return(clean_ratings_values)


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
            resource_name="dynamodb",
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
            batch writer
        '''
        with dynamo_table.batch_writer() as batch_insert:
            '''
                Iterate over all items for upload
            '''
            for individual_item in clean_rating_values:
                batch_insert.put_item(
                    Item=individual_item
                )


def deprecated_main():
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
    deprecated_main()
