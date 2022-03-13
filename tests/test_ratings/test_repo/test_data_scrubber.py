import unittest

class TestDataScrubber(unittest.TestCase):

    def test_data_scrubber(self):
        """determine if needed"""
        from fixtures.get_all_ratings_list import ratings_fixture_bad_data
        print(ratings_fixture_bad_data()[0:2])
