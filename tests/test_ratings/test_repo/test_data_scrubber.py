from unittest.mock import MagicMock, patch
import unittest

from fixtures.get_all_ratings_list import ratings_fixture_2022_07_23


class TestDataScrubber(unittest.TestCase):

    @patch("ratings.repo.data_scrubber._manual_override_by_date")
    @patch("ratings.repo.data_scrubber._remove_missing_time")
    @patch("ratings.repo.data_scrubber._override_ratings_occurred_on")
    @patch("ratings.repo.data_scrubber._manual_skip_date")
    def test_data_override_factory(self, manual_skip_date_mock: MagicMock, 
        override_ratings_occurred_on_mock: MagicMock, 
        remove_missing_time_mock: MagicMock,
        manual_override_by_date_mock: MagicMock):
        """Tests outgoing private cleaning scrubbers call args"""
        from fixtures.get_all_ratings_list import ratings_fixture_bad_data
        from ratings.repo.data_scrubber import data_override_factory


        data_override_factory(all_ratings_list=ratings_fixture_bad_data()[0:2])


        manual_skip_date_mock.assert_not_called(
        )

        override_ratings_occurred_on_mock.assert_called_once_with(
            date_to_override="2022-02-15",
            correct_ratings_date="2022-02-12",
            all_ratings_list=ratings_fixture_bad_data()[0:2]
        )

        remove_missing_time_mock.assert_called_once_with(
            all_ratings_list=ratings_fixture_bad_data()[0:2]
        )

        manual_override_by_date_mock.assert_called()


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


    def test_manual_override_by_date_of_night(self):
        """2022-07-23 incorrectly had two premiere times of 12:00am"""
        from fixtures.get_all_ratings_list import ratings_fixture_bad_data
        from ratings.repo.data_scrubber import _manual_override_by_date

        mock_ratings_list = ratings_fixture_2022_07_23()
        date_in_need_of_override = "2022-07-23"


        _manual_override_by_date(
            date_to_override=date_in_need_of_override,
            all_ratings_list=mock_ratings_list
        )


        clean_ratings_distinct_times = []
        original_ratings_clean_times = []

        for mock_clean_ratings, mock_original_ratings in zip(
            mock_ratings_list, ratings_fixture_2022_07_23()):
            if (mock_clean_ratings["RATINGS_OCCURRED_ON"] 
                == date_in_need_of_override):
                clean_ratings_distinct_times.append(
                    mock_clean_ratings["TIME"]
                )
            if (mock_original_ratings["RATINGS_OCCURRED_ON"] 
                == date_in_need_of_override):
                original_ratings_clean_times.append(
                    mock_original_ratings["TIME"]
                )

        self.assertEqual(len(mock_ratings_list), 
        len(ratings_fixture_2022_07_23()))

        self.assertEqual(
            len(set(clean_ratings_distinct_times)), 
            len(set(original_ratings_clean_times)) + 1
        )
