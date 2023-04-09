import unittest

class TestRatingsRepoBackend(unittest.TestCase):
    def test_ratings_from_internet(self):
        """Parsing of TelevisionRatings entities"""
        from ratings.entities.entity_model import TelevisionRating
        from ratings.repo.ratings_repo_backend import ratings_from_internet
        

        television_ratings, unexpected_error = ratings_from_internet()


        for television_rating in television_ratings:
            self.assertIsInstance(
                television_rating, TelevisionRating
            )
        self.assertIsNone(unexpected_error)