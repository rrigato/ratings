import json
import unittest
from copy import deepcopy
from unittest.mock import MagicMock, patch

from fixtures.ratings_fixtures import mock_secret_config


class TestRatingsRepoBackend(unittest.TestCase):

    @patch("ratings.repo.ratings_repo_backend.load_secret_config")
    def test_ratings_from_internet(
        self,
        load_secret_config: MagicMock
        ):
        """Parsing of TelevisionRatings entities"""
        from ratings.entities.ratings_entities import TelevisionRating
        from ratings.repo.ratings_repo_backend import ratings_from_internet

        load_secret_config.return_value = mock_secret_config()        


        television_ratings, unexpected_error = ratings_from_internet()


        for television_rating in television_ratings:
            self.assertIsInstance(
                television_rating, TelevisionRating
            )
        self.assertIsNone(unexpected_error)
        '''TODO - remove coupled test'''
        load_secret_config.assert_called()


    @patch("boto3.client")
    def test_load_secret_config(self, 
        boto_client_mock: MagicMock):
        """Environment config successfully loaded"""
        from ratings.entities.ratings_entities import SecretConfig
        from ratings.repo.ratings_repo_backend import load_secret_config

        mock_reddit_username = "mock2"
        # pragma: allowlist nextline secret
        mock_reddit_password = "mock3"
        boto_client_mock.return_value.get_secret_value.return_value = (
        deepcopy(
            {
                "Name": "prod/v1/credentials",
                "SecretString": json.dumps(
                    {                
                        # pragma: allowlist nextline secret
                        "reddit_api_secret": "mock0",
                        # pragma: allowlist nextline secret
                        "reddit_api_key": "mock1",
                        "reddit_api_username": mock_reddit_username,
                        "reddit_api_password": mock_reddit_password
                    }
                )

            }
        )
        )


        secret_config = load_secret_config()

        get_secret_args, get_secret_kwargs = (
            boto_client_mock.return_value.get_secret_value.call_args
        )

        self.assertIsInstance(secret_config, SecretConfig)

        self.assertIn("SecretId", get_secret_kwargs.keys())

        
        
        populated_secret_properties = [
            attr_name for attr_name in dir(secret_config)
            if not attr_name.startswith("_")
            and getattr(secret_config, attr_name) is not None
        ]

        for populated_secret in populated_secret_properties:
            self.assertIsNotNone(
                getattr(secret_config, populated_secret),
                msg=f"\n\n secrets_config property {populated_secret}"
            )
        self.assertEqual(
            len(populated_secret_properties),
            4,
            msg="incorrect number of SecretConfig attributes populated"
        )
        
        self.assertEqual(
            secret_config.reddit_username,
            mock_reddit_username,
            msg="\n\ne2e bug where username not populated correctly"
        )
        self.assertEqual(
            secret_config.reddit_password,
            mock_reddit_password,
            msg="\n\ne2e bug where password not populated correctly"
        )