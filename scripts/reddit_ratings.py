import json
import logging
import os

import boto3

from ratings.repo.ratings_repo_backend import (persist_ratings,
                                               persist_show_names,
                                               ratings_from_internet)


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



def get_client_secrets(region_name="us-east-1"):
    """Returns reddit client key and reddit client secret 

        Parameters
        ----------
        region_name : str
                aws region you are using, defaults to
                us-east-1        

        Returns
        -------
        reddit_client_key : str
            Reddit client key

        reddit_client_secret : str
            Reddit client secret        

        Raises
        ------
    """
    secrets_manager_client = get_boto_clients(
        resource_name="secretsmanager",
        region_name=region_name
    )


    '''
        Passing the Name of the string to the boto client
    '''
    all_client_secrets = secrets_manager_client.get_secret_value(
        SecretId="/prod/v1/credentials"
    )

    '''
        Secrets are stored in a json string
    '''
    client_secrets_dict = json.loads(all_client_secrets["SecretString"])

    '''
        return reddit api key and secret
    '''
    return(
        client_secrets_dict["reddit_api_key"],
        client_secrets_dict["reddit_api_secret"]
    )


def main() -> None:
    """Orchestrates clean architecture invocations from
    external

    Raises
    ------
    RuntimeError
        if unexpected error from clean architecture
    """
    logging.info(f"--------------main - invocation begin--------------")

    tv_ratings, retreival_error = ratings_from_internet()

    if retreival_error is not None:
        raise RuntimeError(retreival_error)
    
    logging.info(
        f"main - len(tv_ratings) - {len(tv_ratings)}"
    )

    persistence_error = persist_ratings(tv_ratings)

    if persistence_error is not None:
        raise RuntimeError(persistence_error)
    
    logging.info(f"main - persist_ratings successful")

    analytics_error = persist_show_names(tv_ratings)

    if analytics_error is not None:
        raise RuntimeError(analytics_error)
    
    logging.info(f"--------------main - invocation end--------------")

    return(None)



def lambda_handler(event, context):
    """Handles lambda invocation from cloudwatch events rule
    """
    '''
        Logging required for cloudwatch logs
    '''
    logging.getLogger().setLevel(logging.INFO)
    main()




if __name__ == "__main__":
    import logging
    import os
    from time import strftime
    os.environ["AWS_REGION"] = "us-east-1"
    logging.basicConfig(
        format=("%(levelname)s | %(asctime)s.%(msecs)03d" +
            strftime("%z") + " | %(message)s"
        ),
        datefmt="%Y-%m-%dT%H:%M:%S", 
        level=logging.INFO
    )
    lambda_handler({}, None)

