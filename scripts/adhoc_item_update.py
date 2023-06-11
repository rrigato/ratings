from datetime import datetime

from scripts.historical_ratings_upload import get_boto_clients


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


def get_year_attribute(all_television_ratings, attribute_to_check):
    """Places a year attribute on each item
        Removes attribute_to_check if it is None

        Parameters
        ----------
        
        all_television_ratings : list
            List of dict where each dict represents a timeslot
            for a show

        attribute_to_check : str
            Name of attribute to remove if it is None in the Dynamodb Item

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
                If the attribute_to_check is None, remove that 
                key from the dict
            '''
            if ratings_timeslot[attribute_to_check] is None:
                ratings_timeslot.pop(attribute_to_check)
        except KeyError:
            '''
                If attribute_to_check is not present in Item
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
        all_television_ratings=all_television_ratings,
        attribute_to_check="PERCENTAGE_OF_HOUSEHOLDS"
    )

    batch_put_item(
        television_ratings=clean_television_ratings,
        table_name="prod_toonami_ratings"
    )

if __name__ == "__main__":
    main()
