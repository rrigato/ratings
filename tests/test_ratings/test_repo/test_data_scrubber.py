from unittest.mock import patch
import unittest

class TestDataScrubber(unittest.TestCase):

    @patch("ratings.repo.data_scrubber._manual_skip_date")
    def test_data_override_factory(self, manual_skip_date_mock):
        """Factory function invoke correct private cleaning scrubbers"""
        from fixtures.get_all_ratings_list import ratings_fixture_bad_data

        from ratings.repo.data_scrubber import data_override_factory


        data_override_factory(all_ratings_list=ratings_fixture_bad_data())


        manual_skip_date_mock.assert_called_once_with(
            ratings_date_to_skip="2022-01-29",
            all_ratings_list=ratings_fixture_bad_data()
        )




    def test_manual_skip_date(self):
        """17 matching ratings elements removed"""
        from fixtures.get_all_ratings_list import ratings_fixture_bad_data

        from ratings.repo.data_scrubber import _manual_skip_date

        mock_ratings_list = ratings_fixture_bad_data()


        _manual_skip_date(
            ratings_date_to_skip="2022-01-29",
            all_ratings_list=mock_ratings_list
        )


        self.assertEqual(
            len(mock_ratings_list), 
            len(ratings_fixture_bad_data()) - 17
        )

