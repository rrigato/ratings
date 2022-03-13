from unittest.mock import patch
import unittest

class TestDataScrubber(unittest.TestCase):

    @patch("ratings.repo.data_scrubber._remove_missing_time")
    @patch("ratings.repo.data_scrubber._override_ratings_occurred_on")
    @patch("ratings.repo.data_scrubber._manual_skip_date")
    def test_data_override_factory(self, manual_skip_date_mock, 
        override_ratings_occurred_on_mock, remove_missing_time_mock):
        """Tests outgoing private cleaning scrubbers call args"""
        from fixtures.get_all_ratings_list import ratings_fixture_bad_data
        from ratings.repo.data_scrubber import data_override_factory


        data_override_factory(all_ratings_list=ratings_fixture_bad_data()[0:2])


        manual_skip_date_mock.assert_called_once_with(
            ratings_date_to_skip="2022-01-29",
            all_ratings_list=ratings_fixture_bad_data()[0:2]
        )

        override_ratings_occurred_on_mock.assert_called_once_with(
            date_to_override="2022-02-15",
            correct_ratings_date="2022-02-12",
            all_ratings_list=ratings_fixture_bad_data()[0:2]
        )

        remove_missing_time_mock.assert_called_once_with(
            all_ratings_list=ratings_fixture_bad_data()[0:2]
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


    def test_override_ratings_occurred_on(self):
        """2022-02-12 was incorrectly labeled as 2022-02-15"""
        from fixtures.get_all_ratings_list import ratings_fixture_bad_data
        from ratings.repo.data_scrubber import _override_ratings_occurred_on

        mock_ratings_list = ratings_fixture_bad_data()
        mock_correct_date = "2022-02-12"
        mock_incorrect_date = "2022-02-15"


        _override_ratings_occurred_on(
            date_to_override=mock_incorrect_date,
            correct_ratings_date=mock_correct_date,
            all_ratings_list=mock_ratings_list
        )


        count_of_correct_date = 0
        count_of_incorrect_date = 0
        for mock_rating in mock_ratings_list:
            if mock_rating["RATINGS_OCCURRED_ON"] == mock_incorrect_date:
                count_of_incorrect_date += 1

            if mock_rating["RATINGS_OCCURRED_ON"] == mock_correct_date:
                count_of_correct_date += 1

        self.assertEqual(count_of_incorrect_date, 0)
        self.assertEqual(count_of_correct_date, 8)




    def test_remove_missing_time(self):
        """Prod ratings data had an element with a TIME value of '' """
        from fixtures.get_all_ratings_list import ratings_fixture_bad_data
        from ratings.repo.data_scrubber import _remove_missing_time

        mock_ratings_list = ratings_fixture_bad_data()


        _remove_missing_time(
            all_ratings_list=mock_ratings_list
        )


        self.assertEqual(
            len(mock_ratings_list), 
            len(ratings_fixture_bad_data()) - 1
        )

