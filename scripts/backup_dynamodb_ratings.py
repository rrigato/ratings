from boto3.dynamodb import conditions
from datetime import datetime
from datetime import timedelta

import boto3
import logging
import os

'''
    Special user agent that is recommended according to the
    api docs
    <platform>:<app ID>:<version string> (by /u/<reddit username>)
'''
REDDIT_USER_AGENT = "Lambda:toonamiratings:v1.0 (by /u/toonamiratings)"

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


def test_dynamodb_recent_insertion(table_name):
    """Validates that ratings where inserted in the last month

        Parameters
        ----------
        table_name : str
            Name of the table to check ratings for

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
    
    logging.info("Count of ratings added in last 30 days: " + current_year_items["Count"])
    
    assert current_year_items["Count"] > 5, (
        "Less than 5 show ratings recorded in the last 30 days"
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


def delete_dynamodb_backups(table_name,
    recent_window=29, purge_window=365):
    '''deletes the old/recent dynamodb backups

        Parameters
        ----------
        table_name : str
            Name of the table to remove the backups 
            from

        recent_window : int
            Rolling number of days of old backups we 
            want to delete. Defaults to 29 days. 
            Ex: We want to delete all USER on demand backups 
            that occurred in the last 29 days

        purge_window : int
            How old an on demand backup is before we want to purge it.
            Defaults to 365 days. 
            Ex: We want to delete all USER on demand backups 
            that are older than 365 days

        Returns
        -------


        Raises
        ------
    '''
    dynamodb_client = get_boto_clients(
        resource_name="dynamodb", 
        region_name="us-east-1"
    )

    


    '''
        BackupSummaries = list of all user backups
    '''
    table_backup_list = dynamodb_client.list_backups(
        TableName=table_name,
        BackupType="USER"
    )["BackupSummaries"]


    '''
        return None if there is no backups
    '''
    if len(table_backup_list) == 0:
        return(None)

    '''
        Calulating datetime object based on provided purge_window and
        recent_window
    '''
    oldest_allowed_backup = datetime.now() - timedelta(days=purge_window)

    most_recent_backup = datetime.now() - timedelta(days=recent_window)
    '''
        iterate over every user backup
    '''
    for dynamodb_backup in table_backup_list:

        '''
            datetime.now is local time, but making sure
            both objects are not timezone aware
        '''
        local_dynamo_backup_time = dynamodb_backup["BackupCreationDateTime"].replace(
            tzinfo=None
        )
        '''
            Purging backups older than now minus the purge window
            or newer than now minus the most_recent_backup time

            Ex:
            If today is 2025-05-31 and recent_window= 10 and purge_window=365
            Deleteing all backups created between 2024-05-31
            and 2025-05-21

        '''
        if ( 
            (local_dynamo_backup_time > most_recent_backup) or
            (local_dynamo_backup_time < oldest_allowed_backup)
        ):
            logging.info("Deleting backup: ")
            logging.info(dynamodb_backup["BackupArn"])

            dynamodb_client.delete_backup(
                BackupArn=dynamodb_backup["BackupArn"]
            )
        


def create_dynamodb_backup(table_name,
    backup_name):
    '''deletes the old/recent dynamodb backups

        Parameters
        ----------
        table_name : str
            Name of the table to remove the backups 
            from

        backup_name : str
            Name of the backup with appended day string _YYYY_MM_DD 

        Returns
        -------

        Raises
        ------
    '''
    dynamodb_client = get_boto_clients(
        resource_name="dynamodb", 
        region_name="us-east-1"
    )

    '''
        Add _YYYY_MM_DD to backup_name
    '''
    full_backup_name = "{backup_name}_{backup_date}".format(
        backup_name=backup_name,
        backup_date=datetime.now().strftime("%Y_%m_%d")
    )

    logging.info("Creating backup ")
    logging.info(full_backup_name)

    dynamodb_client.create_backup(
        TableName=table_name,
        BackupName=full_backup_name
    )

def lambda_handler(event, context):
    """Handles lambda invocation from cloudwatch events rule

        Parameters
        ----------

        Returns
        -------

        Raises
        ------
    """
    '''
        Logging required for cloudwatch logs
    '''
    logging.getLogger().setLevel(logging.INFO)

    test_dynamodb_recent_insertion(table_name=os.environ["DYNAMODB_TABLE_NAME"])

    delete_dynamodb_backups(table_name=os.environ["DYNAMODB_TABLE_NAME"])

    create_dynamodb_backup(
        table_name=os.environ["DYNAMODB_TABLE_NAME"],
        backup_name="lambda_backup_script"
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
    test_dynamodb_recent_insertion(table_name="prod_toonami_ratings")
    
    delete_dynamodb_backups(table_name="prod_toonami_ratings")
    create_dynamodb_backup(
        table_name="prod_toonami_ratings",
        backup_name="adhoc_manual_backup"
    )

if __name__ == "__main__":    
    main()
