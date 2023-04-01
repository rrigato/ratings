import unittest

class TestNameMapper(unittest.TestCase):
    def test_get_table_column_name_mapping(self):
        """Each column name mapping value for a ratings post is a str"""
        from ratings.repo.name_mapper import get_table_column_name_mapping
        
        self.assertGreater(
            len(get_table_column_name_mapping().keys()),
            10
        )
        for column_name in get_table_column_name_mapping().keys():
            self.assertEqual(
                type(get_table_column_name_mapping()[column_name]),
                str
            )


    def test_get_table_column_name_mapping_viewers_e2e(self):
        """Bug where viewers key was not mapped"""
        from ratings.repo.name_mapper import get_table_column_name_mapping

        self.assertEqual(
            type(get_table_column_name_mapping()["viewers"]),
            str
        )      


    def test_get_table_column_name_mapping_18_49(self):
        """Bug where 18-49 key was not mapped"""
        from ratings.repo.name_mapper import get_table_column_name_mapping

        self.assertEqual(
            type(get_table_column_name_mapping()["18-49"]),
            str
        )    


    def test_get_table_column_name_mapping_timeslot(self):
        """Bug where timeslot is not mapped"""
        from ratings.repo.name_mapper import get_table_column_name_mapping

        self.assertEqual(
            type(get_table_column_name_mapping()["timeslot"]),
            str
        )    


    def test_get_table_column_name_mapping_rating(self):
        """Bug where rating is not mapped"""
        from ratings.repo.name_mapper import get_table_column_name_mapping

        self.assertEqual(
            type(get_table_column_name_mapping()["rating"]),
            str
        )    

