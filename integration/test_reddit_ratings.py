from unittest.mock import MagicMock
from unittest.mock import patch

import json
import os
import unittest




class IntegrationRedditApi(unittest.TestCase):
    """Integration test for the reddit api pull
    """    
    @classmethod
    def setUpClass(cls):
        """Unitest function that is run once for the class

        """
        '''
            How many news posts the client main function is using
        '''
        cls.MAIN_FUNCTION_POST_COUNT = 25
        os.environ["DYNAMODB_TABLE_NAME"] = "dev_toonami_ratings"

        os.environ["AWS_LAMBDA_FUNCTION_NAME"] = "dev-ratings-backend-lambda-poll"
        
        '''
            Assigns a class attribute which is 
            a dict that represents news posts
        '''
        with open("util/news_flair_fixture.json", "r") as news_flair:
            cls.news_flair_fixture = json.load(news_flair)
        
        cls.oauth_token_fixture = {
            "access_token": "FIXTURETOKEN123",
            "token_type": "bearer",
            "expires_in": 3600,
            "scope": "*"
        }

        cls.valid_column_names = [
            "PERCENTAGE_OF_HOUSEHOLDS",
            "PERCENTAGE_OF_HOUSEHOLDS_AGE_18_49",
            "RATINGS_OCCURRED_ON",
            "SHOW",
            "TIME", 
            "TOTAL_VIEWERS", 
            "TOTAL_VIEWERS_AGE_18_49"

        ]


    def test_get_client_secrets(self):
        """Integration test for the get_client_secrets function

            Parameters
            ----------

            Returns
            -------

            Raises
            ------
        """
        from scripts.reddit_ratings import get_client_secrets

        reddit_client_key, reddit_client_secret = get_client_secrets()

        self.assertEqual(type(reddit_client_key), str)

        self.assertEqual(type(reddit_client_secret), str)



    @patch("scripts.reddit_ratings.get_ratings_post")
    @patch("scripts.reddit_ratings.get_oauth_token")
    @patch("scripts.reddit_ratings.get_news_flair")
    def test_ratings_iteration_historical(self, news_flair_patch,
         oauth_token_mock, get_ratings_post_mock):
        """Test for historical rating iterations

            Parameters
            ----------
            news_flair_patch : unittest.mock.MagicMock
                Mock object used to test how often
                get_news_flair is called

            oauth_token_mock : unittest.mock.MagicMock
                Mock object used to patch
                get_oauth_token

            get_ratings_post_mock : unittest.mock.MagicMock
                Mock object used to patch
                get_ratings_post

            Returns
            -------

            Raises
            ------
        """
        from scripts.reddit_ratings import ratings_iteration

        '''
            Used to make sure the posts are iterated the 
            correct number of times
        '''
        news_flair_patch.return_value = self.news_flair_fixture


        get_ratings_post_mock.return_value = [0,3]

        all_ratings_posts = ratings_iteration(number_posts=100)

        '''
            Should be called 4 times each if 
            100 posts are being iterated
        '''
        self.assertEqual(
            news_flair_patch.call_count,
            4
        )

        self.assertEqual(
            get_ratings_post_mock.call_count,
            4
        )        


    @patch("scripts.reddit_ratings.get_oauth_token")
    @patch("scripts.reddit_ratings.get_news_flair")
    def test_ratings_iteration(self, news_flair_patch, oauth_token_mock):
        """Tests that we can iterate over most recent posts

            Parameters
            ----------
            news_flair_patch : unittest.mock.MagicMock
                Mock object used to test how often
                get_news_flair is called

            oauth_token_mock : unittest.mock.MagicMock
                Mock object used to patch
                get_oauth_token

            Returns
            -------

            Raises
            ------
        """
        from scripts.reddit_ratings import ratings_iteration

        '''
            setting return values for mock
        '''
        oauth_token_mock.return_value = self.oauth_token_fixture

        news_flair_patch.return_value = self.news_flair_fixture
        
        all_ratings_posts = ratings_iteration()
        '''
            Testing that the get_news_flair
            meaning we are only looking for the most recent ratings
        '''
        self.assertEqual(news_flair_patch.call_count,
            1
        )

        self.assertEqual(oauth_token_mock.call_count,
            1
        )

        news_flair_patch.assert_called_once_with(
            access_token="FIXTURETOKEN123",
            posts_to_return=10
        )

        self.assertEqual(
            all_ratings_posts[5]["Time"],
            "2:30a"
        )

        self.assertEqual(
            12,
            len(all_ratings_posts)
        )


    def test_get_oath_token(self):
        """Integration test for the oath token 
            Ensures it is returned from reddit api

            Parameters
            ----------

            Returns
            -------

            Raises
            ------
        """

        from ratings.repo.ratings_repo_backend import get_oauth_token
        from scripts.reddit_ratings import get_client_secrets
        reddit_client_key, reddit_client_secret = get_client_secrets()

        oauth_token = get_oauth_token(
            client_key=reddit_client_key,
            client_secret=reddit_client_secret
        )
        self.assertIsNotNone(oauth_token["access_token"])







class LambdaHandler(unittest.TestCase):
    """Tests specific to when the script is run from a lambda
        function

        Parameters
        ----------

        Returns
        -------

        Raises
        ------
    """
    @classmethod
    def setUpClass(cls):
        """Unitest function that is run once for the class

            Parameters
            ----------

            Returns
            -------

            Raises
            ------
        """
        os.environ["AWS_LAMBDA_FUNCTION_NAME"] = "dev"
        '''
            Assigns a class attribute which is 
            a dict that represents news posts
        '''
        with open("util/lambda_cw_event.json", "r") as news_flair:
            cls.lambda_event_fixture = json.load(news_flair)

    @patch("logging.getLogger")
    @patch("scripts.reddit_ratings.main")
    def test_lambda_handler_event(self, main_mock, 
        getLogger_mock):
        """Tests passing sample event to lambda_handler

            Parameters
            ----------
            main_mock : unittest.mock.MagicMock
                Mock object used to patch the main function

            getLogger_mock : unittest.mock.MagicMock
                Mock object used to patch get_logger for lambda handler

            Returns
            -------

            Raises
            ------
        """
        from scripts.reddit_ratings import lambda_handler

        lambda_handler(
            event=self.lambda_event_fixture,
            context={}
        )

        self.assertEqual(
            getLogger_mock.call_count,
            1
        )

        '''
            Testing call count and args passed
        '''
        self.assertEqual(
            main_mock.call_count,
            1
        )


if __name__ == "__main__":
    unittest.main()
